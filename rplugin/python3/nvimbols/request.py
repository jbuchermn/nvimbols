from abc import abstractmethod
import time

from nvimbols.util import log
from nvimbols.loadable_state import LoadableState


class Request:
    def __init__(self, graph, requested_state):
        self.graph = graph
        self.requested_state = requested_state
        self._source = None

        """
        Number of times, request raised an Exception
        """
        self._error_count = 0

        """
        Number of times, request did not fulfill
        """
        self._idle_count = 0

    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def fulfill(self):
        pass

    def __str__(self):
        return "Request"

    def set_source(self, source):
        self._source = source

    def run(self):
        error = None

        if self.state() < self.requested_state:
            log(self)
            result = False

            try:
                result = self._source.request(self)
            except Exception as err:
                error = err

            if result:
                self.fulfill()

        if self.state() >= self.requested_state:
            return False

        if error is not None:
            self._error_count += 1
        else:
            self._idle_count += 1

        if self._error_count > 3:
            log("Error in source.request: %s" % error)
            log(self)
            return False

        if self._idle_count > 5:
            log("Warning! Idle for: %d" % self._idle_count)

        """
        TODO! Not nice handling of idle as it blocks...
        Need better JobQueue
        """
        time.sleep(1.)

        """
        If the source fails to fulfill and does not raise an
        Exception, assume it is idle and keep on retrying.
        """
        return True


class LoadSymbolRequest(Request):
    def __init__(self, graph, requested_state, location):
        super().__init__(graph, requested_state)
        self.location = location

    def state(self):
        if self.graph.is_empty(self.location):
            return LoadableState.FULL

        symbol = self.graph.symbol(self.location)
        if symbol is None:
            return LoadableState.NOT_LOADED
        else:
            return symbol.state()

    def fulfill(self):
        symbol = self.graph.symbol(self.location)
        if symbol is not None:
            symbol.fulfill(self.requested_state)

    def __str__(self):
        return "Load Symbol at %s to state %s" % (self.location, self.requested_state)


class LoadReferencesRequest(Request):
    def __init__(self, graph, requested_state, symbol, reference_class, source_of):
        super().__init__(graph, requested_state)
        self.symbol = symbol
        self.reference_class = reference_class
        self.source_of = source_of

    def state(self):
        if self.source_of:
            return self.symbol.state_source_of(self.reference_class)
        else:
            return self.symbol.state_target_of(self.reference_class)

    def fulfill(self):
        if self.source_of:
            self.symbol.fulfill_source_of(self.reference_class, self.requested_state)
        else:
            self.symbol.fulfill_target_of(self.reference_class, self.requested_state)

    def __str__(self):
        return "Load References %s (%s) at %s to state %s" % (self.reference_class,
                                                              "Targets" if self.source_of else "Sources",
                                                              self.symbol.location,
                                                              self.requested_state)


class LoadSubGraphFileRequest(Request):
    def __init__(self, graph, sub_graph, requested_state):
        super().__init__(graph, requested_state)
        self.sub_graph = sub_graph

    def state(self):
        return self.sub_graph.state()

    def fulfill(self):
        self.sub_graph.fulfill(self.requested_state)

    def __str__(self):
        return "Load Sub Graph in %s" % self.sub_graph.filename



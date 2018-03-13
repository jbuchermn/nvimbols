from nvimbols.observable import Observable
from nvimbols.job_queue import JobQueue
from nvimbols.request import LoadSymbolRequest
from nvimbols.symbol import LoadableState
from nvimbols.base_graph import BaseGraph
from nvimbols.sub_graph_file import SubGraphFile


class Graph(Observable, BaseGraph):
    def __init__(self, source, parent):
        Observable.__init__(self)
        BaseGraph.__init__(self)

        self._source = source
        self._parent = parent

        self._queue = JobQueue(self._source.tasks)

        """
        Pass notifications from job_queue through
        """
        self._queue.on_update(lambda: self._notify())

        """
        List of Symbols
        """
        self._symbols = []

        """
        List of Locations
        """
        self._empty = []

        """
        List of SubGraphFile
        """
        self._files = []

    """
    BaseGraph functionality
    """

    def nodes(self):
        return self._symbols

    def edge_classes(self):
        return self._source.references

    def source_of(self, node, edge_class):
        if node not in self._symbols:
            raise Exception("Invalid request")

        return [n._to for n in node._get_source_of(edge_class)]

    def target_of(self, node, edge_class):
        if node not in self._symbols:
            raise Exception("Invalid request")

        return [n._from for n in node._get_target_of(edge_class)]

    """
    Queue functionality
    """

    def on_request(self, request):
        self._queue.job(lambda: self._on_request(request))

    def cancel(self):
        self._queue.cancel()

    def _on_request(self, request):
        if self._source.request(request):
            request.fulfill()

    """
    Object creation and access
    """

    def symbol(self, location, symbol_class=None):
        for s in self._symbols:
            if s.location.contains(location):
                return s

        if symbol_class is not None:
            symbol = symbol_class(self, location)
            self._symbols += [symbol]
            return symbol

        return None

    def empty(self, location):
        self._empty += [location]

    def is_empty(self, location):
        for loc in self._empty:
            if loc.contains(location):
                return True

        return False

    def sub_graph_file(self, filename):
        for s in self._files:
            if s.filename == filename:
                return s

        sub_graph_file = SubGraphFile(self, filename)
        self._files += [sub_graph_file]
        return sub_graph_file

    """
    Interface to NVimbols
    """

    def clear(self):
        self._queue.cancel()
        self._symbols = []
        self._empty = []
        self._files = []

    def request_at(self, location):
        if self.is_empty(location):
            return

        symbol = self.symbol(location)
        if symbol is not None:
            if symbol.state() == LoadableState.FULL:
                return

        self.on_request(LoadSymbolRequest(self, LoadableState.FULL, location))

    def request_file(self, filename):
        sub_graph = self.sub_graph_file(filename)
        sub_graph.request(LoadableState.FULL)



















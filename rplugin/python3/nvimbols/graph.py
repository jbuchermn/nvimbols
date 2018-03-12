from nvimbols.observable import Observable
from nvimbols.job_queue import JobQueue
from nvimbols.symbol import Symbol
from nvimbols.request import LoadSymbolRequest
from nvimbols.symbol import LoadableState
from nvimbols.sub_graph_file import SubGraphFile


class Graph(Observable):
    def __init__(self, source, parent):
        super().__init__()

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

    def symbols(self):
        return self._symbols

    def cancel(self):
        self._queue.cancel()

    def on_request(self, request):
        self._queue.job(lambda: self._on_request(request))

    def _on_request(self, request):
        if self._source.request(request):
            request.fulfill()

    def symbol(self, location, symbol_class=None):
        for s in self._symbols:
            if s.location.contains(location):
                return s

        if symbol_class is not None:
            symbol = symbol_class(self, location)
            self._symbols += [symbol]
            return symbol

        return None

    def sub_graph_file(self, filename):
        for s in self._files:
            if s.filename == filename:
                return s

        sub_graph_file = SubGraphFile(self, filename)
        self._files += [sub_graph_file]
        return sub_graph_file

    def empty(self, location):
        self._empty += [location]

    def clear(self):
        self._queue.cancel()
        self._symbols = []
        self._empty = []

    def request(self, location):
        for loc in self._empty:
            if loc.contains(location):
                return

        symbol = self.symbol(location)
        if symbol is not None:
            if symbol.state() == LoadableState.FULL:
                return

        self.on_request(LoadSymbolRequest(self, LoadableState.FULL, location))

    def request_file(self, filename):
        sub_graph = self.sub_graph_file(filename)
        sub_graph.request(LoadableState.FULL)



















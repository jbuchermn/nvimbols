from nvimbols.observable import Observable
from nvimbols.job_queue import JobQueue
from nvimbols.symbol import Symbol
from nvimbols.request import LoadSymbolRequest
from nvimbols.symbol import LoadableState


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

    def cancel(self):
        self._queue.cancel()

    def on_request(self, request):
        self._queue.job(lambda: self._on_request(request))

    def _on_request(self, request):
        if self._source.request(request):
            request.fulfill()

    def symbol(self, location, symbol=None):
        for s in self._symbols:
            if s.location.contains(location):
                return s

        if symbol is not None:
            if not isinstance(symbol, Symbol):
                raise Exception("All symbols must inherit from Symbol")
            symbol._graph = self
            self._symbols += [symbol]

        return symbol

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

        if self.symbol(location) is not None:
            return

        self.on_request(LoadSymbolRequest(self, LoadableState.FULL, location))


















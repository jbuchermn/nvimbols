from nvimbols.symbol import SymbolLocation
from nvimbols.util import log, on_error, on_error_wrap
from nvimbols.loadable import Loadable
from nvimbols.observable import Observable
from nvimbols.job_queue import JobQueue
import time


class _SymbolWrapper:
    def __init__(self, graph, location):
        self.location = location

        self.symbol = Loadable(graph, {'type': 'symbol', 'wrapper': self})
        self.target_of = {ref.name: Loadable(graph, {'type': 'target', 'reference': ref, 'wrapper': self}) for ref in graph.references}
        self.source_of = {ref.name: Loadable(graph, {'type': 'source', 'reference': ref, 'wrapper': self}) for ref in graph.references}


class SymbolsGraph(Observable):
    def __init__(self, source, parent):
        super().__init__()

        self.references = source.references
        self._source = source
        self._parent = parent

        self._queue = JobQueue(self._source.tasks)

        """
        Pass notifications from job_queue through
        """
        self._queue.on_update(lambda: self._notify())

        """
        List of _SymbolWrapper
        """
        self._data = []

    def cancel(self):
        self._queue.cancel()

    def on_request(self, loadable, params):
        self._queue.job(lambda: self._on_request(loadable, params))

    def _on_request(self, loadable, params):
        if params['type'] == 'symbol':
            self._source.load_symbol(params)
        elif params['type'] == 'target':
            self._source.load_target_of(params)
        elif params['type'] == 'source':
            self._source.load_source_of(params)


    def create_wrapper(self, location):
        for w in self._data:
            if w.location.contains(location) or location.contains(w.location):
                return w

        location = SymbolLocation(location.filename, location.start_line, location.start_col, location.end_line, location.end_col)
        wrapper = _SymbolWrapper(self, location)

        self._data += [wrapper]
        return wrapper

    def get(self, location):
        for wrapper in self._data:
            if(wrapper.location.contains(location)):
                return wrapper

        return None

    def clear(self):
        self._queue.cancel()
        self._data = []

    def require_at_location(self, location):
        wrapper = self.get(location)
        if(wrapper is None):
            wrapper = self.create_wrapper(location)

        wrapper.symbol.request()


















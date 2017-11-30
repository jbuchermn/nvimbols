from nvimbols.symbol import SymbolLocation
from nvimbols.util import log, on_error, on_error_wrap
from nvimbols.loadable import Loadable
from nvimbols.job_queue import JobQueue
import time


class _SymbolWrapper:
    def __init__(self, graph, location):
        self.location = location

        self.symbol = Loadable(graph, {'type': 'symbol', 'wrapper': self})
        self.target_of = {ref.name: Loadable(graph, {'type': 'target', 'reference': ref, 'wrapper': self}) for ref in graph.references}
        self.source_of = {ref.name: Loadable(graph, {'type': 'source', 'reference': ref, 'wrapper': self}) for ref in graph.references}


class SymbolsGraph:
    def __init__(self, source, parent):
        self.references = source.references
        self._source = source
        self._parent = parent

        self._queue = JobQueue(self._source.tasks)

        """
        Functions to be called when graph changes. Not guaranteed to be called after
        every atomic changes, might also happen after a batch of requests has been handled
        """
        self._observers = []

        """
        List of _SymbolWrapper
        """
        self._data = []

    def on_update(self, func):
        self._observers += [func]

    def on_request(self, loadable, params):
        self._queue.job(lambda: self._on_request(loadable, params))

    def _notify(self):
        for f in self._observers:
            try:
                f()
            except Exception as err:
                on_error(None, err)

    def _on_request(self, loadable, params):
        if params['type'] == 'symbol':
            self._source.load_symbol(params)
        elif params['type'] == 'target':
            self._source.load_target_of(params)
        elif params['type'] == 'source':
            self._source.load_source_of(params)

        """
        Could be called from the JobQueue, i. e. after abunch of jobs are completed to prevent constant rerendering
        """
        self._notify()

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
        log("CLEAR")
        self._data = []

    def require_at_location(self, location):
        wrapper = self.get(location)
        if(wrapper is None):
            wrapper = self.create_wrapper(location)

        wrapper.symbol.request()


















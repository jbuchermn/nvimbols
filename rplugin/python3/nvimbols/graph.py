import os

from nvimbols.util import log
from nvimbols.symbol import SymbolLocation, SymbolLocationFile, Symbol
from nvimbols.loadable import Loadable, LOADABLE_FULL
from nvimbols.observable import Observable
from nvimbols.job_queue import JobQueue

SYMBOL = 'symbol'
SYMBOL_FILE = 'file'

"""
TODO! Sadly Python is not able to handle circular imports; find a better way.
"""
from nvimbols.reference import ParentRef


class _SymbolWrapper:
    def __init__(self, graph, location):
        self.location = location
        self.type = SYMBOL_FILE if isinstance(location, SymbolLocationFile) else SYMBOL

        self.symbol = Loadable(graph, {'type': 'symbol', 'wrapper': self})
        self.target_of = {ref.name: Loadable(graph, {'type': 'target', 'reference': ref, 'wrapper': self}) for ref in graph.references}
        self.source_of = {ref.name: Loadable(graph, {'type': 'source', 'reference': ref, 'wrapper': self}) for ref in graph.references}

        if self.type == SYMBOL_FILE:
            self.symbol.set(Symbol(os.path.basename(location.filename), "file"))
            """
            This symbol can only exist as target of ParentRef
            """
            for ref in graph.references:
                self.source_of[ref.name].set([], LOADABLE_FULL)
                if(ref != ParentRef):
                    self.target_of[ref.name].set([], LOADABLE_FULL)

    def request(self, level=LOADABLE_FULL):
        self.symbol.request(level)
        for ref in self.source_of:
            self.source_of[ref].request(level)
        for ref in self.target_of:
            self.target_of[ref].request(level)


class SymbolsGraph(Observable):
    def __init__(self, source, parent):
        super().__init__()

        self.references = source.references
        self._source = source
        self._parent = parent

        self._queue = JobQueue(self._source.tasks)

        self._queue.on_update(lambda: self._on_update())

        """
        List of _SymbolWrapper
        """
        self._data = []

    def _on_update(self):
        for ref in self.references:
            ref.validate(self)

        self._notify()

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
        elif params['type'] == 'file':
            self._source.load_symbols_in_file(params)

        """
        Reissue load if not successful
        """
        if(not loadable.is_loaded(params['requested_level'])):
            self._on_request(loadable, params)

    def create_wrapper(self, location):
        for w in self._data:
            if w.location.contains(location) or location.contains(w.location):
                return w

        location = SymbolLocation(location.filename, location.start_line, location.start_col, location.end_line, location.end_col) if not isinstance(location, SymbolLocationFile) else SymbolLocationFile(location.filename)
        wrapper = _SymbolWrapper(self, location)

        self._data += [wrapper]
        return wrapper

    def get(self, location):
        for wrapper in self._data:
            if(wrapper.location.contains(location)):
                return wrapper

        return self.create_wrapper(location)

    def get_all(self):
        return self._data

    def clear(self):
        self._queue.cancel()
        self._data = []




















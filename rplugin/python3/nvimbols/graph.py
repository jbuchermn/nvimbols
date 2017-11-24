from nvimbols.symbol import SymbolLocation
from nvimbols.util import log, on_error_wrap
from threading import Lock, Thread


class SymbolsGraph:
    def __init__(self, source, parent):
        self.references = source.references
        self._source = source
        self._parent = parent

        self._lock = Lock()
        self._locations = []

    def get_location(self, location):
        for loc in self._locations:
            if(loc.contains(location)):
                return loc

        return None

    def clear(self):
        self._locations = []

    def require_symbol(self, location):
        for loc in self._locations:
            if(loc.contains(location)):
                return

        location = SymbolLocation(location.filename, location.start_line, location.start_col, location.end_line, location.end_col)
        self._locations += [location]
        Thread(target=on_error_wrap(None, lambda: self._require_symbol(location))).start()

    def _require_symbol(self, location):
        if not (not location.symbol.is_loading() and location.symbol.data_set()):
            self._source.load_symbol(location)
            self._parent.render()

        symbol = location.symbol.get()
        if symbol is not None:
            for r in self.references:
                if not symbol.target_of_set(r):
                    self._source.load_target_of(symbol, r)
                    for i in range(len(symbol.get_target_of(r))):
                        loc = self.get_location(symbol.get_target_of(r)[i])
                        if loc is not None:
                            symbol.get_target_of(r)[i] = loc

                if not symbol.source_of_set(r):
                    self._source.load_source_of(symbol, r)
                    for i in range(len(symbol.get_source_of(r))):
                        loc = self.get_location(symbol.get_source_of(r)[i])
                        if loc is not None:
                            symbol.get_source_of(r)[i] = loc

            self._parent.render()

    def log_summary(self):
        for loc in self._locations:
            log("%s: %s" % (loc, loc.symbol.get().name if loc.symbol.get() is not None else "None"))


















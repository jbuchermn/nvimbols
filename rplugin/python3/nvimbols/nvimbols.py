import os
from threading import Thread, Lock

from nvimbols.util import log, on_error
from nvimbols.symbol import SymbolLocation


class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source

        self._current_symbol = None

        self._lock = Lock()
        self._location_queue = None

    def _update_location(self):
        if(self._location_queue is None):
            return

        repeat = False

        if self._lock.acquire(False):
            try:
                # Backup location to check if it is still valid after the call
                location = SymbolLocation(self._location_queue._filename, self._location_queue._start_line, self._location_queue._start_col)

                # Possibly expensive call, during which _location_queue may change
                log("[UPDATE_LOCATION] Getting symbol")
                symbol = self._source.symbol_at_location(location)

                if(self._location_queue == location):
                    self._location_queue = None

                    if(self._current_symbol != symbol):
                        self._current_symbol = symbol
                        self._vim.session.threadsafe_call(lambda: self._vim.call("nvimbols#update_symbol"))
                else:
                    repeat = True
            except Exception as err:
                on_error(err)
            finally:
                self._lock.release()

            if(repeat):
                self._update_location()

    def update_location(self, location):
        self._location_queue = location
        Thread(target=NVimbols._update_location, args=(self,)).start()

    def render(self, buf):
        content = ""

        if self._current_symbol is None:
            content += "No symbol\nOther useful information to be\n   displayed here in the future"
        else:
            content += "Symbol: {{{{Statement}}}}%s{{{{/Statement}}}}\nKind: %s\n" % (self._current_symbol._name, self._current_symbol._kind)

            if(len(self._current_symbol._references) > 0):
                content += "\n{{{{Title}}}}-----Targets-----{{{{/Title}}}}\n"
                for symbol in self._current_symbol._references:
                    content += "  {{{{Statement}}}}%s{{{{/Statement}}}}\n    %s %s" % (symbol._name, symbol._kind, os.path.basename(symbol._location._filename))

            if(len(self._current_symbol._referenced_by) > 0):
                content += "\n{{{{Title}}}}-----Usages-----{{{{/Title}}}}\n"
                for symbol in self._current_symbol._referenced_by:
                    content += "  {{{{Statement}}}}%s{{{{/Statement}}}}\n    %s %s" % (symbol._name, symbol._kind, os.path.basename(symbol._location._filename))

        buf[:] = content.split("\n")

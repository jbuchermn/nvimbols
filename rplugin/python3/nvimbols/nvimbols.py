import os
from threading import Thread, Lock

from nvimbols.util import log, on_error
from nvimbols.symbol import SymbolLocation
from nvimbols.content import Content, Wrapper, Highlight, Link

class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source

        self._current_symbol = None
        self._current_content = None

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
                        self._current_content = self._render()
                        self._vim.session.threadsafe_call(lambda: self._vim.call("nvimbols#update_symbol"))
                else:
                    repeat = True
            except Exception as err:
                on_error(self._vim, err)
            finally:
                self._lock.release()

            if(repeat):
                self._update_location()

    def update_location(self, location):
        self._location_queue = location
        Thread(target=NVimbols._update_location, args=(self,)).start()

    def _render(self):
        content = Content()

        if self._current_symbol is None:
            content += "No symbol\nOther useful information to be\n   displayed here in the future"
        else:
            content += Wrapper("Symbol: ", Highlight('Statement', self._current_symbol._name), "\nKind: ", Highlight('Statement', self._current_symbol._kind))

            if(len(self._current_symbol._references) > 0):
                content += Wrapper("\n", Highlight('Title', "-----Targets-----"), "\n")
                for symbol in self._current_symbol._references:
                    content += Link(symbol._location,
                                    Wrapper(Highlight('Statement', symbol._name), "\n    ", Highlight('Statement', symbol._kind), " ", os.path.basename(symbol._location._filename), "\n"))

            if(len(self._current_symbol._referenced_by) > 0):
                content += Wrapper("\n", Highlight('Title', "-----Usages-----"), "\n")
                for symbol in self._current_symbol._referenced_by:
                    content += Link(symbol._location,
                                    Wrapper(Highlight('Statement', symbol._name), "\n    ", Highlight('Statement', symbol._kind), " ", os.path.basename(symbol._location._filename), "\n"))

        return content

    def render(self, buf):
        if(self._current_content is None):
            return

        buf.api.set_option('modifiable', True)

        buf[:] = self._current_content.raw()
        for highlight in self._current_content.highlights():
            buf.add_highlight(highlight.name, highlight.line - 1, highlight.start_col - 1, highlight.end_col - 1, -1)

        buf.api.set_option('modifiable', False)

    def get_link(self, line, col):
        if(self._current_content is None):
            return ""

        for link in self._current_content.links():
            if(link.line == line and link.start_col <= col and (link.end_col == -1 or link.end_col >= col)):
                return str(link.target)

        return ""







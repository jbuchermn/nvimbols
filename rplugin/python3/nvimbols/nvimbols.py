import os
from threading import Lock

from nvimbols.util import log, on_error
from nvimbols.symbol import SymbolLocation
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.async import JobQueue


class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source

        self._current_symbol = None
        self._current_content = None

        self._lock = Lock()
        self._job_queue = JobQueue()

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
                    content += Link(symbol._location, Wrapper(Highlight('Type', os.path.basename(symbol._location._filename)), ":", symbol._location._start_line, "\n"))

        return content

    def _update_symbol(self, symbol):
        """
        Will be called by the JobQueue, i. e. in a new thread.
        """
        with self._lock:
            if(self._current_symbol != symbol):
                self._current_symbol = symbol
                self._current_content = self._render()
                self._vim.session.threadsafe_call(lambda: self._vim.call("nvimbols#update_symbol"))

    def update_location(self, location):
        with self._lock:
            self._job_queue.add_job(
                lambda: self._source.symbol_at_location(location),
                lambda symbol, err: self._update_symbol(symbol) if err is None else on_error(self._vim, err)
            )

    def render(self, buf):
        self._job_queue.join()
        with self._lock:
            if(self._current_content is None):
                return

            buf.api.set_option('modifiable', True)

            buf[:] = self._current_content.raw()
            for highlight in self._current_content.highlights():
                buf.add_highlight(highlight.name, highlight.line - 1, highlight.start_col - 1, highlight.end_col - 1, -1)

            buf.api.set_option('modifiable', False)

    def get_link(self, line, col):
        self._job_queue.join()
        with self._lock:
            if(self._current_content is None):
                return ""

            for link in self._current_content.links():
                if(link.line == line and link.start_col <= col and (link.end_col == -1 or link.end_col >= col)):
                    return str(link.target)

            return ""

    def get_link_to_first_reference(self):
        self._job_queue.join()
        with self._lock: 
            if(self._current_symbol is None):
                return ""
            
            if(len(self._current_symbol._references) == 0):
                return ""

            return str(self._current_symbol._references[0]._location)






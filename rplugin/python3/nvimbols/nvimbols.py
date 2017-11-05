import os

from nvimbols.symbol import SymbolLocation


class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source

        self._current_symbol = None

    def update_current_symbol(self, symbol):
        if(self._current_symbol != symbol):
            self._current_symbol = symbol
            if(self._current_symbol is None):
                self._vim.call("nvimbols#no_symbol")
            else:
                self._vim.call("nvimbols#update_symbol", self._current_symbol.to_dict())

    def update_location(self, filename, line, col):
        location = SymbolLocation(filename, line, col)
        if(self._current_symbol is None or (not self._current_symbol._location.contains(location))):
            self.update_current_symbol(self._source.symbol_at_location(location))

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

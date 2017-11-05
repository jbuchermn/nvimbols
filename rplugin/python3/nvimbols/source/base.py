from abc import abstractmethod


class Base:
    def __init__(self, vim):
        self._vim = vim

    @abstractmethod
    def supported_filetypes(self):
        pass

    @abstractmethod
    def symbol_at_location(self, filename, line, col):
        pass

from abc import abstractmethod


class Base:
    def __init__(self, vim):
        self._vim = vim
        self.name = None
        self.filetypes = []

    @abstractmethod
    def symbol_at_location(self, filename, line, col):
        pass

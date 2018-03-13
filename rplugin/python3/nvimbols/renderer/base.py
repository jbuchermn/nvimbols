from abc import abstractmethod


class Base:
    def __init__(self, vim):
        self._vim = vim

        """
        Default configuration. Replace in YourRenderer.__init__
        """
        self.name = None
        self.filetypes = []
        self.modes = []

    @abstractmethod
    def render(self, graph, cursor_location, mode):
        pass

    @abstractmethod
    def render_denite(self, graph, cursor_location, mode):
        pass

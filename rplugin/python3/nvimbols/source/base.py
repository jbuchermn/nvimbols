from abc import abstractmethod
from nvimbols.reference import TargetReference, ParentReference, InheritanceReference


class Base:
    def __init__(self, vim):
        self._vim = vim

        """
        Default configuration. Replace in YourSource.__init__
        """
        self.name = None
        self.filetypes = []
        self.references = [TargetReference, ParentReference, InheritanceReference]
        self.tasks = 4  # Set tasks=1 for non-threadsafe sources

    @abstractmethod
    def request(self, req):
        pass

    def on_file_invalidate(self, filename, new_text):
        pass


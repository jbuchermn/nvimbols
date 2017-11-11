from abc import abstractmethod
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef


class Base:
    def __init__(self, vim):
        self._vim = vim
        self.name = None
        self.filetypes = []
        self.references = [TargetRef, ParentRef, InheritanceRef]

    @abstractmethod
    def symbol_at_location(self, location):
        pass

    @abstractmethod
    def load_source_of(self, symbol, reference):
        pass

    @abstractmethod
    def load_target_of(self, symbol, reference):
        pass

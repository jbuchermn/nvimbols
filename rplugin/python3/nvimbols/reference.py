class Reference:
    """
    Base class for all edges.
    Meant to be subclassed within the specific source.
    """
    def __init__(self):
        self._graph = None
        self._from = None
        self._to = None

        self.name = ""
        self.display_targets = ""
        self.display_sources = ""

    def __eq__(self, other):
        if not issubclass(type(other), Reference):
            return False
        if type(other) != type(self):
            return False
        if id(self._from) != id(other._from):
            return False
        if id(self._to) != id(other._to):
            return False

        return True

    def delete(self):
        if self._from is not None:
            self._from.delete_reference(self)

        if self._to is not None:
            self._to.delete_reference(self)


class TargetReference(Reference):
    def __init__(self):
        super().__init__()
        self.name = "references"
        self.display_targets = "Targets"
        self.display_sources = "Usages"


class ParentReference(Reference):
    def __init__(self):
        super().__init__()
        self.name = "is_child_of"
        self.display_targets = "Parents"
        self.display_sources = "Children"


class InheritanceReference(Reference):
    def __init__(self):
        super().__init__()
        self.name = "inherits_from"
        self.display_targets = "Supers"
        self.display_sources = "Subs"

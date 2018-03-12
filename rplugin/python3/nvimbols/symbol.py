from nvimbols.loadable_state import LoadableState
from nvimbols.reference import Reference
from nvimbols.request import LoadSymbolRequest, LoadReferencesRequest


class Symbol:
    """
    Base class for all nodes.
    Meant to be subclassed within the specific source.
    """
    def __init__(self, graph, location):
        self.location = location
        self.name = ""
        self.kind = ""

        self._graph = graph
        self._references = []

        self._state = LoadableState.NOT_LOADED
        self._state_source_of = {}
        self._state_target_of = {}

    def __str__(self):
        return "Symbol(%s): %s" % (self.name, self.kind)

    """
    Graph related functionality
    """

    def reference_to(self, reference, symbol):
        if id(self) == id(symbol):
            raise Exception("Circular reference")

        if symbol is None:
            raise Exception("Reference to None")

        if not isinstance(symbol, Symbol):
            raise Exception("All symbols must inherit from Symbol")

        if not isinstance(reference, Reference):
            raise Exception("All references must inherit from Reference")

        reference._graph = self._graph
        reference._from = self
        reference._to = symbol

        for r in self._references:
            if r == reference:
                return r

        self._references += [reference]
        symbol._references += [reference]

        return reference

    def reference_from(self, reference, symbol):
        if id(self) == (symbol):
            raise Exception("Circular reference")

        if symbol is None:
            raise Exception("Reference from None")

        if not isinstance(symbol, Symbol):
            raise Exception("All symbols must inherit from Symbol")

        if not isinstance(reference, Reference):
            raise Exception("All references must inherit from Reference")

        for r in self._references:
            if r == reference:
                return r

        self._references += [reference]
        symbol._references += [reference]
        reference._graph = self._graph
        reference._from = symbol
        reference._to = self

        return reference

    def delete_reference(self, reference):
        self._references.remove(reference)
        if id(reference._to) == id(self) and reference._from is not None:
            reference._from.delete_reference(reference)
        if id(reference._from) == id(self) and reference._to is not None:
            reference._to.delete_reference(reference)

    """
    Request related functionality
    """

    def state(self):
        return self._state

    def state_source_of(self, reference_class):
        if not str(reference_class) in self._state_source_of:
            self._state_source_of[str(reference_class)] = LoadableState.NOT_LOADED

        return self._state_source_of[str(reference_class)]

    def state_target_of(self, reference_class):
        if not str(reference_class) in self._state_target_of:
            self._state_target_of[str(reference_class)] = LoadableState.NOT_LOADED

        return self._state_target_of[str(reference_class)]

    def get_source_of(self, reference_class):
        return [r for r in self._references
                if type(r) == reference_class and id(r._from) == id(self)]

    def get_target_of(self, reference_class):
        return [r for r in self._references
                if type(r) == reference_class and id(r._to) == id(self)]

    def request(self, state=LoadableState.FULL):
        self._graph.on_request(LoadSymbolRequest(self._graph, state, self.location))

    def request_source_of(self, reference_class, state=LoadableState.FULL):
        self._graph.on_request(LoadReferencesRequest(self._graph, state, self, reference_class, True))

    def request_target_of(self, reference_class, state=LoadableState.FULL):
        self._graph.on_request(LoadReferencesRequest(self._graph, state, self, reference_class, False))

    def fulfill(self, state=LoadableState.FULL):
        self._state = state

    def fulfill_source_of(self, reference_class, state=LoadableState.FULL):
        self._state_source_of[str(reference_class)] = state

    def fulfill_target_of(self, reference_class, state=LoadableState.FULL):
        self._state_target_of[str(reference_class)] = state
















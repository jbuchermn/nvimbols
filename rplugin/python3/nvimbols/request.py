from abc import abstractmethod


class Request:
    def __init__(self, graph, state):
        """
        graph is instance of nvimbols.graph.Graph
        state is instance of nvimbols.symbol.LoadableState
        """
        self.graph = graph
        self.state = state

    @abstractmethod
    def fulfill(self):
        pass


class LoadSymbolRequest(Request):
    def __init__(self, graph, state, location):
        super().__init__(graph, state)
        self.location = location

    def fulfill(self):
        symbol = self.graph.symbol(self.location)
        if symbol is not None:
            symbol.fulfill(self.state)


class LoadReferencesRequest(Request):
    def __init__(self, graph, state, symbol, reference_class, source_of):
        super().__init__(graph, state)
        self.symbol = symbol
        self.reference_class = reference_class
        self.source_of = source_of

    def fulfill(self):
        if self.source_of:
            self.symbol.fulfill_source_of(self.reference_class, self.state)
        else:
            self.symbol.fulfill_target_of(self.reference_class, self.state)


"""
TODO
"""

class LoadAllSymbolsInFileRequest(Request):
    pass

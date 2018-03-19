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

    def __str__(self):
        return "Abstract Request"


class LoadSymbolRequest(Request):
    def __init__(self, graph, state, location):
        super().__init__(graph, state)
        self.location = location

    def fulfill(self):
        symbol = self.graph.symbol(self.location)
        if symbol is not None:
            symbol.fulfill(self.state)

    def __str__(self):
        return "Load Symbol at %s to state %s" % (self.location, self.state)


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

    def __str__(self):
        return "Load References %s (%s) at %s to state %s" % (self.reference_class,
                                                              "Targets" if self.source_of else "Sources",
                                                              self.symbol.location,
                                                              self.state)


class LoadSubGraphFileRequest(Request):
    def __init__(self, graph, sub_graph, state):
        super().__init__(graph, state)
        self.sub_graph = sub_graph

    def fulfill(self):
        self.sub_graph.fulfill(self.state)

    def __str__(self):
        return "Load Sub Graph in %s" % self.sub_graph.filename



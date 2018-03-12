from nvimbols.loadable_state import LoadableState
from nvimbols.sub_graph import SubGraph
from nvimbols.request import LoadSubGraphFileRequest


class SubGraphFile(SubGraph):
    def __init__(self, graph, filename):
        super().__init__(graph, lambda symbol: symbol.location.filename == filename)
        self.filename = filename
        self._state = LoadableState.NOT_LOADED

    def state(self):
        return self._state

    def request(self, state=LoadableState.FULL):
        self.graph.on_request(LoadSubGraphFileRequest(self, state))

    def fulfill(self, state=LoadableState.FULL):
        self._state = state

    def symbols(self):
        return [s for s in self.graph.symbols() if self.include(s)]


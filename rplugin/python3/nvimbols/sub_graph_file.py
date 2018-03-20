from nvimbols.loadable_state import LoadableState
from nvimbols.sub_graph import SubGraph
from nvimbols.request import LoadSubGraphFileRequest


class SubGraphFile(SubGraph):
    def __init__(self, graph, filename):
        super().__init__(graph, lambda symbol: symbol.location.filename == filename)
        self.filename = filename
        self._state = LoadableState.NOT_LOADED

    """
    Request related functionality
    """

    def state(self):
        return self._state

    def request(self, state=LoadableState.FULL):
        self._graph.add_request(LoadSubGraphFileRequest(self._graph, self, state))

    def fulfill(self, state=LoadableState.FULL):
        self._state = state

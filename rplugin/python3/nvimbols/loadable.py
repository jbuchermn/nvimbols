
class Loadable:
    def __init__(self, graph, params):
        self._graph = graph
        self._params = params
        self._data = None

        """
        States:
            INITIAL
            REQUESTED
            LOADED

        INITIAL
            -> request()         => REQUESTED
            -> set()             => LOADED

        REQUESTED
            -> set()             => LOADED
        """
        self._state = 'initial'

    def get(self):
        return self._data

    def is_loading(self):
        return self._state == 'requested'

    def is_loaded(self):
        return self._state == 'loaded'

    def request(self):
        if(self._state == 'initial'):
            self._state = 'requested'
            self._graph.on_request(self, self._params)

    def set(self, data):
        self._data = data
        self._state = 'loaded'


class LoadableList(Loadable):
    def __init__(self, graph, params):
        super().__init__(graph, params)
        self._incomplete = False

    def set(self, data, incomplete=False):
        self._incomplete = incomplete
        super().set(data)

    def is_incomplete(self):
        return self._incomplete

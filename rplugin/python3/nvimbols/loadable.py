LOADABLE_PREVIEW = 'preview'
LOADABLE_FULL = 'full'

class Loadable:
    def __init__(self, graph, params):
        self._graph = graph
        self._data = None
        self._params = params
        self._params['requested_level'] = None
        self._loaded_level = None

        """
        levels[i] includes levels[i-1]
        """
        self.levels = [LOADABLE_PREVIEW, LOADABLE_FULL]

        self._state = 'initial'
        self._request_again_when_done = None

    def _compare_levels(self, level1, level2):
        i1 = self.levels.index(level1) if level1 is not None else -1
        i2 = self.levels.index(level2) if level2 is not None else -1

        return i1 - i2

    def get(self):
        return self._data

    def is_loading(self):
        return self._state == 'requested'

    def is_loaded(self, level=None):
        if level is None:
            level = self.levels[0]

        """
        Might be true, even though _state == 'requested'
        """
        return self._compare_levels(self._loaded_level, level) >= 0

    def _request(self, level):
        self._state = 'requested'
        self._params['requested_level'] = level
        self._params['loaded_level'] = self._loaded_level
        self._graph.on_request(self, self._params)

    def request(self, level=None):
        if(level is None):
            level = self.levels[-1]

        if(self._state == 'initial'):
            self._request(level)

        elif self._state == 'requested':
            self._request_again_when_done = level

        elif self._state == 'loaded':
            if(self._compare_levels(self._loaded_level, level) < 0):
                self._request(level)

    def set(self, data, level=None):
        if(level is None):
            level = self.levels[-1]

        self._data = data
        self._state = 'loaded'
        self._loaded_level = level

        if self._request_again_when_done:
            tmp = self._request_again_when_done
            self._request_again_when_done = None
            self.request(tmp)





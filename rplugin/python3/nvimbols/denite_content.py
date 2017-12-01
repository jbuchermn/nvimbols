class DeniteContent:
    def __init__(self):
        self._candidates = []
        self._complete = False

    def __iadd__(self, candidates):
        self._candidates += candidates

    def get_candidates(self):
        return self._candidates

    def set_complete(self, complete=True):
        self._complete = complete

    def is_complete(self):
        return self._complete

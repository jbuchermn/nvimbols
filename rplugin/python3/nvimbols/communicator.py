class Communicator:
    def __init__(self):
        self._objs = {}

    def set(self, name, obj):
        self._objs[name] = obj

    def get(self, name):
        return self._objs[name]


COMM = Communicator()

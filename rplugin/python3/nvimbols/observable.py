from nvimbols.util import on_error


class Observable:
    def __init__(self):
        self._observers = {}
        self._id = 0

    def on_update(self, func):
        self._id += 1
        self._observers[self._id] = func
        return self._id

    def remove_on_update(self, id_):
        del self._observers[id_]

    def _notify(self):
        for id_ in self._observers:
            try:
                self._observers[id_]()
            except Exception as err:
                on_error(None, err)

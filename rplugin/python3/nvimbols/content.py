from nvimbols.util import log
import copy


class Component:
    def __init__(self, children):
        self.line = 0
        self.start_col = 0
        self.end_col = 0
        self.children = children


class Wrapper(Component):
    def __init__(self, *args):
        log(args)
        Component.__init__(self, args)


class Link(Component):
    def __init__(self, target, child):
        Component.__init__(self, [child])
        self.target = target


class Highlight(Component):
    def __init__(self, name, child):
        Component.__init__(self, [child])
        self.name = name


class Content:
    def __init__(self):
        self._raw = ""
        self._components = []

    def current(self):
        line = self._raw.count('\n') + 1
        col = len(self._raw) - self._raw.rfind('\n')
        return line, col

    def __iadd__(self, data):
        return self.append(data)

    def append(self, data):
        if(isinstance(data, Component)):
            start_line, start_col = self.current()

            for c in data.children:
                self += c

            end_line, end_col = self.current()

            for line in range(start_line, end_line + 1):
                d = copy.copy(data)
                d.line, d.start_col, d.end_col = line, start_col if line == start_line else 0, end_col if line == end_line else -1
                self._components.append(d)

            data.end_position = len(self._raw)
        else:
            self._raw += str(data)

        return self

    def raw(self):
        return self._raw.split('\n')

    def highlights(self):
        for c in self._components:
            if(isinstance(c, Highlight)):
                yield c

    def links(self):
        for c in self._components:
            if(isinstance(c, Link)):
                yield c

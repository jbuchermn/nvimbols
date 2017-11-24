from nvimbols.util import log
import copy


class Component:
    def __init__(self, children):
        self.line = 0
        self.start_col = 0
        self.end_col = 0
        self.children = children

    def __eq__(self, other):
        if other is None:
            return False
        
        return (
            self.line == other.line and
            self.start_col == other.start_col and
            self.end_col == other.end_col and
            self.children == other.children
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class Wrapper(Component):
    def __init__(self, *args):
        Component.__init__(self, args)

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, Wrapper) or not Component.__eq__(self, other):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class Link(Component):
    def __init__(self, target, child):
        Component.__init__(self, [child])
        self.target = target

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, Link) or not Component.__eq__(self, other):
            return False

        return self.target == other.target

    def __ne__(self, other):
        return not self.__eq__(other)


class Highlight(Component):
    def __init__(self, name, child):
        Component.__init__(self, [child])
        self.name = name

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, Highlight) or not Component.__eq__(self, other):
            return False

        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


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
                d.line, d.start_col, d.end_col = line, start_col if line == start_line else 1, end_col if line == end_line else -1
                if(d.start_col != d.end_col):
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

    def __eq__(self, other):
        if other is None:
            return False

        return self._raw == other._raw and self._components == other._components

    def __ne__(self, other):
        return not self.__eq__(other)






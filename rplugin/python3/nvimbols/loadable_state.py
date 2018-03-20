from enum import Enum
from functools import total_ordering


@total_ordering
class LoadableState(Enum):
    NOT_LOADED = 0
    PREVIEW = 1
    FULL = 2

    def __lt__(self, other):
        if type(self) != type(other):
            return NotImplemented

        return self.value < other.value

class LoadWrapper:
    def __init__(self, location):
        self._loaded = False
        self._content = None
        self._location = location

    def is_loading(self):
        return not self._loaded

    def get(self):
        return self._content

    def set(self, content):
        self._content = content
        self._loaded = True
        if self._content is not None:
            self._content.location = self._location


class LoadListWrapper(list):
    def __init__(self):
        self._loaded = False
        self._incomplete = False

    def reset(self):
        self._loaded = False
        self._incomplete = False
        del self[:]

    def is_loading(self):
        return not self._loaded

    def is_incomplete(self):
        return self._incomplete

    def loaded(self, incomplete=False):
        self._incomplete = incomplete
        self._loaded = True


class SymbolLocation:
    """
    Includes lines start_line... end_line and columns start_col... end_col-1
    """
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None):
        if(end_line is None):
            end_line = start_line
        if(end_col is None):
            end_col = start_col + 1

        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.start_col = start_col
        self.end_col = end_col

        self.symbol = LoadWrapper(self)

    def contains(self, other):
        if(self.filename != other.filename):
            return False

        return (self.start_line <= other.start_line and
                (self.end_line == -1 or self.end_line >= other.end_line) and
                (self.start_line < other.start_line or (self.start_col <= other.start_col)) and
                ((self.end_line == -1 or self.end_line > other.end_line) or (self.end_col == -1 or self.end_col >= other.end_col)))

    def __str__(self):
        return "%s:%i:%i:%i:%i" % (self.filename, self.start_line, self.start_col, self.end_line, self.end_col)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            self.filename == other.filename and
            self.start_line == other.start_line and
            self.end_line == other.end_line and
            self.start_col == other.start_col and
            self.end_col == other.end_col
        )


class Symbol:
    def __init__(self):
        """
        Data to be set once the information (without references) for this symbol is retrieved
        """
        self.name = None
        self.data = {}

        """
        Data to be set once the references are retrieved
        Maps from reference.name to a LoadListWrapper of symbol locations
        """
        self._target_of = {}
        self._source_of = {}

    def data_set(self):
        return self.name is not None

    def target_of_set(self, reference):
        return not self.get_target_of(reference).is_loading()

    def source_of_set(self, reference):
        return not self.get_source_of(reference).is_loading()

    def get_target_of(self, reference):
        if reference.name not in self._target_of:
            self._target_of[reference.name] = LoadListWrapper()

        return self._target_of[reference.name]

    def get_source_of(self, reference):
        if reference.name not in self._source_of:
            self._source_of[reference.name] = LoadListWrapper()

        return self._source_of[reference.name]

    def __str__(self):
        return "Symbol(%s): %s" % (self.location, self.data)





















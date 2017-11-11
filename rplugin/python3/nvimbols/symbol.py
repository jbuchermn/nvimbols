class SymbolLocation:
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None):
        if(end_line is None):
            end_line = start_line
        if(end_col is None):
            end_col = start_col

        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.start_col = start_col
        self.end_col = end_col

    def contains(self, other):
        if(self.filename != other.filename):
            return False

        return (self.start_line <= other.start_line and
                (self.end_line == -1 or self.end_line >= other.end_line) and
                (self.start_line < other.start_line or (self.start_col <= other.start_col)) and
                ((self.end_line == -1 or self.end_line > other.end_line) or (self.end_col == -1 or self.end_col > other.end_col)))

    def __str__(self):
        return "%s:%i:%i:%i:%i" % (self.filename, self.start_line, self.start_col, self.end_line, self.end_col)

    def __eq__(self, other):
        return (
            self.filename == other.filename and
            self.start_line == other.start_line and
            self.end_line == other.end_line and
            self.start_col == other.start_col and
            self.end_col == other.end_col
        )


class Symbol:
    def __init__(self, location):
        self.location = location

        """
        Data to be set once the information (without references) for this symbol is retrieved
        """
        self.name = None
        self.data = {}

        """
        Data to be set once the references are retrieved
        Maps from reference.name to a list of symbols
        """
        self.target_of = {}
        self.source_of = {}

    def data_set(self):
        return self.name is not None

    def targets_set(self, reference):
        return reference.name in self.target_of

    def source_set(self, reference):
        return reference.name in self.source_of

    def __str__(self):
        return "Symbol(%s): %s" % (self.location, self.data)


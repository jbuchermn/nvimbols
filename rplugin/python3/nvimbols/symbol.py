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
    """
    Meant to be subclassed within the specific source, plain old data object.
    """
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

        """
        Dictionary rendered as Key: Value
        """
        self.data = {}

    def __str__(self):
        return "Symbol(%s): %s" % (self.name, self.kind)





















class Location:
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
        if not isinstance(other, Location):
            raise Exception("Not a location given")

        if self.filename != other.filename:
            return False

        return (self.start_line <= other.start_line and
                (self.end_line == -1 or self.end_line >= other.end_line) and
                (self.start_line < other.start_line or (self.start_col <= other.start_col)) and
                ((self.end_line == -1 or self.end_line > other.end_line) or (self.end_col == -1 or self.end_col >= other.end_col)))

    def __str__(self):
        return "%s:%i:%i:%i:%i" % (self.filename, self.start_line, self.start_col, self.end_line, self.end_col)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)


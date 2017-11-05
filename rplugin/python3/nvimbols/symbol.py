class SymbolLocation:
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None):
        if(end_line is None): end_line = start_line
        if(end_col is None): end_col = start_col

        self._filename = filename
        self._start_line = start_line
        self._end_line = end_line
        self._start_col = start_col
        self._end_col = end_col

    def contains(self, other):
        if(self._filename != other._filename):
            return False

        return (self._start_line <= other._start_line and
                self._end_line >= other._end_line and
                (self._start_line < other._start_line or (self._start_col <= other._start_col)) and
                (self._end_line > other._end_line or (self._end_col > other._end_col)))

    def __str__(self):
        return "%s:%i:%i:%i:%i" % (self._filename, self._start_line, self._start_col, self._end_line, self._end_col)

    def __eq__(self, other):
        return (
            self._filename == other._filename and
            self._start_line == other._start_line and
            self._end_line == other._end_line and
            self._start_col == other._start_col and
            self._end_col == other._end_col
        )


class Symbol:
    def __init__(self, name, kind, type_, location, references=[], referenced_by=[]):
        self._name = name
        self._kind = kind
        self._type = type_
        self._location = location
        self._references = references
        self._referenced_by = referenced_by

    def __str__(self):
        return "Symbol(%s): %s" % (self._kind, self._name)

    def to_dict(self):
        result = dict(self.__dict__)
        result['_references'] = [r.to_dict() for r in result['_references']]
        result['_referenced_by'] = [r.to_dict() for r in result['_referenced_by']]
        result['_location'] = result['_location'].__dict__

        return result

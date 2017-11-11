class SymbolsGraph:
    def __init__(self, source):
        self._source = source
        self.references = source.references

    def symbol_at_location(self, location):
        """
        Possibly long running method to acquire all information needed for a symbol
        on whose location the cursor currently is
        """
        symbol = self._source.symbol_at_location(location)
        if(symbol is None):
            return symbol

        for r in self.references:
            if not r.name in symbol.target_of:
                symbol.target_of[r.name] = []
                for source in self._source.load_target_of(symbol, r):
                    symbol.target_of[r.name] += [source]

            if not r.name in symbol.source_of:
                symbol.source_of[r.name] = []
                for target in self._source.load_source_of(symbol, r):
                    symbol.source_of[r.name] += [target]

        """
        ToDo: Store symbols in cache (self._symbols)
        Sources should be allowed to create new symbols in load_source_of (further than one node away from symbol),
        so here we should go through the graph and check for new symbols
        """

        return symbol

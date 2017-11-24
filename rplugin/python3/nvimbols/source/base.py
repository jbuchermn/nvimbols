import os
from abc import abstractmethod
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef


class Base:
    def __init__(self, vim):
        self._vim = vim
        self.name = None
        self.filetypes = []
        self.references = [TargetRef, ParentRef, InheritanceRef]

    @abstractmethod
    def load_symbol(self, location):
        """
        Loads data into location.symbol without loading any references. Possibly long-running,
        dispatched in seperate worker thread

        Place symbol by location.symbol.set(symbol) and set location.start_col, ... correctly

        If there is no symbol at that location, place None
        """
        pass

    @abstractmethod
    def load_source_of(self, symbol, reference):
        """
        Loads data into symbol.source_of[reference.name], which is a LoadableList of SymbolLocations,
        Symbols within the locations can be set within this function, but this needn't happen.

        Place like
            symbol.get_source_of(reference) += [SymbolLocation(...)]
            symbol.get_source_of(reference) += [SymbolLocation(...)]
            symbol.get_source_of(reference).loaded()

        loaded may be called with loaded(True), to state that not all items have been loaded
        (f. e. references to standard library classes might be many and not really interesting)

        If there are no references, simply call symbol.source_of.loaded()
        """
        pass

    @abstractmethod
    def load_target_of(self, symbol, reference):
        """
        Analogously to load_source_of
        """
        pass

    def render_location(self, location):
        """
        Override this method to implement custom rendering
        """
        content = Content()

        if(location is None or location.symbol.is_loading()):
            content += "..."
        else:
            symbol = location.symbol.get()

            if symbol is None:
                content += "No symbol"
            else:
                content += Wrapper("Symbol: ", Highlight('Statement', symbol.name), "\n")
                for d in symbol.data:
                    content += Wrapper("    %s: " % d, Highlight('Type', symbol.data[d]), "\n")

                for ref in self.references:
                    source_of = symbol.get_source_of(ref)
                    content += Highlight('Title', "\n  ----  " + ref.display_targets + "  ----  \n")

                    if(source_of.is_loading()):
                        content += "..."
                    elif(len(source_of) > 0):
                        for loc in source_of:
                            content += Link(loc, Highlight('Type', "%s:%i\n" % (os.path.basename(loc.filename), loc.start_line)))

                    if(source_of.is_incomplete()):
                        content += Highlight('PreProc', '[...]\n')

                    target_of = symbol.get_target_of(ref)
                    content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")

                    if(target_of.is_loading()):
                        content += "..."
                    elif(len(target_of) > 0):
                        for loc in target_of:
                            content += Link(loc, Highlight('Type', "%s:%i\n" % (os.path.basename(loc.filename), loc.start_line)))
                    
                    if(target_of.is_incomplete()):
                        content += Highlight('PreProc', '[...]\n')

        return content

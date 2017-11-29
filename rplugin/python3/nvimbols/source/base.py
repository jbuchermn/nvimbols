import os
from abc import abstractmethod
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef
from nvimbols.util import log


class Base:
    def __init__(self, vim):
        self._vim = vim
        self._graph = None

        """
        Configuration. Replace in YourSource.__init__
        """
        self.name = None
        self.filetypes = []
        self.references = [TargetRef, ParentRef, InheritanceRef]

        """
        Maximal number of parallel tasks. For non-thredsafe source, this must be set to 1.
        """
        self.tasks = 8

    def set_graph(self, graph):
        self._graph = graph

    @abstractmethod
    def load_symbol(self, wrapper):
        """
        Loads data into wrapper.symbol without loading any references. Possibly long-running,
        dispatched in seperate worker thread

        Remember to set wrapper.location correctly (This is initialised to point
        to one specific character; once the symbol is known location should extend over the whole symbol)

        Place symbol by
            wrapper.symbol.set(MyOwnSymbol(foo, bar)) # or Symbol(name, kind)
            wrapper.location.start_col = 1
            wrapper.location.end_col = 10

        If there is no symbol at that location, place None
        """
        pass

    @abstractmethod
    def load_source_of(self, wrapper, reference):
        """
        Loads data into wrapper.source_of[reference.name].
        Symbols within the locations can be set within this function, but this needn't happen.

        Place by
            symbol.source_of[reference.name].set([self._graph.create_wrapper(location1), self._graph.create_wrapper(location2)])

        set can be called with an additional parameter "incomplete" to specify, that not all elements have been loaded. Currently
        there is no cursor based loading of list. This is only meant to display information, that not all usages (of e. g. std::vector)
        have been fetched.
        """
        pass

    @abstractmethod
    def load_target_of(self, wrapper, reference):
        """
        Loads data into wrapper.target_of[reference.name].
        Symbols within the locations can be set within this function, but this needn't happen.

        Place by
            symbol.target_of[reference.name].set([self._graph.create_wrapper(location1), self._graph.create_wrapper(location2)])

        set can be called with an additional parameter "incomplete" to specify, that not all elements have been loaded. Currently
        there is no cursor based loading of list. This is only meant to display information, that not all usages (of e. g. std::vector)
        have been fetched.
        """
        pass

    def render(self, wrapper):
        """
        Method returns a Content instance

        Override this method to implement custom rendering.
        Data not yet fetched can be request()ed; once it is loaded, render will be called again.
        """
        content = Content()

        if(not wrapper.symbol.is_loaded()):
            content += "..."
            wrapper.symbol.request()
        else:
            symbol = wrapper.symbol.get()

            if symbol is None:
                content += "No symbol"
            else:
                content += Wrapper("Symbol: ", Highlight('Statement', symbol.name), "\n")
                content += Wrapper("        ", Highlight('Type', symbol.kind), "\n")
                for d in symbol.data:
                    content += Wrapper("    %s: " % d, Highlight('Type', symbol.data[d]), "\n")

                for ref in self.references:
                    source_of = wrapper.source_of[ref.name]
                    content += Highlight('Title', "\n  ----  " + ref.display_targets + "  ----  \n")

                    if(not source_of.is_loaded()):
                        content += "..."
                        source_of.request()
                    else:
                        for w in source_of.get():
                            content += Link(w.location, Highlight('Type', "%s:%i\n" % (os.path.basename(w.location.filename), w.location.start_line)))
                        if(source_of.is_incomplete()):
                            content += Highlight('PreProc', "[...]\n")

                    target_of = wrapper.target_of[ref.name]
                    content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")

                    if(not target_of.is_loaded()):
                        content += "..."
                        target_of.request()
                    else:
                        for w in target_of.get():
                            content += Link(w.location, Highlight('Type', "%s:%i\n" % (os.path.basename(w.location.filename), w.location.start_line)))

                        if(target_of.is_incomplete()):
                            content += Highlight('PreProc', "[...]\n")

        return content

    def render_denite(self, wrapper, context):
        """
        Method returns denite candidates as list.

        Override this method to implement custom rendering.
        If rendering is not complete, set context['is_async'] = True. When this method is called, context['is_async'] == False holds.
        """
        result = []

        def wrapper_to_candidate(wrapper, title):
            return {
                'abbr': title + ' ' + str(wrapper.location),
                'word': str(wrapper.location),
                'action__path': wrapper.location.filename,
                'action__line': wrapper.location.start_line,
                'action__col': wrapper.location.start_col,
                'action__text': str(wrapper.location),
                '__nvimbols_hash': str(wrapper.location)
            }

        def add_to_result(result, wrapper, title):
            cand = wrapper_to_candidate(wrapper, title)
            for c in context['all_candidates']:
                if c['__nvimbols_hash'] == str(wrapper.location):
                    return

            result += [cand]

        for ref in self.references:
            source_of = wrapper.source_of[ref.name]
            if(not source_of.is_loaded()):
                context['is_async'] = True
            else:
                for w in source_of.get():
                    add_to_result(result, w, ref.display_targets)

            target_of = wrapper.target_of[ref.name]
            if(not target_of.is_loaded()):
                context['is_async'] = True
            else:
                for w in target_of.get():
                    add_to_result(result, w, ref.display_sources)

        return result












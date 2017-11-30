import os
from abc import abstractmethod
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef
from nvimbols.util import log
from nvimbols.loadable import LOADABLE_PREVIEW, LOADABLE_FULL


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
    def load_symbol(self, params):
        """
        params contains:
            'wrapper'
            'requested_level'
            'loaded_level'

        Loads data into wrapper.symbol without loading any references. Possibly long-running,
        dispatched in seperate worker thread

        Remember to set wrapper.location correctly (This is initialised to point
        to one specific character; once the symbol is known location should extend over the whole symbol)

        Place symbol by
            wrapper.symbol.set(MyOwnSymbol(foo, bar)) # or Symbol(name, kind)
            wrapper.location.start_col = 1
            wrapper.location.end_col = 10
        
        Second parameter of set is the loaded level, should match requested_level (or a higher level). Defaults to LOADABLE_FULL.

        If there is no symbol at that location, place None
        """
        pass

    @abstractmethod
    def load_source_of(self, params):
        """
        params contains:
            'wrapper'
            'reference'
            'requested_level'
            'loaded_level'

        Loads data into wrapper.source_of[reference.name].
        Symbols within the locations can be set within this function, but this needn't happen.

        Place by
            symbol.source_of[reference.name].set([self._graph.create_wrapper(location1), self._graph.create_wrapper(location2)])

        Second parameter of set is the loaded level, should match requested_level (or a higher level). Defaults to LOADABLE_FULL.
        """
        pass

    @abstractmethod
    def load_target_of(self, params):
        """
        params contains:
            'wrapper'
            'reference'
            'requested_level'
            'loaded_level'

        Loads data into wrapper.target_of[reference.name].
        Symbols within the locations can be set within this function, but this needn't happen.

        Place by
            symbol.target_of[reference.name].set([self._graph.create_wrapper(location1), self._graph.create_wrapper(location2)])

        Second parameter of set is the loaded level, should match requested_level (or a higher level). Defaults to LOADABLE_FULL.
        """
        pass

    def render(self, wrapper):
        """
        Method returns a Content instance

        Override this method to implement custom rendering.
        Data not yet fetched can be request()ed; once it is loaded, render will be called again.
        """
        content = Content()

        def max_slice(n, arr):
            return arr if len(arr) < n else arr[:n]

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
                        source_of.request(LOADABLE_PREVIEW)
                    else:
                        is_preview = (not source_of.is_loaded(LOADABLE_FULL)) or (len(source_of.get()) > 100)

                        for w in max_slice(100, source_of.get()):
                            content += Link(w.location, Highlight('Type', "%s:%i\n" % (os.path.basename(w.location.filename), w.location.start_line)))
                        if is_preview:
                            content += Highlight('PreProc', "[...]\n")

                    target_of = wrapper.target_of[ref.name]
                    content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")

                    if(not target_of.is_loaded(LOADABLE_PREVIEW)):
                        content += "..."
                        target_of.request(LOADABLE_PREVIEW)
                    else:
                        is_preview = (not target_of.is_loaded(LOADABLE_FULL)) or (len(target_of.get()) > 100)

                        for w in max_slice(100, target_of.get()):
                            content += Link(w.location, Highlight('Type', "%s:%i\n" % (os.path.basename(w.location.filename), w.location.start_line)))

                        if is_preview:
                            content += Highlight('PreProc', "[...]\n")

        return content

    def render_denite(self, wrapper, context):
        """
        Method returns denite candidates as list.

        Override this method to implement custom rendering.
        If rendering is not complete, set context['is_async'] = True. When this method is called, context['is_async'] == False holds.
        """
        result = []

        title_length = 12
        kind_length = 28

        def fit(text, length):
            if len(text) > length:
                return text[:length]
            else:
                return text.ljust(length, ' ')

        def wrapper_to_candidate(wrapper, title):
            if(not wrapper.symbol.is_loaded()):
                context['is_async'] = True
                wrapper.symbol.request()
                return None

            info = wrapper.symbol.get().kind if wrapper.symbol.get() is not None else ""
            return {
                'word': fit(title, title_length) + fit(info, kind_length) + str(wrapper.location),
                'action__path': wrapper.location.filename,
                'action__line': wrapper.location.start_line,
                'action__col': wrapper.location.start_col,
                'action__text': str(wrapper.location),
                '__nvimbols_hash': str(wrapper.location)
            }

        def add_to_result(result, wrapper, title):
            cand = wrapper_to_candidate(wrapper, title)
            if cand is None:
                return
            for c in context['all_candidates']:
                if c['__nvimbols_hash'] == str(wrapper.location):
                    return

            result += [cand]

        for ref in self.references:
            source_of = wrapper.source_of[ref.name]
            if(not source_of.is_loaded(LOADABLE_FULL)):
                source_of.request(LOADABLE_FULL)
                context['is_async'] = True
            else:
                for w in source_of.get():
                    add_to_result(result, w, ref.display_targets)

            target_of = wrapper.target_of[ref.name]
            if(not target_of.is_loaded(LOADABLE_FULL)):
                target_of.request(LOADABLE_FULL)
                context['is_async'] = True
            else:
                for w in target_of.get():
                    add_to_result(result, w, ref.display_sources)

        return result












import os
from abc import abstractmethod
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.denite_content import DeniteContent
from nvimbols.reference import TargetReference, ParentReference, InheritanceReference
from nvimbols.util import log
from nvimbols.symbol import LoadableState


class Base:
    def __init__(self, vim):
        self._vim = vim

        """
        Default configuration. Replace in YourSource.__init__
        """
        self.name = None
        self.filetypes = []
        self.references = [TargetReference, ParentReference, InheritanceReference]
        self.tasks = 4  # Set tasks=1 for non-threadsafe sources

    @abstractmethod
    def request(self, req):
        pass

    def render(self, symbol):
        """
        Method returns a Content instance

        Override this method to implement custom rendering.
        Data not yet fetched can be request()ed; once it is loaded, render will be called again.
        """
        content = Content()

        def max_slice(n, arr):
            return arr if len(arr) < n else arr[:n]

        if(not symbol.state() >= LoadableState.FULL):
            content += "..."
            symbol.request()
        else:
            """
            Render symbol
            """
            content += Wrapper("Symbol: ", Highlight('Statement', symbol.name), "\n")
            content += Wrapper("        ", Highlight('Type', symbol.kind), "\n")

            for reference_class in self.references:
                ref = reference_class()

                """
                Render source of
                """
                content += Highlight('Title', "\n  ----  " + ref.display_targets + "  ----  \n")

                if not symbol.state_source_of(reference_class) >= LoadableState.PREVIEW:
                    content += "..."
                    symbol.request_source_of(reference_class, LoadableState.PREVIEW)
                else:
                    arr = symbol.get_source_of(reference_class)
                    is_preview = symbol.state_source_of(reference_class) < LoadableState.FULL or (len(arr) > 100)

                    if len(arr) > 0:
                        content.add_quickjump("first_source_of_%s" % ref.name, arr[0]._to.location)

                    for w in max_slice(100, arr):
                        content += Link(w._to.location,
                                        Highlight('Type',
                                                  "%s:%i\n" % (os.path.basename(w._to.location.filename),
                                                               w._to.location.start_line)))
                    if is_preview:
                        content += Highlight('PreProc', "[...]\n")

                """
                Render target of
                """
                content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")

                if not symbol.state_target_of(reference_class) >= LoadableState.PREVIEW:
                    content += "..."
                    symbol.request_target_of(reference_class, LoadableState.PREVIEW)
                else:
                    arr = symbol.get_target_of(reference_class)
                    is_preview = symbol.state_target_of(reference_class) < LoadableState.FULL or (len(arr) > 100)

                    if len(arr) > 0:
                        content.add_quickjump("first_source_of_%s" % ref.name, arr[0]._from.location)

                    for w in max_slice(100, arr):
                        content += Link(w._to.location,
                                        Highlight('Type',
                                                  "%s:%i\n" % (os.path.basename(w._from.location.filename),
                                                               w._from.location.start_line)))
                    if is_preview:
                        content += Highlight('PreProc', "[...]\n")

        return content

    def render_denite(self, symbol):
        """
        Method returns denite candidates as list.

        Override this method to implement custom rendering.
        If we are still waiting for data, set result.set_complete(False), otherwise True. Defaults to False.
        Every candidate needs to include a __hash which uniquely identifies this candidate among all candidates
        """
        result = DeniteContent()
        result.set_complete()

        title_length = 12
        kind_length = 28

        def fit(text, length):
            if len(text) > length:
                return text[:length]
            else:
                return text.ljust(length, ' ')

        def symbol_to_candidate(symbol, title, result):
            if symbol.state() < LoadableState.FULL:
                result.set_complete(False)
                symbol.request()
                return None

            result += [{
                'word': fit(title, title_length) + fit(symbol.kind, kind_length) + str(symbol.location),
                'action__path': symbol.location.filename,
                'action__line': symbol.location.start_line,
                'action__col': symbol.location.start_col,
                'action__text': str(symbol.location),
                '__hash': hash(symbol.location)
            }]

        for reference_class in self.references:
            ref = reference_class()

            """
            Render source of
            """
            if symbol.state_source_of(reference_class) < LoadableState.FULL:
                result.set_complete(False)
                symbol.request_source_of(reference_class)
            else:
                for w in symbol.get_source_of(reference_class):
                    symbol_to_candidate(w._to, ref.display_targets, result)

            """
            Render target of
            """
            if symbol.state_target_of(reference_class) < LoadableState.FULL:
                result.set_complete(False)
                symbol.request_target_of(reference_class)
            else:
                for w in symbol.get_target_of(reference_class):
                    symbol_to_candidate(w._from, ref.display_sources, result)

        return result

    def render_sub_graph(self, sub_graph):
        if not sub_graph.state() == LoadableState.FULL:
            sub_graph.request()

        """
        TODO
        Find ultimate targets of ParentReference.. render children and grandchildren
        """

        return Content()

    def render_sub_graph_denite(self, sub_graph):
        if not sub_graph.state() == LoadableState.FULL:
            sub_graph.request()
            return DeniteContent()

        result = DeniteContent()
        result.set_complete()

        name_length = 28
        kind_length = 12

        def fit(text, length):
            if len(text) > length:
                return text[:length]
            else:
                return text.ljust(length, ' ')

        def symbol_to_candidate(symbol, result):
            if symbol.state() < LoadableState.FULL:
                result.set_complete(False)
                symbol.request()
                return None

            result += [{
                'word': fit(symbol.name, name_length) + fit(symbol.kind, kind_length) + str(symbol.location),
                'action__path': symbol.location.filename,
                'action__line': symbol.location.start_line,
                'action__col': symbol.location.start_col,
                'action__text': str(symbol.location),
                '__hash': hash(symbol.location)
            }]

        for symbol in sub_graph.symbols():
            symbol_to_candidate(symbol, result)

        return result









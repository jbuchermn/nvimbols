import os
from nvimbols.util import log
from nvimbols.renderer.base import Base
from nvimbols.reference import ParentReference
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.denite_content import DeniteContent
from nvimbols.symbol import LoadableState


class Renderer(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = "Default"
        self.sources = ["*"]
        self.modes = ["symbol", "list"]

    def render(self, graph, cursor_location, mode):
        def loading():
            content = Content()
            content += "..."
            return content

        def empty():
            content = Content()
            content += "No symbol"
            return content

        def render_list(graph, filename):
            sub_graph_file = graph.sub_graph_file(filename)
            if sub_graph_file.state() < LoadableState.PREVIEW:
                sub_graph_file.request()
                return loading()

            ready = True
            for n in sub_graph_file.nodes():
                if n.state() < LoadableState.FULL:
                    n.request()
                    ready = False
                if n.state_source_of(ParentReference) < LoadableState.FULL:
                    n.request_source_of(ParentReference)
                    ready = False

            if ready:
                return self.render_list(graph, sub_graph_file)
            else:
                return loading()

        def render_symbol(graph, cursor_location):
            symbol = graph.symbol(cursor_location)
            if symbol is None:
                graph.request_at(cursor_location)
                return loading()
            else:
                return self.render_symbol(graph, symbol)

        if mode == 'symbol':
            if graph.is_empty(cursor_location):
                return empty()
            else:
                return render_symbol(graph, cursor_location)

        elif mode == 'list':
            return render_list(graph, cursor_location.filename)

        else:
            raise Exception("Unsupported mode: %s" % mode)

    def render_symbol(self, graph, symbol):
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

            for reference_class in graph.edge_classes():
                ref = reference_class()

                """
                Render source of
                """
                content += Highlight('Title', "\n  ----  " + ref.display_targets + "  ----  \n")

                if symbol.state_source_of(reference_class) < LoadableState.PREVIEW:
                    content += "..."
                    symbol.request_source_of(reference_class, LoadableState.PREVIEW)
                else:
                    arr = graph.source_of(symbol, reference_class)
                    is_preview = symbol.state_source_of(reference_class) < LoadableState.FULL or (len(arr) > 100)

                    if len(arr) > 0:
                        content.add_quickjump("first_source_of_%s" % ref.name, arr[0].location)

                    for w in max_slice(100, arr):
                        content += Link(w.location,
                                        Highlight('Type',
                                                  "%s:%i\n" % (os.path.basename(w.location.filename),
                                                               w.location.start_line)))
                    if is_preview:
                        content += Highlight('PreProc', "[...]\n")

                """
                Render target of
                """
                content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")

                if symbol.state_target_of(reference_class) < LoadableState.PREVIEW:
                    content += "..."
                    symbol.request_target_of(reference_class, LoadableState.PREVIEW)
                else:
                    arr = graph.target_of(symbol, reference_class)
                    is_preview = symbol.state_target_of(reference_class) < LoadableState.FULL or (len(arr) > 100)

                    if len(arr) > 0:
                        content.add_quickjump("first_target_of_%s" % ref.name, arr[0].location)

                    for w in max_slice(100, arr):
                        content += Link(w.location,
                                        Highlight('Type',
                                                  "%s:%i\n" % (os.path.basename(w.location.filename),
                                                               w.location.start_line)))
                    if is_preview:
                        content += Highlight('PreProc', "[...]\n")

        return content

    def render_list(self, graph, sub_graph):
        parents = [n for n in sub_graph.nodes() if
                   len(sub_graph.source_of(n, ParentReference)) == 0]

        content = Content()
        if len(parents) == 0:
            content += "No symbols"
            return content

        for p in parents:
            if p.state() < LoadableState.FULL:
                p.request()

            content += Link(p.location,
                            Wrapper(Highlight('Statement', p.name),
                                    " ",
                                    Highlight('Type', p.kind),
                                    "\n"))

            for c in sub_graph.target_of(p, ParentReference):
                content += Link(c.location,
                                Wrapper(Highlight('PreProc', "  " + c.name),
                                        "\n"))

        return content

    def render_denite(self, graph, cursor_location, mode):
        def loading():
            content = DeniteContent()
            content.set_complete(False)
            return content

        def render_list(graph, filename):
            sub_graph_file = graph.sub_graph_file(filename)
            if sub_graph_file.state() < LoadableState.PREVIEW:
                sub_graph_file.request()
                return loading()

            ready = True
            for n in sub_graph_file.nodes():
                if n.state() < LoadableState.FULL:
                    n.request()
                    ready = False
                if n.state_source_of(ParentReference) < LoadableState.FULL:
                    n.request_source_of(ParentReference)
                    ready = False

            if ready:
                return self.render_denite_list(graph, sub_graph_file)
            else:
                return loading()

        def render_symbol(graph, cursor_location):
            symbol = graph.symbol(cursor_location)
            if symbol is None:
                graph.request_at(cursor_location)
                return loading()
            else:
                return self.render_denite_symbol(graph, symbol)

        if mode == 'symbol':
            if graph.is_empty(cursor_location):
                return DeniteContent()
            else:
                return render_symbol(graph, cursor_location)

        elif mode == 'list':
            return render_list(graph, cursor_location.filename)

        else:
            raise Exception("Unsupported mode: %s" % mode)

    def render_denite_symbol(self, graph, symbol):
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

        for reference_class in graph.edge_classes():
            ref = reference_class()

            """
            Render source of
            """
            if symbol.state_source_of(reference_class) < LoadableState.FULL:
                result.set_complete(False)
                symbol.request_source_of(reference_class)
            else:
                for w in graph.source_of(symbol, reference_class):
                    symbol_to_candidate(w, ref.display_targets, result)

            """
            Render target of
            """
            if symbol.state_target_of(reference_class) < LoadableState.FULL:
                result.set_complete(False)
                symbol.request_target_of(reference_class)
            else:
                for w in graph.target_of(symbol, reference_class):
                    symbol_to_candidate(w, ref.display_sources, result)

        return result

    def render_denite_list(self, graph, sub_graph):
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

        for symbol in sub_graph.nodes():
            symbol_to_candidate(symbol, result)

        return result









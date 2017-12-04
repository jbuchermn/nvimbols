from nvimbols.loadable import LOADABLE_FULL
from nvimbols.symbol import SymbolLocationFile
from nvimbols.graph import SYMBOL_FILE


class Reference:
    def __init__(self, name, display_targets, display_sources):
        self.name = name
        self.display_sources = display_sources
        self.display_targets = display_targets

    def validate(self, graph):
        pass


class TargetReference(Reference):
    def __init__(self):
        super().__init__('references', 'Targets', 'Usages')


class ParentReference(Reference):
    def __init__(self):
        super().__init__('is_child_of', 'Parents', 'Children')

    def validate(self, graph):
        for d in graph.get_all():
            parents = d.source_of[self.name]
            if(not parents.is_loaded(LOADABLE_FULL)):
                parents.request(LOADABLE_FULL)
                continue

            """
            Ensure hierarchy within file and unique parent
            """
            tmp = []
            for p in parents.get():
                if p.location.filename == d.location.filename:
                    tmp += [p]

            parents.set(tmp[:1] if len(tmp) > 0 else [], LOADABLE_FULL)

            """
            Set filename as parent of roots
            """
            if not d.type == SYMBOL_FILE and len(parents.get()) == 0:
                file_wrapper = graph.create_wrapper(SymbolLocationFile(d.location.filename))
                parents.set([file_wrapper], LOADABLE_FULL)

        """
        Delete children, that are not really children
        """
        for d in graph.get_all():
            children = d.target_of[self.name]
            if(not children.is_loaded()):
                continue

            children.set(children.get(), LOADABLE_FULL)

            for i in range(len(children.get()) - 1, 0, -1):
                c = children.get()[i]
                if c.source_of[self.name].is_loaded(LOADABLE_FULL) and d not in c.source_of[self.name].get():
                    del children.get()[i]


class InheritanceReference(Reference):
    def __init__(self):
        super().__init__('inherits_from', 'Supers', 'Subs')


TargetRef = TargetReference()
ParentRef = ParentReference()
InheritanceRef = InheritanceReference()

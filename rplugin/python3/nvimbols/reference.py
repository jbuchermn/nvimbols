from nvimbols.loadable import LOADABLE_FULL
from nvimbols.symbol import SymbolLocationFile
from nvimbols.util import log
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
            """
            Request parent of all symbols
            """
            parents = d.source_of[self.name]
            if(not parents.is_loaded(LOADABLE_FULL)):
                parents.request()
                continue

            """
            Ensure hierarchy within file and unique parent
            """
            tmp = None
            for p in parents.get():
                if p.location.filename == d.location.filename:
                    tmp = p
                    break

            parents.set([tmp] if tmp is not None else [])

        """
        Delete children, that are not really children
        """
        for d in graph.get_all():
            children = d.target_of[self.name]
            if(not children.is_loaded()):
                continue

            new_children = []
            for c in children.get():
                log(c.location)
                log(c.symbol.get())
                if (not c.source_of[self.name].is_loaded(LOADABLE_FULL)) or (d in c.source_of[self.name].get()):
                    new_children += [c]

            children.set(new_children)


class InheritanceReference(Reference):
    def __init__(self):
        super().__init__('inherits_from', 'Supers', 'Subs')


TargetRef = TargetReference()
ParentRef = ParentReference()
InheritanceRef = InheritanceReference()

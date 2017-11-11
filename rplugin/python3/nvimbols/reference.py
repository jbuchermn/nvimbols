class Reference:
    def __init__(self, name, display_targets, display_sources):
        self.name = name
        self.display_sources = display_sources
        self.display_targets = display_targets
        self.requires_verification_from_both = False


TargetRef = Reference('references', 'Targets', 'Usages')
ParentRef = Reference('is_child_of', 'Parents', 'Children')
InheritanceRef = Reference('inherits_from', 'Supers', 'Subs')

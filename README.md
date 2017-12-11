# NVimbols

## Graph

The idea is to represent dependencies within a project (i. e. a call of a specific function, reference of a class or declaration of a field...) as a graph
whose nodes are called symbols. A symbol can be stuff like

* Declaration of a class, method, field
* Definition of a method
* Call of a method (this is a distinct symbol from the definition or declaration of the method)
* Reference of a variable

for example

```cpp
// Symbol: Declaration and definition of test
// Symbol: Declaration of a
// Symbol: Declaration of b
int test(int a, int b){
    // Symbol: Declaration of c
    int c;

    // Symbol: Reference of a
    // Symbol: Reference of b
    // Symbol: Reference of c
    c = a+b;

    // Symbol: Reference of c
    return c;
}
```

However, the specifics of how the symbols are defined is not fixed by NVimbols. Another way to symbolize the above code might be

```cpp
// Symbol: Declaration and defintion of test
int test(int a, int b){
    // Symbol: Declaration of c
    int c;

    // Symbol: Reference of c
    // Symbol: Reference of the declaration/defintion of test
    c = a+b;

    // Symbol: Reference of c
    return c;
}
```
Only the fact that source files consist of distinct locations (e. g. `main.cpp:111:10:111:15`, columns 10 through 14 on line 111 in main.cpp), which reference each other
in various ways, like:

* Call or usage
* Inheritance
* Children (e. g. method declaration of class declaration)

## Architecture

NVimbols is merely meant to streamline this concept, it is not in any way aware of the source code. This task is left to sources for specific languages. So,
upon moving the cursor in ViM, NVimbols will see if it knows a source for the filetype and ask that source to load the symbol at the current location. The source will then
load information like, whether this is a class declaration or a method reference, or whatever. NVimbols will also - if needed - ask the source to load locations
the symbol references (i. e. the declaration of a method) or that reference this symbol (i. e. usages of a method).

All the knowledge about what happens comes from the source, NVimbols is merely thought to provide a unified interface for sources to make this data available and provide
boiler-code for parallel loading of symbols and graph creation, jumping through the source code, interacting with Denite, ...

## Source API

```python
from nvimbols.source.base import Base

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = "RTags"
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']

    def load_symbol(self, params):
        wrapper = params['wrapper']

        symbol = rc_get_symbol_info(wrapper.location)

        if(symbol is None):
            wrapper.symbol.set(None)
        else:
            filename, start_line, start_col, end_line, end_col = get_location(symbol)

            wrapper.location.filename = filename
            wrapper.location.start_line = start_line
            wrapper.location.start_col = start_col
            wrapper.location.end_line = end_line
            wrapper.location.end_col = end_col

            wrapper.symbol.set(RTagsSymbol(symbol))
            if 'parent' in symbol:
                parent_location = SymbolLocation(*get_location(symbol['parent']))
                wrapper.source_of[ParentRef.name].set([self._graph.create_wrapper(parent_location)])

    def load_source_of(self, params):
        wrapper = params['wrapper']
        reference = params['reference']

        res = []
        full = True

        if(reference == TargetRef):
            res, full = self._find_references(wrapper.location, params['requested_level'] == LOADABLE_PREVIEW)
            res = [self._graph.create_wrapper(loc) for loc in res]

        elif(reference == InheritanceRef):
            supers, subs = rc_get_class_hierarchy(wrapper.location)
            for s in supers:
                res += [self._graph.create_wrapper(SymbolLocation(*s))]

        wrapper.source_of[reference.name].set(res, LOADABLE_FULL if full else LOADABLE_PREVIEW)

    def load_target_of(self, params):
        wrapper = params['wrapper']
        reference = params['reference']

        res = []
        full = True

        if(reference == TargetRef):
            res, full = self._find_referenced_by(wrapper.location, params['requested_level'] == LOADABLE_PREVIEW)
            res = [self._graph.create_wrapper(loc) for loc in res]

        elif(reference == InheritanceRef):
            supers, subs = rc_get_class_hierarchy(wrapper.location)
            for s in subs:
                res += [self._graph.create_wrapper(SymbolLocation(*s))]

        wrapper.target_of[reference.name].set(res, LOADABLE_FULL if full else LOADABLE_PREVIEW)
```


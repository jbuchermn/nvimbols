# NVimbols

# Graph

The idea is to represent dependencies within a project (i. e. a call of a specific function, reference of a
class or declaration of a field...) as a directed graph whose nodes are called symbols. A symbol can be stuff like

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

However, the specifics of how the symbols are defined is not fixed by NVimbols. Another way to symbolize
the above code might be

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
Only the fact that source files consist of distinct locations (e. g. `main.cpp:111:10:111:15`,
columns 10 through 14 on line 111 in main.cpp), which reference each other in various ways, like:

* Call or usage
* Inheritance
* Children (e. g. method declaration of class declaration)

# Architecture

NVimbols is merely meant to streamline this concept, it is not in any way aware of the source code.
This task is left to sources for specific languages. So, upon moving the cursor in ViM, NVimbols will see 
if it knows a source for the filetype and ask that source to load the symbol at the current location. 
The source will then load information like, whether this is a class declaration or a method reference, or whatever. 
NVimbols will also - if needed - ask the source to load locations the symbol references (i. e. the declaration
of a method) or that reference this symbol (i. e. usages of a method).

All the knowledge about what happens comes from the source, NVimbols is merely thought to provide a unified
interface for sources to make this data available and provide boilerplate-code for parallel loading of symbols
and graph creation, jumping through the source code, interacting with Denite, ...

# Specifications

## Basic classes

```py
class Location:
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None)
```

describes the location and extent of a symbol. end_col is not included. Serves as primary key for symbols.

```py
class Symbol:
    def __init__(self, location):
        self.location = location
        self.name = ""
        self.kind = ""

    def reference_to(self, reference, symbol)
    def reference_from(self, reference, symbol)
    def delete_reference(self, reference, symbol)
```

is the base class for all nodes in the graph (meant to be subclassed in the implementation of a Source). 
Name is a readable (non-unique) identifier, and kind some readable additional information. 
Both attributes are only used for rendering the symbol and do not impact the way NVimbols behaves. For example,
the declaration of a method `test` might result in a `Symbol(Location(...), "test", "Method Declaration")`.
Also, when providing a custom renderer, `name` and `kind` need not be set.

`reference_from` and `reference_to` attach an edge from or to `symbol`. These don't need to be called on both symbols.
References of the same class between the two same nodes are considered identical and will not be attached twice. The
reference (new or already existing) will be returned by `reference_from` and `reference_to`.

```py
class Reference:
    def __init__(self):
        self.name = ""
        self.display_targets = ""
        self.display_sources = ""

    def delete(self)
```

is the base class for all edges in the graph. `display_targets` is used when rendering the source of the reference, 
`display_sources` when rendering the target of the reference. NVimbols comes with three implementations of this:

- `TargetRefrence`: Most basic reference, e.g. a function call usually has an edge pointing to the function
  declaration.
- `ParentReference`: A method declaration points to the surrounding class declaration.
- `InheritanceReference`: An overridden method points to the method it overrides or a subclass to its superclass.

However, a source may create many more or choose not to support some of the above. Any newly created reference must
have a no arguments constructor.

```py
class Graph:
    def symbol(self, location, symbol=None)
    def empty(self, location)
```

is the main object. Any new symbol created by the source needs to be registered by calling `graph.symbol`. If the graph
already knows a symbol at this location, this method returns the old object and discards the new one, otherwise the new
one is registered. Calling the mthod with `symbol=None` can be used to query the graph, whether there is a symbol at
this location. In all cases the return value of `symbol` needs to be used!

Example:

```py
symbol = MySymbol(location, "test", "MethodDeclaration")
symbol = graph.symbol(symbol.location, symbol)

symbol.reference_to(...)
...
```

If the source knows, that at a given location there is no symbol (e.g. an empty line), it may notify the graph by
calling `graph.empty(Location(...))`. Then there will be no more requests regarding this location. Otherwise, NVimbols
will keep asking the source for the symbol at this location if the cursor is moved there.

## Source classes

All source need to derive from

```py
class Base:
    def __init__(self, ...):
        self._vim = ...
        ...

    @abstractmethod
    def request(self, req)

    def render(self, symbol)
    def render_denite(self, symbol)
```

`_vim` is the neovim object, used for example to retrieve configuration from `init.vim`. `render` and `render_denite` can
be overridden to provide custom rendering, however `request` is the core method any source must provide. The argument of
`request` is an object of the class `Request`.


### Constructor `__init__`

The neovim object is stored in `self._vim`. In the constructor a source is supposed to set its configuration:

- `self.name`: Name of the source,
- `self.filetypes`: ViM filetypes it supports. The source will not be called on files of other types,
- `self.references`: `Reference` classes the source supports
- `self.tasks`: Maximum number of different threads simultaneously calling methods on the source. Set to 1 for
   non-threadsafe sources.

### Method `request`

The argument `req` is of the class

```py
class Request:
    def __init__(...):
        self.graph = ...
        self.state = ...

    def fulfill(self)
```

`self.graph` is the `Graph` object to be changed by the request. `state` provides a way to preview certain information
(f. e. a class might be used in many places, but this might not be of interest. Instead we don't want to wait a
horrendous amount of time for the request to finish and preview this list of usages). `state` is an instance of the
enum

```py
class LoadableState(Enum):
    NOT_LOADED
    PREVIEW
    FULL
```

Each `Symbol` instance carries information about how much information has been loaded:

```py
class Symbol:
    ...
    state(self)
    state_source_of(self, reference_class)
    state_target_of(selfm reference_class)
    fulfill(self, state)
    fulfill_source_of(self, reference_class, state)
    fulfill_target_of(self, reference_class, state)
```

where `source_of` means edges of class `reference_class` that start at the symbol and `target_of` means edges that point
to the symbol. The symbol itself also is stateful, meaning that `name`, `kind` and similar information may not be
loaded. For example, when retrieving usages of a function, it might be convenient to simply create `Symbol`s that only
contain the location and fill in further information later (requests will be issued automatically).

Whenever the state changes (in the `Source.request` method) this must be notified by calling the corresponding `fulfill`
method. (Another way to do this is to call `req.fulfill()` which will call `Symbol.fulfill` with appropriate arguments.
Or even simpler, if `Source.request` returns `True`, `req.fulfill()` will be called automatically). However, if a source
loads more information than it is asked, which might be convenient if this information is readily available and will be
needed later anyway, the appropriate `fullfill` methods need to be called in order to prevent doubly loading the
information.

### Class `Request`

`Request` is an abstract class with three implementations which must be handled by the source (If requests are ignored
NVimbols will keep on requesting leading to massive resource usage):

- `LoadSymbolRequest`: Fill in `name`, `kind` and similar information,
- `LoadReferencesRequest`: Load references from or to the symbol,
- `LoadAllSymbolsInFileRequest`: Load all symbols of intrest (usually declarations) in a file.

### Class `LoadSymbolRequest`

### Class `LoadReferencesRequest`

### Class `LoadAllSymbolsInFileRequest`

### Custom rendering

Overriding `render` and/or `render_denite` can be used to implement custom rendering. See `Base` for a reference
implementation. This part of the API is not yet stable and might be moved from `Source` to `Symbol`.

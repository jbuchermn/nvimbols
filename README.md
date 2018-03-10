# NVimbols

## Graph

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

## Architecture

NVimbols is merely meant to streamline this concept, it is not in any way aware of the source code.
This task is left to sources for specific languages. So, upon moving the cursor in ViM, NVimbols will see 
if it knows a source for the filetype and ask that source to load the symbol at the current location. 
The source will then load information like, whether this is a class declaration or a method reference, or whatever. 
NVimbols will also - if needed - ask the source to load locations the symbol references (i. e. the declaration
of a method) or that reference this symbol (i. e. usages of a method).

All the knowledge about what happens comes from the source, NVimbols is merely thought to provide a unified
interface for sources to make this data available and provide boilerplate-code for parallel loading of symbols
and graph creation, jumping through the source code, interacting with Denite, ...

## Specifications

### Basic classes

```py
class SymbolLocation:
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None)
```

describes the location and extent of a symbol. end_col is not included. Serves as primary key for symbols.

```py
class Symbol:
    def __init__(self, name, kind)
```

is the base class for all nodes in the graph (meant to be subclassed in the implementation of a Source). 
Name is a readable (non-unique) identifier, and kind some readable additional information. 
Both attributes are only used for rendering the symbol and do not impact the way NVimbols behaves. For example,
the declaration of a method `test` might have result in a `Symbol("test", "Method Declaration")`

```py
class Reference:
    def __init__(self, from_symbol, to_symbol)
```

is the base class for all edges in the graph. NVimbols comes with three implementations of this:

- `TargetRefrence`: Most basic reference, e.g. a function call usually has an edged pointed to the function
  declaration.
- `ParentReference`: A method declaration points to the surrounding class declaration.
- `InheritanceReference`: An overridden method points to the method it overrides or a subclass to its superclass.

However, a source may create many more or choose not to support some of the above.

### Source classes

All source need to derive from

```py
class Base:
    def __init__(self, vim)

    @abstractmethod
    def load_symbol(self, params)

    @abstractmethod
    def load_source_of(self, params)

    @abstractmethod
    def load_target_of(self, params)

    def render(self, wrapper)
    def render_denite(self, wrapper)
```

`vim` is the neovim object, used for example to retrieve configuration from `init.vim`.

#### Constructor

`vim` will be stored in `self._vim`. In the constructor a source is supposed to set its configuration:

- `self.name`: Name of the source,
- `self.filetypes`: ViM filetypes it supports. The source will not be called on files of other types,
- `self.references`: `Reference` instances the source supports
- `self.tasks`: Maximum number of different threads simultaneously calling methods on the source. Set to 1 for
   non-threadsafe sources.



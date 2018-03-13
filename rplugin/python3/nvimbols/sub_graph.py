from nvimbols.base_graph import BaseGraph


class SubGraph(BaseGraph):
    def __init__(self, graph, include_node):
        super().__init__()

        self._graph = graph
        self._include_node = include_node

    """
    BaseGraph functionality
    """

    def nodes(self):
        return [n for n in self._graph.nodes() if self._include_node(n)]

    def edge_classes(self):
        return self._graph.edge_classes()

    def source_of(self, node, edge_class):
        return [n for n in self._graph.source_of(node, edge_class) if self._include_node(n)]

    def target_of(self, node, edge_class):
        return [n for n in self._graph.target_of(node, edge_class) if self._include_node(n)]

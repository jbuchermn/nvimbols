from abc import abstractmethod


class BaseGraph:
    """
    A directed graph in the mathematical sense. BaseGraph is always immutable.
    """

    @abstractmethod
    def nodes(self):
        """
        Return an iterable of all nodes in the graph
        """
        pass

    @abstractmethod
    def edge_classes(self):
        """
        Return an iterable of all types of edges in the graph. The type
        of the result is not determined, but it must be valid to pass it into
        the sources and targets method.
        """
        pass

    @abstractmethod
    def source_of(self, node, edge_class):
        """
        Return all nodes n, s. t. there exists an edge of type edge_class
        pointing from node to n.
        """
        pass

    @abstractmethod
    def target_of(self, node, edge_class):
        """
        Return all nodes n, s. t. there exists an edge of type edge_class
        pointing from n to node.
        """
        pass

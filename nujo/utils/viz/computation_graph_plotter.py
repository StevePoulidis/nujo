from graphviz import Digraph

from nujo.autodiff.node import Node
from nujo.autodiff.tensor import Tensor


class ComputationGraphPlotter:
    ''' Computation Graph Plotter

        Uses graphviz.

    '''
    def __init__(self, **kwargs):
        self.computation_graph = Digraph(**kwargs)

    @staticmethod
    def get_color(node) -> str:
        if isinstance(node, Tensor):
            if len(node.children) > 0:
                return 'lightblue'
            return 'indianred1'
        else:
            return 'gray'

    @staticmethod
    def get_shape(node) -> str:
        if isinstance(node, Tensor) and len(node.children) == 0:
            return 'box'
        else:
            return 'oval'

    def create(self, root: Node) -> 'ComputationGraphPlotter':
        if len(root.children) == 0:
            return

        for child in root.children:
            self.computation_graph.node(str(child),
                                        color=self.get_color(child),
                                        shape=self.get_shape(child),
                                        style='filled')

            self.computation_graph.node(str(root),
                                        color=self.get_color(root),
                                        shape=self.get_shape(root),
                                        style='filled')

            self.computation_graph.edge(str(child), str(root))
            self.create(child)

        return self

    def view(self) -> None:
        self.computation_graph.view()

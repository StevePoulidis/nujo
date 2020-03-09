from abc import abstractmethod
from numbers import Number
from typing import Union

from numpy import array, ndarray

from nujo.autodiff.modes import DIFF_ENABLED
from nujo.autodiff.node import Node
from nujo.autodiff.tensor import Tensor


class Function(Node):
    ''' Base Class for functions

    Functions are applied to tensors.

    A Function takes multiple tensors as input
    and produces only one tensor as output.

    Functions do not change tensors in-place.

    Parameters:
    -----------
    children : varargs, the inpute tensors
    name : string, the name of the function

    '''
    def __init__(self, *children: Tensor, name='<Function>') -> None:
        super(Function, self).__init__(*children, name=name)

    def _generate_tensor_name(self) -> str:
        return f'Z:{self.id}{self.name}'

    @abstractmethod
    def forward(self) -> Union[Number, ndarray, Tensor]:
        pass

    @abstractmethod
    def backward(self) -> Union[Number, ndarray, Tensor]:
        pass

    def __call__(self) -> Tensor:
        z = self.forward()
        if not isinstance(z, Tensor):
            z = Tensor(z, children=[self], name=self._generate_tensor_name())

        if DIFF_ENABLED:
            for tensor, derivative in zip(self.children, self.backward()):
                tensor.add_grad_dependency(z, array(derivative))

        return z

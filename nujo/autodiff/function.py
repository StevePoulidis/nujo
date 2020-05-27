from abc import abstractmethod
from numbers import Number
from typing import Any, Dict, List, TypeVar, Union

from numpy import ndarray

import nujo.autodiff.modes as modes
from nujo.autodiff._node import _Node
from nujo.autodiff.tensor import Tensor


class Function(_Node, object):
    ''' Base Class for functions

    Functions are applied to tensors. They take multiple
    tensors as input and produces only one tensor as output.
    They do NOT change tensors in-place.

    Functions were also written so they reuse the input/output tensors
    when possible, which results in the computation graph being:
     - "Dynamically defined, statically evaluated."
    taking the best from both worlds.

    Parameters:
    -----------
     - children : varargs, the inpute tensors
     - name : string, the name of the function

    '''

    _func_children_lookup_cache: Dict[str, 'Function'] = {}
    ''' Cache used to lookup for functions that may have already been defined
    in the computation graph.

     - key : str(hash(FuncType)) + str(hash(children))
     - value : the already defined function which will be reused

    '''

    _cache_hit = False
    ''' Flag signaling cache hit/miss.
    '''

    T = TypeVar('T', Tensor, ndarray)

    def __init__(self,
                 *children: Union[Tensor, ndarray, List[Number], Number],
                 name='Function'):

        if self._cache_hit:
            return

        super(Function, self).__init__(*Function._parse_inputs(children),
                                       name=name)

        # This output placeholder is reused when possible
        self._output_placeholder = Tensor(
            None,
            diff=any([x.diff for x in self.children]) and modes.DIFF_ENABLED,
            creator=self if modes.DIFF_ENABLED else None,
            name=self._generate_tensor_name())

        if modes.DIFF_ENABLED:  # If graph building is enabled.
            # Allocate space for parent's output (output placeholder)
            for child in self.children:
                child.parents_outputs.append(self._output_placeholder)

    def __new__(cls, *children: Union[Tensor, ndarray, List[Number], Number],
                **kwargs):
        ''' Used to lookup the cache for an already defined function of
        the current type using the current `children` as arguments. If a
        function satisfying this requirements could not be found, a new
        function is created and added to the cache, in order to be later
        potentially reused.

        '''

        # Only cache functions that are in the computation graph
        if modes.DIFF_ENABLED:
            key = str(hash(cls))  # Inlcude the function type hash in the key
            # Include the arguments' (inputs/children) identifiers in the key
            key += ''.join((str(x.id) if isinstance(x, Tensor) else str(x)
                            for x in children))

            if key in cls._func_children_lookup_cache:
                cls._cache_hit = True
                return cls._func_children_lookup_cache[key]

            else:
                cls._cache_hit = False
                func = super(Function, cls).__new__(cls)
                cls._func_children_lookup_cache[key] = func
                return func

        # If the functions are not in the computation graph,
        # perform standard python init.
        else:
            cls._cache_hit = False
            return super(Function, cls).__new__(cls)

    @classmethod
    def _parse_inputs(cls, inputs: List[Any]) -> List[Tensor]:
        ''' Parse all inputs that are not Nodes to Tensors '''

        return [
            x if isinstance(x, _Node) else Tensor(x, name=str(x))
            for x in inputs
        ]

    def __repr__(self):
        return super(Function, self).__repr__() + f'#{self.id}'

    def _generate_tensor_name(self) -> str:
        return 'Z' + self.__repr__()

    @abstractmethod
    def forward(self) -> ndarray:
        ''' Implement forward pass of the function here.

        Use the `self.children` list to access the inputs.
        '''

        pass

    @abstractmethod
    def backward(self, idx: int, acumm_grad: T) -> T:
        ''' Implement backward pass of the function here

        Compute the gradient of children[idx] w.r.t. output of the
        computation graph from the acummulated gradient (the gradient
        of the output of the function w.r.t. the output of the graph).

        Parameters:
        -----------
        - idx : int, the index of the children for which to compute the
         gradient w.r.t. output of the computation graph
        - acumm_grad : T (Tensor or ndarray), the accumulated grad in the graph
         so far, you can otherwise think of it as the gradient of the output of
         the function w.r.t. the output of the graph.

            - `acumm_grad` is Tensor if differentiantion is enabled
             (`DIFF_ENABLED`) and the children has opted for differentiation
             (`diff` is True), thus the computations will be recorded in the
             computation graph and higher-order derivatives could be computed.
            - otherwise, `acumm_grad` is ndarray and the computations are not
             recorded; ndarrays are used since the computations with them are
             more efficient.

        Returns:
        --------
        - grad : T (Tensor or ndarray), the computed gradient of
         `self.children[idx]`

        '''

        pass

    def __call__(self) -> Tensor:
        ''' Executes cached forward pass
        '''

        # Forward pass
        self._output_placeholder.value = self.forward()
        return self._output_placeholder

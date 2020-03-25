''' More details here:
    https://ml-cheatsheet.readthedocs.io/en/latest/loss_functions.html
'''

from numpy import clip

from nujo.autodiff.tensor import Tensor
from nujo.flow import Flow
from nujo.math import abs, log, mean, sum

__all__ = [
    'Loss',
    'L1Loss',
    'L2Loss',
    'BinaryCrossEntropy',
    'CrossEntropy',
]

# ====================================================================================================


class Loss(Flow):
    ''' Base loss class
    '''
    def __init__(self, dim: int = None, keepdim=False, reduction: str = None):
        super(Loss, self).__init__(name=self.__class__.__name__)
        self.dim = dim
        self.keepdim = keepdim
        self.reduction_fn = mean if reduction == 'mean' else sum


# ====================================================================================================


class L1Loss(Loss):
    ''' L1 loss (or Mean Absolute Error)
    '''
    def __init__(self, dim: int = None, keepdim=False, reduction='mean'):
        super(L1Loss, self).__init__(dim, keepdim, reduction)

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        return self.reduction_fn(abs(input - target),
                                 dim=self.dim,
                                 keepdim=self.keepdim)


# ====================================================================================================


class L2Loss(Loss):
    ''' L2 loss (or Mean Squared Error)
    '''
    def __init__(self, dim: int = None, keepdim=False, reduction='mean'):
        super(L2Loss, self).__init__(dim, keepdim, reduction)

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        return self.reduction_fn((input - target)**2,
                                 dim=self.dim,
                                 keepdim=self.keepdim)


# ====================================================================================================


class BinaryCrossEntropy(Loss):
    ''' Binary Cross-Entropy loss

        −(y * log(p) + (1−y) * log(1 − p))

    '''
    def __init__(self, dim: int = None, keepdim=False, reduction='sum'):
        super(BinaryCrossEntropy, self).__init__(dim, keepdim, reduction)

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        # Avoid division by zero
        input.value = clip(input.value, 1e-16, 1 - 1e-16)
        return self.reduction_fn(-target * log(input) -
                                 (1 - target) * log(1 - input),
                                 dim=self.dim,
                                 keepdim=self.keepdim)


# ====================================================================================================


class CrossEntropy(Loss):
    ''' Multi-class Cross-Entropy loss
    '''
    def __init__(self, dim: int = None, keepdim=False, reduction='sum'):
        super(CrossEntropy, self).__init__(dim, keepdim, reduction)

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        # Avoid division by zero
        input.value = clip(input.value, 1e-16, 1 - 1e-16)
        return -self.reduction_fn(sum(target * log(input), dim=1),
                                  dim=self.dim,
                                  keepdim=self.keepdim)


# ====================================================================================================

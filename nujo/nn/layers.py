from functools import lru_cache
from typing import Tuple, Union

from nujo.autodiff._functions._transform import _Im2col, _Pad
from nujo.autodiff.tensor import Tensor
from nujo.flow import Flow
from nujo.init.random import randn

__all__ = [
    'Linear',
    'Conv2d',
]

# ====================================================================================================


class Linear(Flow):
    ''' Linear Layer

        f(x) = Wx + b

    Parameters:
    -----------
     - in_features : int, dim of input variables
     - out_features : int, wanted dim of output variables
     - bias : bool, whether to train a bias term or no
     - name : string, identifier for the current layer

    '''
    def __init__(self,
                 in_features: int,
                 out_features: int,
                 bias=True,
                 name='Linear'):

        super(Linear,
              self).__init__(name=f'{name}({in_features}, {out_features})')

        self.in_features = in_features
        self.out_features = out_features
        self.bias = bias

        self.W = randn(self.out_features,
                       self.in_features,
                       name=self.name + '.W')

        if self.bias:
            self.b = randn(self.out_features, 1, name=self.name + '.bias')

    def forward(self, x: Tensor) -> Tensor:
        out = self.W @ x
        return out + self.b if self.bias else out


# ====================================================================================================


class Conv2d(Flow):
    ''' A 2-dimensional convolutional layer

    Applies a 2D convolution over an input signal composed of
    several input planes.
    More info: https://cs231n.github.io/convolutional-networks/

    Parameters:
    -----------
     - in_channels : int, number of channels in the input image
     - out_channels : int, number of channels produced by the convolution
        (in other word, the number of kernels)
     - kernel_size : int or tuple, size of the convolving kernel
     - stride : int or tuple, optional, stride of the convolution. Default: 1
     - padding : int or tuple, optional, zero-padding added to both sides of
        the input. Default: 0
     - dilation : int or tuple, optional - spacing between kernel elements.
        Default: 0
     - bias : bool, optional, if True, adds a learnable bias to the output.
        Default: True
     - name : string, identifier for the current layer

    '''
    def __init__(self,
                 in_channels: int,
                 out_channels: int,
                 kernel_size: Union[int, Tuple[int, int]],
                 stride: Union[int, Tuple[int, int]] = 1,
                 padding: Union[int, Tuple[int, int]] = 0,
                 dilation: Union[int, Tuple[int, int]] = 0,
                 bias=True,
                 name='Conv2d'):

        super(Conv2d,
              self).__init__(name=f'{name}({in_channels}, {out_channels})')

        self.in_channels = in_channels
        self.out_channels = out_channels

        self.kernel_size = kernel_size if isinstance(
            kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding,
                                                                   padding)

        # Not used for now
        self.dilation = dilation if isinstance(dilation, tuple) else (dilation,
                                                                      dilation)

        self.bias = bias

        # Define trainable parameters

        self.kernels = randn(self.out_channels,
                             self.in_channels,
                             *self.kernel_size,
                             name=self.name + '.kernels')

        if self.bias:
            self.b = randn(self.out_channels, 1, name=self.name + '.bias')

    def forward(self, x: Tensor) -> Tensor:
        batch_size, channels, height, width = x.shape
        assert channels == self.in_channels

        # Apply padding
        x_padded = _Pad(x, self.padding)()

        # Apply the kernels
        x_col = _Im2col(x_padded, self.kernel_size, self.stride)()
        kernels_col = self.kernels.reshape(self.out_channels, -1)
        out_col = kernels_col @ x_col
        if self.bias:
            out_col += self.b

        # Reshape
        output_shape = self.get_output_shape(height, width)

        return out_col.reshape(*output_shape, batch_size)\
            .transpose(3, 0, 1, 2)

    @lru_cache(maxsize=64)
    def get_output_shape(self, height: int,
                         width: int) -> Tuple[int, int, int]:
        ''' Cached output shape calculation
        '''

        return (
            self.out_channels,
            ((height + self.padding[0] * 2 - self.kernel_size[0]) //
             self.stride[0]) + 1,
            ((width + self.padding[1] * 2 - self.kernel_size[1]) //
             self.stride[1]) + 1,
        )


# ====================================================================================================

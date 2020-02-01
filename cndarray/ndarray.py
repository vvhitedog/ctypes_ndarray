import ctypes as ct
from numpy.ctypeslib import ndpointer
import numpy as np

##############################################################################################
# #
# #            NdArray data marshaling
# #
##############################################################################################
##############################################################################################


__all__ = ['NdArray','allocator_type']


allocator_type = ct.CFUNCTYPE(ct.c_char_p, ct.c_size_t, )


def as_ctypes(obj):
    """Create and return a ctypes object from a numpy array.  Actually
    anything that exposes the __array_interface__ is accepted."""
    """
    XXX: Note I have to hack this because of a regression in a certain numpy version
    which can be read about here:
    https://github.com/numpy/numpy/issues/14214
    """
    from numpy.ctypeslib import _ctype_ndarray, as_ctypes_type
    ai = obj.__array_interface__
    if ai["strides"]:
        raise TypeError("strided arrays not supported")
    if ai["version"] != 3:
        raise TypeError("only __array_interface__ version 3 supported")
    addr, readonly = ai["data"]
    if readonly:
        raise TypeError("readonly arrays unsupported")
    # This is the issue (can't use dtype as it's limited to 32-bit):
    #dtype = _dtype((ai["typestr"], ai["shape"]))
    #result = as_ctypes_type(dtype).from_address(addr)
    # This is the replacement:
    ctype_scalar = as_ctypes_type(ai["typestr"])
    result = _ctype_ndarray(ctype_scalar, ai["shape"]).from_address(addr)
    result.__keep = obj
    return result

class NdArray(ct.Structure):
    """NdArray is a simple interface to using numpy ndarrays in C or C++ code."""


    _fields_ = [('m_data', ct.POINTER(ct.c_char)),
                ('m_ndim', ct.c_int),
                ('m_shape', ct.POINTER(ct.c_uint64)),
                ('m_sizeofdtype', ct.c_int),
                ('m_alloc', allocator_type),
                ]


    def __init__(self, shape=None, dtype='float64', maxdims=256):
        """
        Parameters
        ----------
        shape : tuple
            The shape of the array, if None, array can be resized in the future.
        dtype : str
            The datatype of the array, all numpy dtypes are supported.
        maxdims : int, optional
            The maximum number of dims allowed when creating an array.

        """

        self.arr = None
        self.dtype = dtype

        def allocator(nbytes):
            ret = np.zeros((nbytes,), dtype='u1')
            self.arr = ret
            return ct.addressof(as_ctypes(ret))

        aparam = allocator_type(allocator)
        self.m_sizeofdtype = np.dtype(dtype).itemsize
        if shape is None:
            # delay allocation until shape is known (in C++ or C code)
            self.np_shape = np.zeros(maxdims, dtype='uint64')
            ndim = 0
        else:
            # allocate right away if shape is known
            self.np_shape = shape.astype('uint64')
            ndim = len(shape)
            nbytes = np.prod(shape) * self.m_sizeofdtype
            ret = np.zeros((nbytes,), dtype='u1')
            self.arr = ret
            self.m_data = ct.addressof(as_ctypes(ret))

        shape = np.ctypeslib.as_ctypes(self.np_shape)
        self.m_ndim = ndim
        self.m_shape = shape
        self.m_alloc = aparam


    def asarray(self):
        """
        Returns
        -------
        arr: ndarray
            The numpy array of the type and shape specified when constructing.
        """
        ndim = self.m_ndim
        shape = self.np_shape[:ndim]
        return self.arr.view(self.dtype).reshape(shape).squeeze()


##############################################################################################
##############################################################################################

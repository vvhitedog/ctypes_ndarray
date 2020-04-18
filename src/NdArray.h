#ifndef CNDARRAY_H
#define CNDARRAY_H

#include <cstddef>
#include <cstdint>
#include <cstring>

//////////////////////////////////////////////////////////////////////////////////////////////
//
//            Ctypes NdArray Definitions
//
//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

extern "C" {

typedef char* NumpyAllocator(size_t nbytes);
typedef void SetDtypeFunc (const char *newdtype);

struct NdArray {
	char *m_data;
	int m_ndim;
	uint64_t *m_shape;
	int m_sizeofdtype;
	NumpyAllocator *m_alloc;
	NumpyAllocator *m_realloc;
  SetDtypeFunc *m_set_dtype;
  char *m_dtype;
};

}

//////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////
//
//            Common Ctypes NdArray Functionality
//
//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

void inline ndarray_set_size(NdArray* arr, uint64_t dim0, uint64_t dim1) {
	arr->m_ndim = 2;
	arr->m_shape[0] = dim0;
	arr->m_shape[1] = dim1;
}

void inline ndarray_set_size(NdArray* arr, uint64_t dim0, uint64_t dim1, uint64_t dim2) {
	arr->m_ndim = 3;
	arr->m_shape[0] = dim0;
	arr->m_shape[1] = dim1;
	arr->m_shape[2] = dim2;
}

void inline ndarray_set_size(NdArray* arr, int ndim, uint64_t* dims) {
	arr->m_ndim = ndim;
	for ( int idim = 0; idim < ndim; ++idim ) {
		uint64_t dim = dims[idim];
		arr->m_shape[idim] = dim;
	}
}

void inline ndarray_set_dtype(NdArray* arr, const char *dtype ) {
  arr->m_set_dtype(dtype);
}

void inline ndarray_alloc(NdArray* arr) {
	size_t nelem = 1;
	for (int i = 0; i < arr->m_ndim; ++i) {
		nelem *= arr->m_shape[i];
	}
	arr->m_data = arr->m_alloc(arr->m_sizeofdtype * nelem);
}

//////////////////////////////////////////////////////////////////////////////////////////////

#endif // CNDARRAY_H

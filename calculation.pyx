# cython: language_level=3
# cython: nonecheck=False

import numpy as np

cimport cython
cimport numpy as cnp
from libc.math cimport hypot, atan2   
from cython.parallel import prange

cdef extern from *:
	void __atomic_fetch_or(void *ptr, int val, int memorder) nogil

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef inline void process_ray(cnp.int16_t n, cnp.int16_t m,
								cnp.int16_t start_x, cnp.int16_t start_y,
								cnp.int16_t[:,:] heights, cnp.int16_t scale,
								cnp.float64_t cos_a,
								cnp.float64_t sin_a,
								cnp.npy_bool[:,:] visibility) noexcept nogil:
		cdef cnp.int16_t start_height = heights[start_x, start_y]
		cdef int r, x, y, dx, dy
		cdef double max_angle, angle, dist, dh
		max_angle = -1e99
		r = 1
		while True:
			x = start_x + <int>(r * cos_a)
			y = start_y + <int>(r * sin_a)
			
			if x < 0 or x >= n or y < 0 or y >= m:
				break
				
			if x == start_x and y == start_y:
				r += 1
				continue
			
			dx = x - start_x
			dy = y - start_y
			dist = hypot(<double>dx, <double>dy)
			dh = heights[x, y] - start_height
			angle = dh/dist
			#angle = atan2(<double>(heights[x, y] - start_height), dist)
			if angle > max_angle:
				visibility[x, y] = 1
				max_angle = angle
			
			r += 1
	
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void compute_visibility_mv(cnp.int16_t n, cnp.int16_t m,
								cnp.int16_t start_x, cnp.int16_t start_y,
								cnp.int16_t[:,:] heights, cnp.int16_t scale,
								cnp.float64_t[:] cos_vals,
								cnp.float64_t[:] sin_vals,
								cnp.npy_bool[:,:] visibility) noexcept nogil:
	cdef int alpha_idx
	for alpha_idx in prange(scale, nogil=True, schedule='guided', num_threads=16, chunksize=225):
		process_ray(n, m, start_x, start_y, heights, scale,
			cos_vals[alpha_idx], sin_vals[alpha_idx], visibility)

cpdef cnp.ndarray[cnp.npy_bool] compute_visibility_cyt(int n_, int m_,
										int start_x_, int start_y_,
										cnp.ndarray[cnp.int16_t, ndim=2] heights,
										int scale_):
	cdef cnp.int16_t n = n_, m = m_, start_x = start_x_, start_y = start_y_, scale = scale_
	cdef cnp.ndarray[cnp.npy_bool, ndim=2] visibility = np.zeros((n, m), dtype=bool)
	cdef cnp.ndarray[cnp.float64_t, ndim=1] angles = np.linspace(0, 2 * np.pi, scale_, endpoint=False)
	cdef cnp.ndarray[cnp.float64_t, ndim=1] cos_vals = np.cos(angles)
	cdef cnp.ndarray[cnp.float64_t, ndim=1] sin_vals = np.sin(angles)

	cdef cnp.int16_t[:,:] heights_mv = heights
	cdef cnp.npy_bool[:,:] visibility_mv = visibility
	cdef cnp.float64_t[:] cos_vals_mv = cos_vals
	cdef cnp.float64_t[:] sin_vals_mv = sin_vals

	compute_visibility_mv(n, m, start_x, start_y, heights_mv, scale,
						  cos_vals_mv, sin_vals_mv, visibility_mv)
	return visibility
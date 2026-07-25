import numpy as np
import math
def generate_random_heights(n: int, m: int) -> np.ndarray:
    return np.random.randint(1, 101, size=(n, m), dtype=np.int16)

def compute_visibility(n: int, m: int, start_x: int, start_y: int,
                       heights: np.ndarray, scale: int = 360) -> np.ndarray:
    visibility = np.zeros((n, m), dtype=bool)
    start_height = heights[start_x, start_y]

    angles = np.linspace(0, 2 * np.pi, scale, endpoint=False)
    cos_vals = np.cos(angles)
    sin_vals = np.sin(angles)

    for alpha_idx in range(scale):
        cos_a = cos_vals[alpha_idx]
        sin_a = sin_vals[alpha_idx]
        r = 1
        max_angle = -np.inf

        while True:
            x = start_x + int(r * cos_a)
            y = start_y + int(r * sin_a)

            if x < 0 or x >= n or y < 0 or y >= m:
                break

            # Пропускаем начальную точку
            if x == start_x and y == start_y:
                r += 1
                continue

            dx = x - start_x
            dy = y - start_y
            dist = math.hypot(dx, dy)
            h = heights[x, y]
            angle = math.atan2(h - start_height, dist)

            if angle > max_angle:
                visibility[x, y] = True
                max_angle = angle

            r += 1

    return visibility
import pyximport
import sys
if sys.platform == 'win32':
    extra_compile_args = ['/openmp']
    extra_link_args = []   # /openmp automatically links vcomp140.lib
else:
    extra_compile_args = ['-fopenmp']
    extra_link_args = ['-fopenmp']

pyximport.install(
    setup_args={
        "include_dirs": [np.get_include()],
        "extra_compile_args": extra_compile_args,
        "extra_link_args": extra_link_args,
    }
)
import calculation as calc
def compute_visibility_cyt(n: int, m: int, start_x: int, start_y: int,
                       heights: np.ndarray, scale: int = 360):
    return calc.compute_visibility_cyt(n, m, start_x, start_y, heights, scale)
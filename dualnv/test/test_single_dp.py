"""
SOME simple tests
@author: c. zhang
"""
import json
import pyrp.pydp as py
import pyrp.model_single_dp as purepy
import pyrp.model_single as mip
import sys
import numpy as np
import time

TEST_DIR = 'test'

if __name__ == '__main__':
    size = int(sys.argv[1])

    problem = json.load(open(f"{TEST_DIR}/test_{size}.json", 'rb'))
    T = problem['T'][:size]
    I = problem['I']
    _I_size = len(I)
    c1 = -10 + 8 * np.random.random(size=size)
    a_arr = py.convert_to_c_arr(_I_size, problem['a'])
    b_arr = py.convert_to_c_arr(_I_size, problem['b'])
    tau_arr = py.convert_to_c_arr_int(_I_size, problem['tau'])
    s_arr = py.convert_to_c_arr(_I_size, problem['s0'])
    c_arr = py.convert_to_c_arr(size, c1)

    # single
    idx = 0
    s0 = problem['s0'][idx]
    a = problem['a'][idx]
    b = problem['b'][idx]
    L = problem['L']
    tau = problem['tau'][idx]

    print(
        f"problem size: {size}\n")

    start = time.time()

    sol = py.run_dp_single(c_arr, size, a, b, L, tau, s0, _print=True, truncate=True)
    val, solution = sol[-1], np.array(sol[:-1]).reshape((2, -1))
    end_cpp = time.time()

    print(
        f"problem size: {size}\n"
        f"cpp-dp  used: {end_cpp - start:.2f}\n"
    )

    best_v, best_p, *_ = mip.single_mip(problem, size, c1, idx)
    print(best_v)
    print(best_p)
    end_mip = time.time()
    print(
        f"problem size: {size}\n"
        f"MIP  used: {end_mip - end_cpp:.2f}\n"
    )

    best_v1, best_p1, *_ = purepy.single_dp(problem, size, c1, idx)
    print(best_v1)
    print(best_p1)
    end_purepy = time.time()
    print(
        f"problem size: {size}\n"
        f"purepy  used: {end_purepy - end_mip:.2f}\n"

    )

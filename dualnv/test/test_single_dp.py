"""
SOME simple tests
@author: c. zhang
"""
import json
import pyrp.pydp as py
import pyrp.model_single_dp as purepy
import sys
import numpy as np
import time

TEST_DIR = 'test'

if __name__ == '__main__':
    idx = 0
    size = int(sys.argv[1])

    problem = json.load(open(f"{TEST_DIR}/test_{size}.json", 'rb'))
    s0 = problem['s0'][idx]
    a = problem['a'][idx]
    b = problem['b'][idx]
    L = problem['L']
    tau = problem['tau'][idx]
    T = problem['T'][:size]
    c1 = -10 + 8 * np.random.random(size=size)
    print(
    f"problem size: {size}\n")
    
    start = time.time()
    c_arr = py.double_array(size)
    for i in range(size):
        c_arr[i] = c1[i]
    sol = py.run_dp_single(c_arr, size, a, b, L, tau, s0, _print=True, truncate=True)
    val, solution = sol[-1], np.array(sol[:-1]).reshape((2, -1))
    end_cpp = time.time()

    print(
        f"problem size: {size}\n"
        f"cpp-dp  used: {end_cpp - start:.2f}\n"
    )


    best_v1, best_p1, *_ = purepy.single_dp(problem, size, c1, idx)
    print(best_v1)
    print(best_p1)
    end_purepy = time.time()
    print(
        f"problem size: {size}\n"
        f"purepy  used: {end_purepy - end_cpp:.2f}\n"

    )
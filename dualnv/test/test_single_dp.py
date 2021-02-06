"""
SOME simple tests
@author: c. zhang
"""
import json
import pyrp.pydp as py
import pyrp.model_single_dp as purepy

TEST_DIR = 'test'

if __name__ == '__main__':
    idx = 1
    size = 20
    problem = json.load(open(f"{TEST_DIR}/test_large_{size}.json", 'rb'))
    s0 = problem['s0']
    a = problem['a'][idx]
    b = problem['b'][idx]
    L = problem['L']
    tau = problem['tau']
    T = problem['T'][:size]
    c1 = [-2.43732, -5.08001, -8.83009, -2.70797, -8.94776, -7.93972, -2.58655, -3.96225, -9.25911, -5.37123, -9.23084,
          -8.02637, -2.56384, -6.17786, -2.06662, -1.6506, -6.34907, -9.173, -4.36922, -6.49543]
    best_v1, best_p1, *_ = purepy.single_dp(problem, 20, c1, idx)
    print(best_v1)
    print(best_p1)
    c_arr = py.double_array(size)
    for i in range(size):
        c_arr[i] = c1[i]
    py.run_dp_single(c_arr, size, a, b, L, tau, s0, _print=True, truncate=True)

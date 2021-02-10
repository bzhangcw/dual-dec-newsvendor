# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /model.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:56:16 pm
# @description:

import logging
import sys
from collections import namedtuple

import pandas as pd

from .util import *

_logger = logging.getLogger("single.dp")
_logger.setLevel(logging.DEBUG)


def _cond(s1, s2):
    # do ->
    if s1.u == 1 and s2.m != 1:
        return True
    # idle
    if s1.m == 0 and s2.m != 1:
        return True
    # maintenance ready
    if s1.m == 1 and s2.m != 1:
        return True
    # under maintenance
    if s1.m == s2.m + 1:
        return True
    return False


Tail = namedtuple('p', field_names=['u', 'm', 's', 't'])


def single_dp(problem, nT, c, idx, u_target=None, x_target=None):
    s0 = problem['s0'][idx]
    a = problem['a'][idx]
    b = problem['b'][idx]
    L = problem['L']
    tau = problem['tau'][idx]
    T = problem['T'][:nT]

    # define the stage ~ action evaluation
    _bool_u = u_target is not None
    _bool_x = x_target is not None
    if _bool_u and _bool_x:
        ac_val = lambda u, x, t: abs(2 * (u - u_target[t]) * c[t]) \
                                 + abs((x - x_target[t]) * c[t])
    elif not _bool_u and not _bool_x:
        ac_val = lambda u, x, t: u * c[t]
    elif not _bool_u:
        ac_val = lambda u, x, t: abs((x - x_target[t]) * c[t]) + c[t] * u
    else:
        ac_val = lambda u, x, t: abs((u - u_target[t]) * c[t])

    tails_queue = []

    vals = dict()
    tails = dict()
    policy = dict()

    flags = [(1, 0)] + [(0, m) for m in range(0, tau + 1)]
    initials = [(1, 0, s0 - a, 0), (0, 0, s0, 0), (0, tau, s0, 0)]
    for u, m, s, t in initials:
        tails_queue.append(Tail(u, m, s, t))

    while tails_queue:
        pr = tails_queue[-1]
        _logger.debug(pr)
        if pr.t == nT - 1:
            # this is the final
            vals[pr.u, pr.m, pr.s, pr.t] = ac_val(pr.u, pr.m, pr.t)  # pr.u * c[pr.t]
            policy[pr.u, pr.m, pr.s, pr.t] = [pr]
            tails_queue.pop(-1)
            continue

        _tails = tails.get(pr, -1)

        if _tails != -1:
            # tail problems known
            pass
        else:
            # generate tail problems
            _tails = []
            for u, m in flags:
                # check life span violation
                _s = pr.s - a * u + b * int(pr.m == 1)
                if _s < L:
                    continue
                new_pr = Tail(u, m, _s, pr.t + 1)
                # check flag transition violation
                _bool_flag = _cond(pr, new_pr)
                if _bool_flag:
                    # lifespan & transition good :)
                    _tails.append(new_pr)
                    if new_pr not in vals:
                        # not solved
                        tails_queue.append(new_pr)

            tails[pr] = _tails
            continue

        # else, all tail problems has been solved
        #  do value eval
        try:
            _val = sorted(
                ((_tail_pr,
                  ac_val(pr.u, pr.m, pr.t) + vals[_tail_pr.u, _tail_pr.m, _tail_pr.s, _tail_pr.t]
                  ) for _tail_pr in _tails), key=lambda x: x[-1])[0]

            _best_child, _best_val = _val
            vals[pr.u, pr.m, pr.s, pr.t] = _best_val
            policy[pr.u, pr.m, pr.s, pr.t] = [pr] + policy[_best_child.u, _best_child.m, _best_child.s, _best_child.t]
        except:
            _logger.debug(f"invalid {pr}")
        tails_queue.pop(-1)

    vs = pd.Series(vals)

    # summarize
    best_s, best_v = min(((k, vs[k]) for k in initials), key=lambda x: x[-1])
    best_p = np.array([[pr.u, int(pr.m == 2), pr.s] for pr in policy[best_s]])
    return best_v, best_p


def test():
    import time

    TEST_DIR = 'test'
    start = time.time()
    problem = json.load(open(f"{TEST_DIR}/test.json", 'rb'))

    c = [[-0.5751079019436339, -0.026884933935354738, -0.7125255181905054, -0.10770288960149066,
          -0.5392229576522433, -0.23078240408226935, -0.6128866913345116, -0.2954506914149363,
          -0.48980848777558306, -0.41303183086466067],  # // 2.75
         [-0.7127880426437507, -0.5659706571481583, -0.4550456819963197, -0.4958330603215182,
          -0.4915044667753743, -0.46593208077888737, -0.7663454211766438, -0.2788126396413988,
          -0.056291269036947034, -0.4476142259600049],  # // 2.91
         [-0.09221111835216411, -0.7119915204805928, -0.05008315149821718, -0.060805373703190724,
          -0.9100117664910027, -0.7912614250104067, -0.25440552456677945, -0.7596541281026525,
          -0.1311693310130878, -0.1896127093580806],  # // 3.17
         [-0.950964750856392, -0.4154944318479806, -0.49231440714337793, -0.6421424832507828,
          -0.0542522335485478, -0.8453473896111343, -0.07653416889402609, -0.7997331172218721,
          -0.48645964251958385, -0.44671620871332085],  # // 3.60
         [-0.5597228619548954, -0.41248534223116784, -0.9746206013126346, -0.17545187065408596,
          -0.22512148925156905, -0.3217034035286185, -0.5818429443491299, -0.6022893435405621,
          -0.89940023010885, -0.6361390464933777],  # // 4.01
         ]

    for i in c:
        best_v1, best_p1, *_ = single_dp(problem, 10, i, 0)
        print(best_v1)

    problem = json.load(open(f"{TEST_DIR}/test_large_20.json", 'rb'))
    c1 = [-2.43732, -5.08001, -8.83009, -2.70797, -8.94776, -7.93972, -2.58655, -3.96225, -9.25911, -5.37123, -9.23084,
          -8.02637, -2.56384, -6.17786, -2.06662, -1.6506, -6.34907, -9.173, -4.36922, -6.49543]
    best_v1, best_p1, *_ = single_dp(problem, 20, c1, 0)
    print(best_v1)

    end = time.time()
    print(f"finished benchmark {end - start} seconds")
    for n in [20, 30, 50, 100, 200]:
        start = time.time()
        for i in range(10):
            c = np.random.random(size=n)
            problem = json.load(open(f"{TEST_DIR}/test_large_{n}.json", 'rb'))
            best_v1, best_p1, *_ = single_dp(problem, n, c, 0)
        end = time.time()
        print(f"finished large sample size := {n} in {end - start} seconds")


if __name__ == '__main__':
    test()

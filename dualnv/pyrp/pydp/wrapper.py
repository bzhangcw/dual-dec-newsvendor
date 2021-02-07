import numpy as np

from .pydp import *


def cppdp_single(c_arr, size, a, b, L, tau, s0, _print=False, truncate=True):
  sol = run_dp_single(c_arr, size, a, b, L, tau, s0, _print=_print, truncate=truncate)
  val, solution = sol[-1], np.array(sol[:-1]).reshape((3, -1)).T
  return val, solution

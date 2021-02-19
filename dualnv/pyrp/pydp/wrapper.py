import numpy as np

from .pydp import *


def convert_to_c_arr(size, lambda_k):
  c_arr = double_array_py(size)
  for i in range(size):
    c_arr[i] = lambda_k[i]

  return c_arr


def convert_to_c_arr_int(size, lambda_k):
  c_arr = int_array_py(size)
  for i in range(size):
    c_arr[i] = lambda_k[i]

  return c_arr


def cppdp_single(c_arr, size, a, b, L, tau, s0, _print=False, truncate=True):
  sol = run_dp_single(c_arr, size, a, b, L, tau, s0, _print=_print, truncate=truncate)
  val, solution = sol[-1], np.array(sol[:-1]).reshape((3, -1)).T.round(3)
  return val, solution


def cppdp_batch(i_size, c_arr, size, a, b, L, tau, s0, _print=False, truncate=True):
  sol = run_dp_batch(
    i_size,
    c_arr,
    size,
    a,
    b,
    L,
    tau,
    s0,
    _print=_print, truncate=truncate)
  arr = np.array(sol)
  val = arr[-i_size:]
  policy = arr[:-i_size].reshape(i_size, 3, -1).swapaxes(1,2)

  return val, policy

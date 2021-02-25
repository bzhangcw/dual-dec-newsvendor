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


def cppdp_single(lambda_k, c, size, a, b, L, tau, s0, _print=False, truncate=True):
  lambda_arr = convert_to_c_arr(size, lambda_k)
  sol = run_dp_single(lambda_arr, c, size, a, b, L, tau, s0, _print=_print, truncate=truncate)
  val, solution = sol[-1], np.array(sol[:-1]).reshape((3, -1)).T.round(3)
  return val, solution


def cppdp_batch(i_size, lambda_arr, c_arr, size, a, b, L, tau, s0, _print=False, truncate=True):

  sol = run_dp_batch(
    i_size,
    lambda_arr,
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

def test_phi_lambda(lambda_k, problem, scale):
  # ======================
  # DEBUG for phi(lambda)
  # ======================
  num_i = len(problem['I'])
  lambda_arr = convert_to_c_arr(scale, lambda_k.astype(float))
  a_arr = convert_to_c_arr(num_i, problem['a'])
  b_arr =  convert_to_c_arr(num_i, problem['b'])
  tau_arr =  convert_to_c_arr_int(num_i, problem['tau'])
  s_arr =  convert_to_c_arr(num_i, problem['s0'])
  c_arr = convert_to_c_arr(num_i, problem['c'].astype(float))
  _L = problem['L']
  sub_v_k, x_k = cppdp_batch(num_i, lambda_arr, c_arr, scale, a_arr, b_arr,
                 _L, tau_arr, s_arr, True, True)
  return sub_v_k, x_k
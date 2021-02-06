# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /model.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:56:16 pm
# @description:

import multiprocessing as mpc
import time
from collections import namedtuple
from .pydp import run_dp_single, double_array
from .model_single import single_mip
from .model_single_dp import single_dp
from .util import *
from .test import eval


# ===================
# PROJECTION METHODS
# ===================
def projection_box(x, lower, upper):
  """
  Simple projection onto box: [lower, upper]
  Args:
    ...
  Returns:
  """
  return np.minimum(np.maximum(x, lower), upper)


def multiplier_method(g_k, d_k, delta_k, gamma_k, lambda_b, projection_method, b, h, option='subgrad'):
  if option == 'cvx':
    _d = d_k
  elif option == 'subgrad':
    _d = g_k
  else:
    raise ValueError("no such method")

  step = 1 / (_d.dot(_d)) * delta_k * gamma_k
  lambda_k = lambda_b + step * _d
  lambda_k = projection_method(lambda_k, -b, h)
  return step, lambda_k


# ===================
# PARAM METHODS
# ===================
def alpha_method(gamma0, iteration, use_optimal, d, g):
  """
  alpha method update \gamma \alpha
    at start of iteration k
  iteration: note that iteration := k
    you should use d of last iteration
    and g of current
  """
  if not use_optimal:
    alp_k = 1 / iteration
    gamma_k = gamma0
    return alp_k, gamma_k

  # the optimal alpha_k by see (Brännlund 1995),
  #   Brännlund U (1995) A generalized subgradient method with relaxation step. Mathematical Programming 71(2):207–219.
  gd = g.dot(d)
  if iteration == 1 or gd > 0:
    return 1, 1
  dd = d.dot(d)
  alp_k = gamma_k = dd / (dd - gd)
  return alp_k, gamma_k


# ===================
# CONTAINERS
# ===================
class Sol:
  def __init__(self):
    self.primal_sol = []
    self.primal_val = []
    self.primal_k = []
    self.lb = []
    self.fc = {}


class Param:
  def __init__(self):
    self.use_maximum = False
    self.use_optimal = False


def convert_to_c_arr(size, lambda_k):
  print(lambda_k)
  c_arr = double_array(size)
  for i in range(size):
    c_arr[i] = lambda_k[i]

  return c_arr


def dualnv_subgradient(
    problem,
    scale,
    subproblem_method=single_dp,
    projection_method=projection_box,
    mp=True,
    pool=None,
    max_iteration=150,
    gap=0.01,
    r0=2,
    dual_option="max",
    hyper_option="simple",
    dir_option='subgrad',
    eps_step=1e-4,
    **kwargs):
  """[summary]
  The subgradient algorithm for the repair problem
  Args:
      subproblem_method (callable): the function for subproblem
      projection_method (callable): the function for projection of dual multipliers.
        Defaults to projection_box.
      **kwargs
  """
  _unused_ = kwargs
  h, b = problem['h'], problem['p']
  T = problem['T'][:scale]
  I = problem['I']
  D = problem['D'][:scale]
  numI = len(problem['I'])

  # extra evaluations
  funcs = kwargs.get('evals', [])

  st_sec = time.time()
  # solution
  sol = Sol()

  # algorithm options
  param = Param()
  param.use_maximum = dual_option == 'max'
  param.use_optimal = hyper_option != 'simple'
  param.use_cpp_dp = subproblem_method.__name__ == 'run_dp_single'
  param.direction = 'cvx' if dir_option == 'cvx' else 'subgrad'

  # ==================
  # INITIALIZATION
  # ==================
  # initial solution:
  #   do nothing and thus everything is short
  x_bar = i_bar = 0
  # primal dual bound
  z_bar = b * sum(D)
  phi_bar = -1e3
  # dual variable
  lambda_k = lambda_b = np.ones(scale) * h
  # hyper parameters
  improved = 0
  improved_eps = 30
  # initial direction
  d_k = 0
  # alpha & gamma
  alp_k = gamma_k = 1
  # iteration #
  k = 0
  fc_vals = {}
  for fc in funcs:
    fc_vals[fc] = []
  # ==================
  # MAIN ROUTINE
  # ==================
  while True:

    # ==================
    # solve \phi_k = \phi(\lambda_k)
    # ==================
    # solution keeper
    sub_v_k, x_k = np.zeros(numI), np.zeros((numI, scale, 3))

    # solve decomposable subproblems
    #   can use lazy multiprocessing
    if param.use_cpp_dp:
      c_arr = convert_to_c_arr(scale, lambda_k.astype(float))
      _s0 = problem['s0']
      _L = problem['L']
      _tau = problem['tau']
      if mp:
        results = []
        for idx, i in enumerate(I):
          _a = problem['a'][idx]
          _b = problem['b'][idx]
          r = pool.apply_async(
            subproblem_method,
            (c_arr, scale, _a, _b, _L, _tau, _s0, True, True)
          )
          results.append(r)
        for idx, r in enumerate(results):
          _best_v_i, _best_p_i, *_ = r.get()
          sub_v_k[idx] = _best_v_i
          x_k[idx, :, :] = _best_p_i
      else:
        for idx, i in enumerate(I):
          _a = problem['a'][idx]
          _b = problem['b'][idx]
          _best_v_i, _best_p_i, *_ = subproblem_method(c_arr, scale, _a, _b, _L, _tau, _s0, True, True)
          sub_v_k[idx] = _best_v_i
          x_k[idx, :, :] = _best_p_i
    else:
      if mp:
        results = [
          pool.apply_async(subproblem_method, (problem, scale, lambda_k, idx))
          for idx, i in enumerate(I)
        ]
        for idx, r in enumerate(results):
          _best_v_i, _best_p_i, *_ = r.get()
          sub_v_k[idx] = _best_v_i
          x_k[idx, :, :] = _best_p_i
      else:
        for idx, i in enumerate(I):
          _best_v_i, _best_p_i, *_ = subproblem_method(problem, scale, lambda_k, idx)
          sub_v_k[idx] = _best_v_i
          x_k[idx, :, :] = _best_p_i

    # eval \phi_k
    phi_k = np.inner(D, -lambda_k) + sub_v_k.sum()

    # =====================
    # subgradient computation
    # =====================
    i_k = x_k.sum(0)[:, 0]
    g_k = (i_k - D)

    # =====================
    # update direction params
    # =====================
    # hint: use k + 1 since k start from 0
    alp_k, gamma_k = alpha_method(gamma0=r0, iteration=k + 1, use_optimal=param.use_optimal, d=d_k, g=g_k)

    # =====================
    # compute direction
    # =====================
    # there are many ways to do this
    d_k = (1 - alp_k) * d_k + g_k * alp_k

    # =====================
    # the recovery algorithm
    # =====================
    #
    # update current primal
    #
    # This is an implied step,
    #  by this you actually use a "heuristic"
    #  since you retrieve a primal solution
    #  using g = U^T e - d
    #  and max{g, 0}, max{-g, 0} which are convex
    # calculate best primal
    surplus_idx_k = g_k > 0
    z_k = h * g_k[surplus_idx_k].sum(
      0) - b * g_k[~surplus_idx_k].sum(0)

    # calculate cvx (averaging primal heuristic)
    surplus_idx_bar = d_k > 0
    z_bar = h * d_k[surplus_idx_bar].sum(
      0) - b * d_k[~surplus_idx_bar].sum(0)

    # ================
    # test evaluations
    # ================
    _args = z_bar, lambda_k, d_k, g_k
    for fc in funcs:
      try:
        _func = getattr(eval, fc)
        _val = _func(*_args)
        print(f"{fc}@{k}: {_val}")
        fc_vals[fc].append(_val)
      except:
        print(f"no such method in {eval.__name__}")

    # =====================
    # update dual vars
    # =====================
    step, lambda_k = multiplier_method(g_k, d_k, z_bar - phi_k, gamma_k, lambda_b, projection_method, b, h,
                                       option=param.direction)

    # =====================
    # MAIN FINISHED
    # =====================

    # =====================
    # AUXILIARY START
    # the auxiliary steps
    # =====================
    #
    # dual value evaluation
    _bool_lb_updated = phi_k > phi_bar
    if _bool_lb_updated:
      phi_bar = phi_k
      lambda_b = lambda_k.copy()
      improved = 0
    else:
      improved += 1
      if improved >= improved_eps:
        r0 = r0 / 2
        improved = 0

    # update base "dual multipliers"
    # condition (phi_k > phi_bar) is only for the volume algorithm
    if not param.use_maximum or _bool_lb_updated:
      lambda_b = lambda_k.copy()

    gap_k = (z_bar - phi_bar) / abs(z_bar)

    print(
      f"k: {k} @dual: {phi_k:.2f}; @lb: {phi_bar:.2f}; @primal: {z_k:.2f}; @primal_bar: {z_bar:.2f}; @gap: {gap_k:.4f}\n"
      f"@stepsize: {step:.5f}; @norm: {np.abs(d_k).sum():.2f}; @alp: {alp_k:.4f}"
    )

    sol.primal_val.append(z_bar)
    sol.primal_k.append(z_k)
    sol.lb.append(phi_bar)
    sol.fc = fc_vals

    if k >= max_iteration or gap_k < gap or step < eps_step:
      x_bar = (1 - alp_k) * x_bar + x_k * alp_k
      i_bar = (1 - alp_k) * i_bar + i_k * alp_k
      sol.primal_sol = x_bar
      break

    # increment iteration
    k += 1

  finish_sec = time.time()
  total_runtime = finish_sec - st_sec
  if max_iteration:
    print(
      f"@summary: @k: {k}; @dual: {phi_k}; @primal: {z_bar}; @lb: {phi_bar}; @gap: {gap_k} @sec: {total_runtime}")
  return x_bar, i_bar, alp_k, z_bar, lambda_b, sol, total_runtime


def main(problem, **kwargs):
  print(f"THE SUBGRADIENT OPTIMIZATION ARGUMENTS:\n{kwargs}")
  mp_num = kwargs.get('mp_num', 8)
  subproblem_alg = kwargs.get('subproblem_alg')
  if subproblem_alg is not None:
    print(subproblem_alg.__name__)
    subproblem_method = subproblem_alg
  else:
    subproblem_alg_name = kwargs.get('subproblem_alg_name', 'dp')
    # query subproblem algorithm
    if subproblem_alg_name == 'mip':
      # use mip
      subproblem_method = single_mip
    elif subproblem_alg_name == 'purepydp':
      # use dp
      subproblem_method = single_dp
    elif subproblem_alg_name == 'cppdp':
      # use dp
      subproblem_method = run_dp_single
    else:
      raise ValueError("unknown method for sub problem")

  _ = dualnv_subgradient(
    problem,
    subproblem_method=subproblem_method,
    pool=mpc.Pool(processes=mp_num),
    **kwargs)
  return _


if __name__ == "__main__":
  kwargs = {  # kwargs
    "i": 10,
    "t": 20,
    "subproblem_alg": 'dp',
    "mp": True,
    "scale": 5,
    "max_iteration": 50
  }
  problem = create_instance(kwargs['i'], kwargs['t'])
  _ = main(problem, **kwargs)

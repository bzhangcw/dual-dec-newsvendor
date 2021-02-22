# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /model.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:56:16 pm
# @description:

import multiprocessing as mpc
import concurrent.futures as cf
import time
from collections import namedtuple
from .pydp import cppdp_single, cppdp_batch, convert_to_c_arr, convert_to_c_arr_int
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


def multiplier_method(g_k,
                      d_k,
                      delta_k,
                      gamma_k,
                      lambda_b,
                      projection_method,
                      b,
                      h,
                      option='subgrad'):
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
    self.z_bar = []
    self.z_k = []
    self.z_best = []
    self.lb = []
    self.fc = {}
    self.x_bar = []
    self.x_best = []


class Param:

  def __init__(self):
    self.use_maximum = False
    self.use_optimal = False


def dualnv_subgradient(problem,
                       scale,
                       subproblem_method=cppdp_single,
                       projection_method=projection_box,
                       mp=False,
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
  h, b = problem['h'][:scale], problem['p'][:scale]
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
  param.use_cpp_single = subproblem_method.__name__ == 'cppdp_single'
  param.direction = 'cvx' if dir_option == 'cvx' else 'subgrad'
  if mp:
    if kwargs.get("proc"):
      mpc = 1
      pool = mpc.Pool(4)
    else:
      mpc = cf.ThreadPoolExecutor(4)
    print(f"using mpc = {mpc}: 0-threads; 1-procs")
  else:
    mpc = -1

  # ==================
  # INITIALIZATION
  # ==================
  # initial solution:
  #   do nothing and thus everything is short
  x_best = x_bar = i_bar = 0
  # primal dual bound
  z_best = 1e6
  z_bar = b * sum(D)
  phi_bar = -1e3
  # dual variable
  lambda_k = lambda_b = h
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
  # C TYPES
  # ==================
  _I_size = len(I)
  a_arr = convert_to_c_arr(_I_size, problem['a'])
  b_arr = convert_to_c_arr(_I_size, problem['b'])
  tau_arr = convert_to_c_arr_int(_I_size, problem['tau'])
  s_arr = convert_to_c_arr(_I_size, problem['s0'])

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
    # if param.use_cpp_dp:
    c_arr = convert_to_c_arr(scale, lambda_k.astype(float))
    _L = problem['L']
    if mp:
      print("pls not using Python multiprocessings!")
      results = []
      for idx, i in enumerate(I):
        _a = problem['a'][idx]
        _b = problem['b'][idx]
        _s0 = problem['s0'][idx]
        _tau = problem['tau'][idx]
        if mpc:
          # NOT WORKING YET
          r = pool.apply_async(
              subproblem_method,
              (c_arr, scale, _a, _b, _L, _tau, _s0, False, True))
          results.append(r)
          for idx, r in enumerate(results):
            _best_v_i, _best_p_i, *_ = r.get()
            sub_v_k[idx] = _best_v_i
            x_k[idx, :, :] = _best_p_i
        else:
          r = pool.submit(subproblem_method, c_arr, scale, _a, _b, _L, _tau,
                          _s0, False, True)
          results.append(r)
          for idx, r in enumerate(results):
            _best_v_i, _best_p_i, *_ = r.result()
            sub_v_k[idx] = _best_v_i
            x_k[idx, :, :] = _best_p_i
    else:
      if param.use_cpp_single:
        for idx, i in enumerate(I):
          _a = problem['a'][idx]
          _b = problem['b'][idx]
          _s0 = problem['s0'][idx]
          _tau = problem['tau'][idx]
          _best_v_i, _best_p_i, *_ = subproblem_method(c_arr, scale, _a, _b, _L,
                                                       _tau, _s0, False, True)
          sub_v_k[idx] = _best_v_i
          x_k[idx, :, :] = _best_p_i
      else:
        sub_v_k, x_k = subproblem_method(_I_size, c_arr, scale, a_arr, b_arr,
                                         _L, tau_arr, s_arr, False, True)

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
    alp_k, gamma_k = alpha_method(
        gamma0=r0, iteration=k + 1, use_optimal=param.use_optimal, d=d_k, g=g_k)

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
    z_k = np.maximum(g_k * h, -g_k * b).sum(0)
    if z_k < z_best:
      z_best = z_k
      x_best = x_k

    # calculate cvx (averaging primal heuristic)
    surplus_idx_bar = d_k > 0
    z_bar = np.maximum(d_k * h, -d_k * b).sum(0)
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
    step, lambda_k = multiplier_method(
        g_k,
        d_k,
        z_bar - phi_k,
        gamma_k,
        lambda_b,
        projection_method,
        b,
        h,
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
    # volume algorithm:
    # Barahona, Francisco, and Ranga Anbil.
    # “The Volume Algorithm: Producing Primal Solutions with a Subgradient Method.” Mathematical Programming 87, no. 3 (2000): 385–99.
    if not param.use_maximum or _bool_lb_updated:
      lambda_b = lambda_k.copy()

    gap_k = (z_bar - phi_bar) / abs(z_bar)
    if k % 20 == 0:
      print(
          f"k: {k} @dual: {phi_k:.2f}; @lb: {phi_bar:.2f}; @z_best: {z_best:.2f}; @z_bar: {z_bar:.2f}; @gap: {gap_k:.4f}\n"
          f"@stepsize: {step:.5f}; @norm: {np.abs(d_k).sum():.2f}; @alp: {alp_k:.4f}; @time: {time.time() - st_sec:.2f};"
      )

    sol.z_bar.append(z_bar)
    sol.z_k.append(z_k)
    sol.z_best.append(z_best)
    sol.lb.append(phi_bar)
    sol.fc = fc_vals

    if k >= max_iteration or gap_k < gap or step < eps_step:
      x_bar = (1 - alp_k) * x_bar + x_k * alp_k
      i_bar = (1 - alp_k) * i_bar + i_k * alp_k
      sol.x_bar = x_bar
      sol.x_best = x_best
      break

    # increment iteration
    k += 1

  finish_sec = time.time()
  total_runtime = finish_sec - st_sec
  if max_iteration:
    print(
        f"@summary: @k: {k}; @dual: {phi_k}; @primal: {z_bar}; @lb: {phi_bar}; @gap: {gap_k} @sec: {total_runtime}"
    )
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
      subproblem_method = cppdp_single
    elif subproblem_alg_name == 'cppdp_batch':
      # use dp
      subproblem_method = cppdp_batch
    else:
      raise ValueError("unknown method for sub problem")

  _ = dualnv_subgradient(problem, subproblem_method=subproblem_method, **kwargs)

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

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
from collections import namedtuple as nt

from .model_single import single_mip
from .model_single_dp import single_dp
from .util import *


def min_alp(l, lt, length=100, alp_max=0.1):
  def _val(st):
    lp = (1 - st) * l + st * lt
    val = lp.dot(lp)
    return val
  
  vals = sorted(((alp_max * al / length, _val(alp_max * al / length))
                 for al in range(1, length)),
                key=lambda x: x[-1])
  return min(alp_max, vals[0][0])


# ===================
# PROJECTION METHODS
# ===================
def projection_box(x, lower, upper):
  """
  Args:
    x:
    lower:
    upper:

  Returns:
  """
  return np.minimum(np.maximum(x, lower), upper)


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


def repair_subgradient(
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
    **kwargs):
  """[summary]
  The subgradient algorithm for repair problem
  Args:
      subproblem_method (callable): the function for subproblem
      projection_method (callable): the function for projection of dual multipliers.
        Defaults to projection_box.
      **kwargs
  """
  
  h, b = problem['h'], problem['p']
  T = problem['T'][:scale]
  I = problem['I']
  D = problem['D'][:scale]
  numI = len(problem['I'])
  
  st_sec = time.time()
  sol_container = nt("sol", ["primal_sol", "primal_val", "primal_k", "lb"])
  sol_container.primal_sol = []
  sol_container.primal_val = []
  sol_container.primal_k = []
  sol_container.lb = []
  
  # algorithm options
  _use_maximum = dual_option == 'max'
  _use_optimal = hyper_option != 'simple'
  
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
  d_lambda_bar = 0
  
  # main routine
  for k in range(0, max_iteration):
  
    
    # ==================
    # solve \phi_k = \phi(\lambda_k)
    # ==================
    sub_v_k, x_k = np.zeros(numI), np.zeros((numI, scale, 3))
    
    # solve decomposable subproblems
    #   can use lazy multiprocessing
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
    d_lambda_k = (i_k - D)
    
    # =====================
    # update direction params
    # =====================
    alp_k, gamma_k = alpha_method(gamma0=r0, iteration=k + 1, use_optimal=_use_optimal, d=d_lambda_bar, g=d_lambda_k)
    print(f'==={alp_k, gamma_k} === ')
    
    # =====================
    # compute direction
    # =====================
    # there are many ways to do this
    x_bar = (1 - alp_k) * x_bar + x_k * alp_k
    i_bar = (1 - alp_k) * i_bar + i_k * alp_k
    d_lambda_bar = (i_bar - D)
    
    # =====================
    # the recovery algorithm
    # =====================
    #
    # update current primal
    #
    # This is an implied step,
    #  by this you actually use a "heuristic"
    #  since you retrieve a primal solution
    #  using U^T e - d
    # calculate best primal
    surplus_idx_k = d_lambda_k > 0
    z_k = h * d_lambda_k[surplus_idx_k].sum(
      0) - b * d_lambda_k[~surplus_idx_k].sum(0)
    
    # calculate cvx (averaging primal heuristic)
    surplus_idx_bar = d_lambda_bar > 0
    z_bar = h * d_lambda_bar[surplus_idx_bar].sum(
      0) - b * d_lambda_bar[~surplus_idx_bar].sum(0)

    # =====================
    # update dual vars
    # =====================
    step = 1 / (d_lambda_bar.dot(d_lambda_bar)) * (z_bar - phi_k) * gamma_k
    lambda_k = lambda_b + step * d_lambda_bar
    lambda_k = projection_method(lambda_k, -b, h)
    
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
    if not _use_maximum or _bool_lb_updated:
      lambda_b = lambda_k.copy()
    
    gap_k = (z_bar - phi_bar) / abs(z_bar)
    
    print(
      f"k: {k} @dual: {phi_k:.2f}; @lb: {phi_bar:.2f}; @primal: {z_k:.2f}; @primal_bar: {z_bar:.2f}; @gap: {gap_k:.4f}\n"
      f"@stepsize: {step:.4f}; @norm: {np.abs(d_lambda_bar).sum():.2f}; @alp: {alp_k:.4f}"
    )
    sol_container.primal_sol = x_bar
    sol_container.primal_val.append(z_bar)
    sol_container.primal_k.append(z_k)
    sol_container.lb.append(phi_bar)
    
    if gap_k < gap or step < 1e-4:
      break
  
  finish_sec = time.time()
  total_runtime = finish_sec - st_sec
  if max_iteration:
    print(
      f"@summary: @k: {k}; @dual: {phi_k}; @primal: {z_bar}; @lb: {phi_bar}; @gap: {gap_k} @sec: {total_runtime}")
  return x_bar, i_bar, alp_k, z_bar, lambda_b, sol_container


def main(problem, **kwargs):
  print(kwargs)
  subproblem_alg = kwargs.get('subproblem_alg', 'dp')
  
  # query subproblem algorithm
  if subproblem_alg == 'mip':
    # use mip
    subproblem_method = single_mip
  elif subproblem_alg == 'dp':
    # use dp
    subproblem_method = single_dp
  else:
    raise ValueError("unknown method for sub problem")
  
  _ = repair_subgradient(
    problem,
    subproblem_method=subproblem_method,
    pool=mpc.Pool(processes=8),
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

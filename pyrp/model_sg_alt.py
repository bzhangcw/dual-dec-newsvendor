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


def projection_box(x, lower, upper):
  """
  Args:
    x:
    lower:
    upper:

  Returns:
  """
  return np.minimum(np.maximum(x, lower), upper)


def repair_volume(  # volume algorithm for repair model
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
    **kwargs):
  """[summary]
  The volume algorithm for repair problem
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
  
  # ==================
  # INITIALIZATION
  # ==================
  # initial solution:
  #   do nothing and thus everything is short
  x_bar = i_bar = 0
  # primal dual bound
  z_bar = worst = b * sum(D)
  phi_bar = -1e6
  # dual variable
  lambda_k = lambda_b = np.ones(scale) * h
  # hyper parameters
  alp = 1
  improved = 0
  improved_eps = 30
  
  # dual options
  _use_maximum = dual_option == 'max'
  
  # main routine
  for k in range(0, max_iteration):
    # ==================
    # solve \phi(\lambda)
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
    
    phi_k = np.inner(D, -lambda_k) + sub_v_k.sum()
    
    # =====================
    # update current primal
    # =====================
    i_k = x_k.sum(0)[:, 0]
    x_bar = (1 - alp) * x_bar + x_k * alp
    i_bar = (1 - alp) * i_bar + i_k * alp
    
    # =====================
    # subgradient
    # =====================
    d_lambda_bar = (i_bar - D)
    d_lambda_k = (i_k - D)
    
    # =====================
    # lagrangian heuristic
    # =====================
    # This is an implied step,
    #  by this you actually use a heuristic
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
    step = 1 / (d_lambda_bar.dot(d_lambda_bar)) * (z_bar - phi_k) * r0
    lambda_k = lambda_b + step * d_lambda_bar
    lambda_k = projection_method(lambda_k, -b, h)
    
    gap_k = (z_bar - phi_bar) / abs(z_bar)
    # =====================
    # update alp:
    #   convex combination
    # =====================
    # there are many ways to do this:
    # - the volume:
    #   alp = min_alp(partial_lambda, b * (D - i_sol), alp_max=alp_max)
    #   if (k + 1) % 50 == 0:
    #     alp_max *= 0.5
    # - averaging:
    #   alp = 1 / (k + 1)
    alp = 1 / (k + 2)
    
    print(
      f"k: {k} @dual: {phi_k:.2f}; @lb: {phi_bar:.2f}; @primal: {z_k:.2f}; @primal_bar: {z_bar:.2f}; @gap: {gap_k:.4f}\n"
      f"@stepsize: {step:.4f}; @norm: {np.abs(d_lambda_bar).sum():.2f}; @alp: {alp:.4f}"
    )
    sol_container.primal_sol = x_bar
    sol_container.primal_val.append(z_bar)
    sol_container.primal_k.append(z_k)
    sol_container.lb.append(phi_bar)
    # eval best bound
    if phi_k > phi_bar:
      phi_bar = phi_k
      lambda_b = lambda_k.copy()
      improved = 0
    else:
      improved += 1
      if improved >= improved_eps:
        r0 = r0 / 2
        improved = 0
        
    # update base "dual multipliers"
    if not _use_maximum or phi_k > phi_bar:
      lambda_b = lambda_k.copy()
    
    if gap_k < gap or step < 1e-4:
      break
  
  finish_sec = time.time()
  total_runtime = finish_sec - st_sec
  if max_iteration:
    print(
      f"@summary: @k: {k}; @dual: {phi_k}; @primal: {z_bar}; @lb: {phi_bar}; @gap: {gap_k} @sec: {total_runtime}")
  return x_bar, i_bar, alp, z_bar, lambda_b, sol_container


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
  
  _ = repair_volume(
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

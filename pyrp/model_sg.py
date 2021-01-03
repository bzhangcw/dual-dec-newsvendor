# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /model.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:56:16 pm
# @description:

import multiprocessing as mpc

from .model_single import single_mip
from .model_single_dp import single_dp
from .util import *


def projected_multipliers_model(a, l, th, dl, dth):
  """
  calculate
  Args:
    l:
    th:
    dl:
    dth:

  Returns:

  """
  # raw steps
  tmp_l = l + a * dl
  tmp_th = th + a * dth

  # compute projection
  import mosek.fusion as mf

  expr = mf.Expr
  dom = mf.Domain
  mat = mf.Matrix

  model = mf.Model()
  lk = model.variable([l.shape[0]], dom.greaterThan(0.0))
  tk = model.variable([l.shape[0]], dom.greaterThan(0.0))
  lv = model.variable(1, dom.greaterThan(0.0))
  tv = model.variable(1, dom.greaterThan(0.0))
  delta_l = model.variable([l.shape[0]], dom.unbounded())
  delta_th = model.variable([l.shape[0]], dom.unbounded())

  model.constraint(expr.add(lk, tk), dom.lessThan(1))
  model.constraint(expr.sub(delta_l, expr.sub(lk, tmp_l)), dom.equalsTo(0))
  model.constraint(expr.sub(delta_th, expr.sub(tk, tmp_th)), dom.equalsTo(0))
  model.constraint(expr.vstack(tv, delta_l), dom.inQCone())
  model.constraint(expr.vstack(tv, delta_th), dom.inQCone())

  model.objective(mf.ObjectiveSense.Minimize, expr.add(lv, tv))
  model.solve()
  model.flushSolutions()
  # return l + a * (lk.level().round(3) - l), \
  #        th + a * (tk.level().round(3) - th)
  return lk.level().round(4), tk.level().round(4)


def min_alp(l, t, lt, tt, length=100, alp_max=0.1):

  def _val(st):
    lp = (1 - st) * l + st * lt
    tp = (1 - st) * t + st * tt
    val = lp.dot(lp) + tp.dot(tp)
    return val

  vals = sorted(((alp_max * al / length, _val(alp_max * al / length))
                 for al in range(1, length)),
                key=lambda x: x[-1])
  return min(alp_max, vals[0][0])


def repair_volume(  # repair volume algorithm
    problem,
    scale,
    subproblem_method=single_dp,
    projection_method=projected_multipliers_model,
    mp=True,
    pool=None,
    max_iteration=150,
    **kwargs):
  """[summary]
  The volume algorithm for repair problem
  Args:
      subproblem_method (callable): the function to calculate subproblem
      projection_method (callable): the function to calculate projection of dual multipliers. Defaults to projected_multipliers_model.
      **kwargs
  """

  h, b = problem['h'], problem['p']
  T = problem['T'][:scale]
  I = problem['I']
  D = problem['D'][:scale]
  numI = len(problem['I'])

  l_b, t_b = np.ones(scale) * 0.33, np.ones(scale) * 0.67

  lambdas = l_b.copy()
  thetas = t_b.copy()
  r0 = 1
  improved = 0
  z_bar = -1e6
  z_star = worst = b * sum(problem['D'])
  x_bar = 0
  alp = alp_max = 0.1
  print(max_iteration)
  for k in range(0, max_iteration):
    # solve relaxation
    if (k + 1) % 50 == 0:
      alp_max *= 0.5
    c = h * thetas - b * lambdas

    best_v, best_p = np.zeros(numI), np.zeros((numI, scale, 3))

    # solve subproblems
    if mp:
      results = [
          pool.apply_async(subproblem_method, (problem, scale, c, idx))
          for idx, i in enumerate(I)
      ]
      for idx, r in enumerate(results):
        _best_v_i, _best_p_i, *_ = r.get()
        best_v[idx] = _best_v_i
        best_p[idx, :, :] = _best_p_i
    else:
      for idx, i in enumerate(I):
        _best_v_i, _best_p_i, *_ = subproblem_method(problem, scale, c, idx)
        best_v[idx] = _best_v_i
        best_p[idx, :, :] = _best_p_i

    # update current primal
    x_bar = (1 - alp) * x_bar + best_p * (alp)
    p_bar = x_bar.sum(0)
    i_bar = p_bar[:, 0]
    p_sol = best_p.sum(0)
    i_sol = p_sol[:, 0]

    objectives_dl = np.inner(D, -c)
    objectives_subp = best_v.sum()
    objectives = objectives_dl + objectives_subp

    # compute multipliers from l_b, t_b
    partial_lambda = b * (D - i_bar)
    partial_theta = h * (i_bar - D)

    step = 1 / (partial_lambda.dot(partial_lambda) +
                partial_theta.dot(partial_theta)) * (worst - objectives) * r0

    lambdas, thetas = projection_method(step, l_b, t_b, partial_lambda,
                                        partial_theta)

    true_q = np.vstack((partial_theta, partial_lambda)).max(axis=0)
    z_primal = true_q.sum(0)

    # update alp
    alp = min_alp(
        partial_lambda,
        partial_theta,
        b * (D - i_sol),
        h * (i_sol - D),
        alp_max=alp_max)

    print(f"k: {k} @obj_t: {objectives}; @obj: {z_primal}; @lb: {z_bar};\n"
          f"@stepsize: {step}; @norm: {np.abs(lambdas).sum()}; @alp: {alp}")

    # eval
    if objectives > z_bar:
      z_bar = objectives
      l_b = lambdas.copy()
      t_b = thetas.copy()
      improved = 0
    else:
      improved += 1
      if improved >= 7:
        r0 = r0 / 2
        improved = 0
    if z_primal - z_bar < 5e-2:
      break
  return x_bar, i_bar, alp, true_q, l_b, t_b


if __name__ == "__main__":
  kwargs = {  # kwargs
      "i": 10,
      "t": 20,
      "subproblem_alg": 'dp',
      "mp": True,
      "scale": 5,
      "max_iteration": 50
  }
  num_i = kwargs.get('i')
  num_t = kwargs.get('t')
  scale = kwargs.get('scale', num_t)
  mp = kwargs.get('mp', False)
  subproblem_alg = kwargs.get('subproblem_alg', 'dp')
  max_iteration = kwargs.get('max_iteration', 150)
  # create instance
  problem = create_instance(num_i, num_t)

  # query subproblem algorithm
  if subproblem_alg == 'mip':
    # use mip
    subproblem_method = single_mip
  elif subproblem_alg == 'dp':
    # use dp
    subproblem_method = single_dp
  else:
    raise ValueError("unknown method for sub problem")

  sol, i_sol, alp, q_sol, l_b, t_b = repair_volume(
      problem,
      subproblem_method=subproblem_method,
      projection_method=projected_multipliers_model,
      time_scale=scale,
      pool=mpc.Pool(),
      **kwargs)

  # model, sol_bench, *_ = repair_mip_model(
  #   problem, engine='gurobi', scale=scale)

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

from .util import *

_logger = logging.getLogger("single.mip")
_logger.setLevel(logging.DEBUG)


def single_mip(problem, nT, c, idx, target=None):
  import gurobipy as grb
  s0 = problem['s0']
  a = problem['a'][idx]
  b = problem['b'][idx]
  L = problem['L']
  tau = problem['tau']
  T = problem['T'][:nT]

  model = grb.Model("rep")

  # vars
  x = model.addVars(T, name='x', vtype=grb.GRB.BINARY)
  u = model.addVars(T, name='u', vtype=grb.GRB.BINARY)
  s = model.addVars(T, name='s', lb=L)

  # constrs
  model.addConstr(s[0] == s0 - a * u[0])
  for t in T[:-1]:
    model.addConstr(s[t + 1] == s[t] - a * u[t + 1] +
                    b * x.get((t - tau + 1), 0))
  # model.addConstr(s[nT - 1] - a * u[nT ] + b * x.get((nT - 1 - tau + 1), 0) >= L)

  for t in T:
    for rho in range(t, t + tau):
      if rho == t:
        model.addConstr(x[t] + u.get((rho), 0) <= 1)
      else:
        model.addConstr(x[t] + x.get((rho), 0) + u.get((rho), 0) <= 1)

  if target is None:
    obj = grb.quicksum(v * c[t] for t, v in u.items())
    model.setObjective(obj)
  else:
    deltas = model.addVars(T, name='dt')
    for t in T:
      model.addConstr(deltas[t] >= c[t] * (u[t] - target[t]))
      model.addConstr(deltas[t] >= c[t] * (target[t] - u[t]))
    obj = grb.quicksum(deltas[t] for t in T)

  model.setObjective(obj)
  model.setParam("TimeLimit", 20)
  model.setParam("OutputFlag", 0)
  model.optimize()
  ssol = model.getAttr(grb.GRB.Attr.X, s)
  usol = model.getAttr(grb.GRB.Attr.X, u)
  xsol = model.getAttr(grb.GRB.Attr.X, x)

  best_p = np.array([[usol[t], xsol[t], ssol[t]] for t in T])
  best_v = model.ObjVal
  return best_v, best_p, model


if __name__ == '__main__':
  np.random.seed(1)
  scale = int(sys.argv[1])
  idx = 5
  problem = create_instance(10, 20)
  c = -np.random.random(scale)
  best_v, best_p, *_ = single_mip(problem, scale, c, idx)

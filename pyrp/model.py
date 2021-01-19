# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /model.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:56:16 pm
# @description:

from coptpy import *
import pandas as pd
from .util import *
import argparse
from .model_single_dp import single_dp
from .model_single import single_mip
import multiprocessing as mpc


def repair_msk_model(problem, **kwargs):
  time_limit = kwargs.get("timelimit", 300)
  mip_gap = kwargs.get("mipgap", 0.1)
  scale = kwargs.get("scale", 5)
  # vars
  I = problem['I']
  T = problem['T'][:scale]
  D = problem['D'][:scale]
  h = problem['h']
  p = problem['p']
  tau = problem['tau']
  s0 = problem['s0']
  pass


def repair_model(problem, **kwargs):
  engine = kwargs.get("engine", "gurobi").lower()
  if engine in ['gurobi', 'copt']:
    return repair_mip_model(problem, **kwargs)
  elif engine == 'mosek':
    return repair_msk_model(problem, **kwargs)
  else:
    raise ValueError(f"unknown MILP engine {engine}")


def repair_mip_model(problem, **kwargs):
  time_limit = kwargs.get("timelimit", 300)
  engine = kwargs.get("engine", "gurobi").lower()
  mp_num = kwargs.get("mp_num", 8)
  scale = kwargs.get("scale", 5)
  mipgap = kwargs.get("gap", 5e-3)
  if engine.lower() == 'copt':
    import coptpy as cp
    env = cp.Envr()
    # Create COPT model
    model = env.createModel("assembly_shop")
    quicksum = cp.quicksum
    ENGINE = cp.COPT
    PREFIX = "nameprefix"
    MIPGAP = cp.COPT.Param.RelGap
    TIMELIMIT = cp.COPT.Param.TimeLimit
    VERBOSE = "Logging"
    # raise ValueError("need more dev")
  else:
    import gurobipy as gr
    model = gr.Model('assembly_shop')
    quicksum = gr.quicksum
    ENGINE = gr.GRB
    PREFIX = "name"
    MIPGAP = gr.GRB.Param.MIPGap
    TIMELIMIT = gr.GRB.Param.TimeLimit
    VERBOSE = gr.GRB.Param.OutputFlag
  
  # vars
  I = problem['I']
  T = problem['T'][:scale]
  D = problem['D'][:scale]
  h = problem['h']
  p = problem['p']
  tau = problem['tau']
  s0 = problem['s0']
  
  # add model vars
  x = model.addVars(I, T, **{PREFIX: 'x', "vtype": ENGINE.BINARY})
  u = model.addVars(I, T, **{PREFIX: 'u', "vtype": ENGINE.BINARY})
  s = model.addVars(I, T, **{PREFIX: 's', "lb": problem['L']})
  q = model.addVars(T, **{PREFIX: "q"})
  
  # constrs
  for idx, i in enumerate(I):
    a, b = problem['a'][idx], problem['b'][idx]
    model.addConstr(s[i, 0] == s0 - a * u[i, 0])
    for t in T[:-1]:
      model.addConstr(s[i, t + 1] == s[i, t] - a * u[i, t + 1] +
                      b * x.get((i, t - tau + 1), 0))
  
  for idx, i in enumerate(I):
    for t in T:
      for rho in range(t, t + tau):
        if rho == t:
          model.addConstr(x[i, t] + u.get((i, rho), 0) <= 1)
        else:
          model.addConstr(
            x[i, t] + x.get((i, rho), 0) + u.get((i, rho), 0) <= 1)
  ql = qt = {}
  for t in T:
    i_sum = quicksum(u[i, t] for i in I)
    ql[t] = model.addConstr(q[t] >= h * i_sum - h * D[t])
    qt[t] = model.addConstr(q[t] >= p * D[t] - p * i_sum)
  
  obj = quicksum(v for v in q.values())
  model.setObjective(obj)
  model.setParam(TIMELIMIT, time_limit)
  model.setParam(VERBOSE, 1)
  model.setParam(MIPGAP, mipgap)
  try:
    model.setParam("Threads", mp_num)
  except:
    print(f'{engine} do not have mp options')
    return -1
  
  if engine == 'copt':
    model.solve()
    ssol = model.getInfo(ENGINE.Info.Value, s)
    usol = model.getInfo(ENGINE.Info.Value, u)
    xsol = model.getInfo(ENGINE.Info.Value, x)
    qsol = model.getInfo(ENGINE.Info.Value, q)
  else:
    model.optimize()
    ssol = model.getAttr(ENGINE.Attr.X, s)
    usol = model.getAttr(ENGINE.Attr.X, u)
    xsol = model.getAttr(ENGINE.Attr.X, x)
    qsol = model.getAttr(ENGINE.Attr.X, q)
  
  sol = np.zeros(shape=(len(I), len(T), 3))
  for idx, i in enumerate(I):
    for t in T:
      sol[idx, t] = [usol[i, t], xsol[i, t], ssol[i, t]]
  
  return model, sol, xsol, usol, ssol, qsol, ql, qt


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--alg', default='mip', type=str)
  args = parser.parse_args()
  num_i = 10
  num_t = 20
  problem = create_instance(num_i, num_t)
  alg = args.alg
  if alg == 'mip':
    model, sol, xsol, usol, ssol, qsol, ql, qt = repair_mip_model(
      problem, engine='gurobi', scale=5)
    print(sol[0, 0])
  else:
    pass

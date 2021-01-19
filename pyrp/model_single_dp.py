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
from collections import namedtuple

import pandas as pd

from .util import *

_logger = logging.getLogger("single.dp")
_logger.setLevel(logging.DEBUG)


def _cond(s1, s2):
  # do -> 
  if s1.u == 1 and s2.m != 1:
    return True
  # idle
  if s1.m == 0 and s2.m != 1:
    return True
  # maintenance ready
  if s1.m == 1 and s2.m != 1:
    return True
  # under maintenance
  if s1.m == s2.m + 1:
    return True
  return False


Tail = namedtuple('p', field_names=['u', 'm', 's', 't'])


def single_dp(problem, nT, c, idx, u_target=None, x_target=None):
  s0 = problem['s0']
  a = problem['a'][idx]
  b = problem['b'][idx]
  L = problem['L']
  tau = problem['tau']
  T = problem['T'][:nT]
  
  # define the stage ~ action evaluation
  _bool_u = u_target is not None
  _bool_x = x_target is not None
  if _bool_u and _bool_x:
    ac_val = lambda u, x, t: abs(2 * (u - u_target[t]) * c[t]) \
                             + abs((x - x_target[t]) * c[t])
  elif not _bool_u and not _bool_x:
    ac_val = lambda u, x, t: u * c[t]
  elif not _bool_u:
    ac_val = lambda u, x, t: abs((x - x_target[t]) * c[t]) + c[t] * u
  else:
    ac_val = lambda u, x, t: abs((u - u_target[t]) * c[t])
  
  tails_queue = []
  
  vals = dict()
  tails = dict()
  policy = dict()
  
  flags = [(1, 0)] + [(0, m) for m in range(0, tau + 1)]
  initials = [(1, 0, s0 - a, 0), (0, 0, s0, 0), (0, tau, s0, 0)]
  for u, m, s, t in initials:
    tails_queue.append(Tail(u, m, s, t))
  
  while tails_queue:
    pr = tails_queue[-1]
    _logger.debug(pr)
    if pr.t == nT - 1:
      # this is the final
      vals[pr.u, pr.m, pr.s, pr.t] = ac_val(pr.u, pr.m, pr.t)  # pr.u * c[pr.t]
      policy[pr.u, pr.m, pr.s, pr.t] = [pr]
      tails_queue.pop(-1)
      continue
    
    _tails = tails.get(pr, -1)
    
    if _tails != -1:
      # tail problems known
      pass
    else:
      # generate tail problems
      _tails = []
      for u, m in flags:
        # check life span violation
        _s = pr.s - a * u + b * int(pr.m == 1)
        if _s < L:
          continue
        new_pr = Tail(u, m, _s, pr.t + 1)
        # check flag transition violation
        _bool_flag = _cond(pr, new_pr)
        if _bool_flag:
          # lifespan & transition good :)
          _tails.append(new_pr)
          if new_pr not in vals:
            # not solved
            tails_queue.append(new_pr)
      
      tails[pr] = _tails
      continue
    
    # else, all tail problems has been solved
    #  do value eval
    try:
      _val = sorted(
        ((_tail_pr,
          ac_val(pr.u, pr.m, pr.t) + vals[_tail_pr.u, _tail_pr.m, _tail_pr.s, _tail_pr.t]
          ) for _tail_pr in _tails), key=lambda x: x[-1])[0]
      
      _best_child, _best_val = _val
      vals[pr.u, pr.m, pr.s, pr.t] = _best_val
      policy[pr.u, pr.m, pr.s, pr.t] = [pr] + policy[_best_child.u, _best_child.m, _best_child.s, _best_child.t]
    except:
      _logger.debug(f"invalid {pr}")
    tails_queue.pop(-1)
  
  vs = pd.Series(vals)
  
  # summarize
  best_s, best_v = min(((k, vs[k]) for k in initials), key=lambda x: x[-1])
  best_p = np.array([[pr.u, int(pr.m == 2), pr.s] for pr in policy[best_s]])
  return best_v, best_p


if __name__ == '__main__':
  import pickle
  
  problem = pickle.load(open("/Users/brent/Archiver/Workspace/repair/instances_pr/1_5_10_1611064221_0.json", 'rb'))
  c = -np.random.random(10)
  problem['tau'] = 2
  best_v1, best_p1, *_ = single_dp(problem, 10, c, 0)
  from pyrp.model_single import single_mip
  
  best_v, best_p, *_ = single_mip(problem, 10, c, 0)

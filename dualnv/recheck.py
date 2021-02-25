import pickle as pk
import sys
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import pyrp.pydp as py
import pyrp.model as mip
import pyrp.model_sg_alt as subgrad_main
from pyrp import *

plt.rcParams["font.size"] = 9
plt.rcParams["font.weight"] = 400
plt.rcParams["font.family"] = "roboto"
plt.rcParams["font.monospace"] = "roboto mono"
plt.rcParams["lines.linewidth"] = 0.8
plt.rcParams["legend.fontsize"] = "small"
plt.rcParams["text.usetex"] = True

# TEX alias
tex_alias = {'lb': r'$\phi_k$', 'val': r'$\bar z_k$', 'primal_k': r'$z_k$'}

if __name__ == '__main__':
  print(sys.argv)
  np.random.seed(1)

  # create instance
  problem = pk.load(open(sys.argv[1], 'rb'))
  timestamp = int(time.time())

  # test evals
  evals = ['cv_func2']
  ni = len(problem['I'])
  nt = len(problem['T'])
  kwargs = {  # kwargs
      "i": ni,
      "t": nt,
      "subproblem_alg_name": 'cppdp_batch',
      "mp": False,
      "proc": 0,
      "mp_num": 4,
      "gap": 0.005,
      "scale": nt,
      "max_iteration": 2000,
      "eps_step": 1e-5,
      "log_interval": 1,
      # "evals": evals
  }

  scale = kwargs.get('scale')
  num_i = kwargs.get('i')
  num_t = kwargs.get('t')
  mp_num = kwargs.get('mp_num')
  gap = kwargs.get('gap')
  bench_lb = {}
  bench_sol = {}

  results = defaultdict(dict)

  methods = {
      # "normal" convex sg
      # "bran95_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "cvx", "hyper_option": "optimal", **kwargs},
      "normal_sg": {
          "r0": 1.2,
          "dual_option": "normal",
          "dir_option": "subgrad",
          **kwargs
      },
      # "convex_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "cvx", **kwargs},
      # "volume" convex sg
      # "volume_sg": {"r0": 1.5, **kwargs}
  }


  # iteration json object
  # plot series
  plt_series = []

  # benchmark
  model, *_ = mip.repair_mip_model(
    problem, engine='gurobi', scale=scale, mp_num=mp_num, gap=gap)

  model_rel = model.relax()
  model_rel.optimize()


  for method, kw in methods.items():
    # run the method wrapper
    sol = subgrad_main.main(
        problem, **kw)

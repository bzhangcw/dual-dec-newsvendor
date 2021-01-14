import json
import sys
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import pyrp.model as mip
import pyrp.model_sg_alt as sg_alt
from pyrp.util import *

plt.rcParams["font.size"] = 9
plt.rcParams["font.weight"] = 400
plt.rcParams["font.family"] = "roboto"
plt.rcParams["font.monospace"] = "roboto mono"
plt.rcParams["lines.linewidth"] = 0.8
plt.rcParams["legend.fontsize"] = "small"

if __name__ == '__main__':
  print(sys.argv)
  np.random.seed(1)
  instances, ni, nt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
  timestamp = int(time.time())
  kwargs = {  # kwargs
    "i": ni,
    "t": nt,
    "subproblem_alg": 'dp',
    "mp": True,
    "gap": 0.005,
    "scale": nt,
    "max_iteration": 400,
    "eps_step": 1e-5
  }
  scale = kwargs.get('scale')
  num_i = kwargs.get('i')
  num_t = kwargs.get('t')
  
  bench_lb = {}
  bench_sol = {}
  
  results = defaultdict(dict)
  
  methods = {
    # "normal" convex sg
    # "bran95_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "cvx", "hyper_option": "optimal", **kwargs},
    "normal_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "subgrad", **kwargs},
    "convex_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "cvx", **kwargs},
    # "volume" convex sg
    # "volume_sg": {"r0": 1.5, **kwargs}
  }
  
  for i in range(instances):
    # iteration json object
    r = {}
    # plot series
    plt_series = []
    # create instance
    problem = create_instance(num_i, num_t)
    
    for method, kw in methods.items():
      # run the method wrapper
      sol, i_sol, alp, z_primal, l_b, sol_container = sg_alt.main(
        problem, **kw)
      r[f"{method}_lb"] = results[f"{method}_lb"][i] = sol_container.lb[1:]
      r[f"{method}_val"] = results[f"{method}_val"][i] = sol_container.primal_val[1:]
      r[f"{method}_sol"] = results[f"{method}_sol"][i] = sol_container.primal_sol[1:]
      r[f"{method}_primal_k"] = results[f"{method}_primal_k"][i] = sol_container.primal_k[1:]
    
    model, *_ = mip.repair_mip_model(
      problem, engine='gurobi', scale=scale)
    
    r['bench_lb'] = results['bench_lb'][i] = model.ObjBoundC
    r['bench_val'] = results['bench_val'][i] = model.ObjVal
    
    for method in methods:
      for who in ['lb', 'val', 'primal_k']:
        length = len(r[f"{method}_{who}"])
        if who == 'primal_k':
          plt.plot(range(length), r[f"{method}_{who}"], label=f"{method}_{who}", linestyle='dashed')
        else:
          plt.plot(range(length), r[f"{method}_{who}"], label=f"{method}_{who}")
    
    plt.legend(loc="lower left")
    plt.savefig(f"fig/conv_{i}_{num_i}_{num_t}.png", dpi=500)
    plt.clf()
    
    # with open(f"instances/result_{instances}_{num_i}_{num_t}_{timestamp}.json",
    #           'a') as f:
    #   f.write(json.dumps(r))
  
  import pickle as pk
  
  with open(f"instances/result_{instances}_{num_i}_{num_t}_{timestamp}.pk",
            'wb') as f:
    pk.dump(dict(results), f)

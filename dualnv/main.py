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
plt.rcParams["text.usetex"]: True

# TEX alias
tex_alias = {
  'lb': r'$\phi_k$',
  'val': r'$\bar z_k$',
  'primal_k': r'$z_k$'
}

if __name__ == '__main__':
  print(sys.argv)
  # np.random.seed(1)
  instances, ni, nt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
  timestamp = int(time.time())
  # test evals
  evals = ['cv_func2']

  kwargs = {  # kwargs
    "i": ni,
    "t": nt,
    "subproblem_alg_name": 'cppdp_batch',
    "mp": False,
    "proc": 0,
    "mp_num": 4,
    "gap": 0.005,
    "scale": nt,
    "max_iteration": 300,
    "eps_step": 1e-5,
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
    # "normal_sg": {"r0": 1.2, "dual_option": "normal", "dir_option": "subgrad", **kwargs},
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
      sol, i_sol, alp, z_primal, l_b, sol_container, total_runtime = subgrad_main.main(
        problem, **kw)
      r[f"{method}_lb"] = results[f"{method}_lb"][i] = sol_container.lb[1:]
      r[f"{method}_val"] = results[f"{method}_val"][i] = sol_container.z_bar[1:]
      r[f"{method}_primal_k"] = results[f"{method}_primal_k"][i] = sol_container.z_best[1:]
      r[f'{method}_time'] = results[f'{method}_time'][i] = total_runtime
      for fc, v in sol_container.fc.items():
        plt.plot(v[1:], label=f"{method}_{fc}", linestyle='dashed')
      # save evaluations
      plt.legend(loc="lower left")
      plt.savefig(f"fig/evals_{i}_{method}_{num_i}_{num_t}.png", dpi=500)
      plt.clf()
      # save vals
      for who in ['lb', 'val', 'primal_k']:
        length = len(r[f"{method}_{who}"])
        if who == 'primal_k':
          plt.plot(range(length), r[f"{method}_{who}"], label=tex_alias.get(who), linestyle='dashed')
        else:
          plt.plot(range(length), r[f"{method}_{who}"], label=tex_alias.get(who))

      plt.legend(loc="lower left")
      plt.savefig(f"fig/conv_{i}_{method}_{num_i}_{num_t}.png", dpi=500)
      plt.clf()

    model, *_ = mip.repair_mip_model(
      problem, engine='gurobi', scale=scale, mp_num=mp_num, gap=gap)

    r['bench_lb'] = results['bench_lb'][i] = model.ObjBoundC
    r['bench_val'] = results['bench_val'][i] = model.ObjVal
    r['bench_time'] = results['bench_time'][i] = model.Runtime

    with open(f"instances_pr/{instances}_{num_i}_{num_t}_{timestamp}_{i}.json",
              'wb') as f:
      pk.dump(problem, f)

  with open(f"instances/result_{instances}_{num_i}_{num_t}_{timestamp}.pk",
            'wb') as f:
    pk.dump(dict(results), f)

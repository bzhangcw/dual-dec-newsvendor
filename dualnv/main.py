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
  instances, ni, nt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
  uniform = int(sys.argv[4])
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
      "gap": 0.001,
      "scale": nt,
      "max_iteration": 1000,
      "eps_step": 1e-5,
      "log_interval": 20,
      "mip_gap": 0
      # "evals": evals
  }

  scale = kwargs.get('scale')
  num_i = kwargs.get('i')
  num_t = kwargs.get('t')
  mp_num = kwargs.get('mp_num')
  mip_gap = kwargs.get('mip_gap')
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

  for i in range(instances):
    # iteration json object
    r = {}
    # plot series
    plt_series = []
    # create instance
    problem = create_instance(num_i, num_t, uniform)

    # benchmark
    model, *_ = mip.repair_mip_model(
        problem, engine='gurobi', scale=scale, mp_num=mp_num, gap=mip_gap)

    model_relax_u, *u_ = mip.repair_mip_model(
        problem,
        engine='gurobi',
        scale=scale,
        mp_num=mp_num,
        gap=mip_gap,
        relax_u=True)

    model_relax_x, *x_ = mip.repair_mip_model(
        problem,
        engine='gurobi',
        scale=scale,
        mp_num=mp_num,
        gap=mip_gap,
        relax_x=True)

    instance_id = f"{num_i}_{num_t}_{timestamp}_{i}"
    r['idx'] = results['idx'][i] = instance_id
    r['bench_lb'] = results['bench_lb'][i] = model.ObjBound
    r['bench_val'] = results['bench_val'][i] = model.ObjVal
    r['bench_time'] = results['bench_time'][i] = model.Runtime

    # relaxations
    r['relax_u_lb'] = results['relax_u_lb'][i] = model_relax_u.ObjBound
    r['relax_u_val'] = results['relax_u_val'][i] = model_relax_u.ObjVal
    r['relax_u_time'] = results['relax_u_time'][i] = model_relax_u.Runtime
    r['relax_x_lb'] = results['relax_x_lb'][i] = model_relax_x.ObjBound
    r['relax_x_val'] = results['relax_x_val'][i] = model_relax_x.ObjVal
    r['relax_x_time'] = results['relax_x_time'][i] = model_relax_x.Runtime

    for method, kw in methods.items():
      # run the method wrapper
      sol = subgrad_main.main(problem, **kw)
      r[f"{method}_lb"] = results[f"{method}_lb"][i] = sol.lb[1:]
      r[f"{method}_val"] = results[f"{method}_val"][i] = sol.z_bar[1:]
      r[f"{method}_primal_k"] = results[f"{method}_primal_k"][i] = sol.z_best[
          1:]
      r[f'{method}_time'] = results[f'{method}_time'][i] = sol.total_runtime
      for fc, v in sol.fc.items():
        plt.plot(v[1:], label=f"{method}_{fc}", linestyle='dashed')
      # save evaluations vals
      plt.legend(loc="lower left")
      plt.savefig(f"fig/evals_{i}_{method}_{num_i}_{num_t}.png", dpi=1000)
      plt.clf()
      # save major vals
      plt.plot(
          range(len(sol.lb) - 1),
          r['bench_val'] * np.ones(len(sol.lb) - 1),
          label=r'$f^\star$',
          linestyle='dashed')
      for who in ['lb', 'val', 'primal_k']:
        length = len(r[f"{method}_{who}"])
        if who == 'primal_k':
          plt.plot(
              range(length),
              r[f"{method}_{who}"],
              label=tex_alias.get(who),
              linestyle='dashed')
        else:
          plt.plot(
              range(length), r[f"{method}_{who}"], label=tex_alias.get(who))
      plt.xlabel(r"iteration $k$")
      plt.ylabel(r"primal and dual values")
      plt.legend(loc="lower left")
      plt.savefig(f"fig/conv_{i}_{method}_{num_i}_{num_t}.png", dpi=500)
      plt.clf()

      # if phi^\star != f^\star
      if abs(r['bench_lb'] - r[f"{method}_lb"][-1]) > 0.01:
        print(r)
        with open(f"instances_pr/{instance_id}.json", 'wb') as f:
          pk.dump(problem, f)
        model.write(f"instances_pr/{instance_id}.lp")
        # DEBUG FOR PHI_LAMBDA
        py.test_phi_lambda(sol.lambda_k, problem, scale)

  # save results for analysis
  with open(f"instances/result_{instances}_{num_i}_{num_t}_{timestamp}.pk",
            'wb') as f:
    pk.dump(dict(results), f)

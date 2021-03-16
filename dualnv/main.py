"""
 main entry
 @author: c.z
"""
import json
import pickle as pk
import time
from collections import defaultdict

import pyrp.model as mip
import pyrp.model_sg_alt as subgrad_main
import pyrp.pydp as py
from pyrp import *
from pyrp import algorithms
from pyrp import util

parser = util.ArgumentParser()
parser.add_argument("-n", type=int, default=1)
parser.add_argument("--ni", type=int, default=1)
parser.add_argument("--nt", type=int, default=1)
parser.add_argument("--type", type=int, default=1)
parser.add_argument("--mp", type=bool, default=False)
parser.add_argument("--mp_num", type=int, default=4)
parser.add_argument("--scale", type=int, default=None)
parser.add_argument("--plot_sg", type=bool, default=False)
parser.add_argument("--mips", action='store', dest='mips',
                    type=str, nargs='*', default=algorithms.MIPS,
                    help="mip models", choices=algorithms.MIPS)
parser.add_argument("--subgrads", action='store', dest='subgrads',
                    type=str, nargs='*', default=["normal_sg"],
                    help="subgrad algorithms", choices=algorithms.ALGORITHMS)

np.random.seed(1)


def main():
  timestamp = int(time.time())

  args = parser.parse_args()
  kwargs = args.__dict__
  print("system arguments")
  print(json.dumps(kwargs, indent=2))

  algs = args.subgrads
  mips = args.mips

  # alias
  instances = args.n
  ni, nt, instance_type, scale = args.ni, args.nt, args.type, args.nt

  # test evals
  evals = ['cv_func2']

  bench_lb = {}
  bench_sol = {}

  results = defaultdict(dict)

  for i in range(instances):
    # iteration json object
    # kept info for this instance
    r = {}
    # create instance
    problem = create_instance(ni, nt, **util.INSTANCE_TYPES[instance_type])
    print("instance arguments:")
    print(json.dumps(util.INSTANCE_TYPES[instance_type], indent=2))
    instance_id = f"{ni}_{nt}_{timestamp}_{i}"
    # benchmark set by mip models
    for mip_name in mips:
      mip_kwargs = algorithms.MIPS[mip_name]
      model, *_ = mip.repair_mip_model(
        problem,
        **mip_kwargs)

      r['idx'] = results['idx'][i] = instance_id
      r[f'{mip_name}_lb'] = results['bench_lb'][i] = model.ObjBound
      r[f'{mip_name}_val'] = results['bench_val'][i] = model.ObjVal
      r[f'{mip_name}_time'] = results['bench_time'][i] = model.Runtime

    # our algorithms
    for method in algs:
      # algorithm kwargs
      kw = algorithms.ALGORITHMS[method]
      # run the method wrapper
      sol = subgrad_main.main(problem, **kw, **kwargs)
      r[f"{method}_lb"] \
        = results[f"{method}_lb"][i] = sol.lb[1:]
      r[f"{method}_val"] \
        = results[f"{method}_val"][i] = sol.z_bar[1:]
      r[f"{method}_primal_k"] \
        = results[f"{method}_primal_k"][i] = sol.z_best[1:]
      r[f'{method}_time'] \
        = results[f'{method}_time'][i] = sol.total_runtime
      if args.plot_sg:
        for fc, v in sol.fc.items():
          plt.plot(v[1:], label=f"{method}_{fc}", linestyle='dashed')
        # save evaluations vals
        plt.legend(loc="lower left")
        plt.savefig(f"fig/evals_{i}_{method}_{ni}_{nt}.png", dpi=1000)
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
              label=TEX_ALIAS.get(who),
              linestyle='dashed')
          else:
            plt.plot(
              range(length), r[f"{method}_{who}"], label=TEX_ALIAS.get(who))
        plt.xlabel(r"iteration $k$")
        plt.ylabel(r"primal and dual values")
        plt.legend(loc="lower left")
        plt.savefig(f"fig/conv_{i}_{method}_{ni}_{nt}.png", dpi=500)
        plt.clf()

      # if phi^\star != f^\star
      # [strong duality not hold then output for further analytics]
      if abs(r['bench_lb'] - r[f"{method}_lb"][-1]) > 0.01:
        with open(f"instances_pr/{instance_id}.json", 'wb') as f:
          pk.dump(problem, f)
        model.write(f"instances_pr/{instance_id}.lp")
        # DEBUG FOR PHI_LAMBDA
        #
        # print(r)
        # py.test_phi_lambda(sol.lambda_k, problem, scale)

  # save all results for analysis in pickle
  with open(f"instances/result_{instances}_{ni}_{nt}_{timestamp}.pk",
            'wb') as f:
    pk.dump(dict(results), f)


if __name__ == '__main__':
  main()

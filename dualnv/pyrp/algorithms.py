MIP_DEFAULTS = {
  "mp_num": 4,
  "gap": 0,
  "engine": 'gurobi'
}

MIPS = {
  "bench": MIP_DEFAULTS,
  "relax_u":
    {
      "relax_u": True,
      **MIP_DEFAULTS
    },
  "relax_x":
    {
      "relax_x": True,
      **MIP_DEFAULTS
    }
}

ALG_DEFAULTS = {
  "gap": 0.001,
  "max_iteration": 1000,
  "eps_step": 1e-5,
  "log_interval": 20,
  "mip_gap": 0
}

ALGORITHMS = {
  # "normal" convex sg
  "bran95_sg": {
    "r0": 1.2,
    "dual_option": "normal",
    "dir_option": "cvx",
    "hyper_option": "optimal",
    **ALG_DEFAULTS},
  "normal_sg": {
    "r0": 1.2,
    "dual_option": "normal",
    "dir_option": "subgrad",
    "subproblem_alg_name": 'cppdp_batch',
    **ALG_DEFAULTS
  },
  "convex_sg": {
    "r0": 1.2,
    "dual_option": "normal",
    "dir_option": "cvx",
    **ALG_DEFAULTS},
  # "volume" convex sg
  # "volume_sg": {"r0": 1.5, **kwargs}
}

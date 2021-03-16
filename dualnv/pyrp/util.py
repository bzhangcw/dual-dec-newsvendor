# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /util.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:25:21 pm
# @description:

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.size"] = 9
plt.rcParams["font.weight"] = 400
plt.rcParams["font.family"] = "roboto"
plt.rcParams["font.monospace"] = "roboto mono"
plt.rcParams["lines.linewidth"] = 0.8
plt.rcParams["legend.fontsize"] = "small"
plt.rcParams["text.usetex"] = True


# TEX alias
TEX_ALIAS = {'lb': r'$\phi_k$', 'val': r'$\bar z_k$', 'primal_k': r'$z_k$'}

DEFAULT_INSTANCE_PARAM = {
  "uniform_c": True,
  "uniform_flow": False,
  "uniform_penalty": True,
}

INSTANCE_TYPES = {
  1: DEFAULT_INSTANCE_PARAM,  # default, which is uniform sum, regular flow, and uniform penalty
  2: {**DEFAULT_INSTANCE_PARAM, "uniform_penalty": False},
  3: {**DEFAULT_INSTANCE_PARAM, "uniform_c": False},
  4: {**DEFAULT_INSTANCE_PARAM, "uniform_flow": True}
}


def create_instance(
    nI: int, nT: int,
    uniform_c=True,
    uniform_flow=False,
    uniform_penalty=False
):
  I = [f"fl_{i}" for i in range(nI)]
  T = range(nT)
  L = 2  # np.random.random() * 0.3
  U = np.random.randint(1, 10) + 12
  D = np.random.randint(nI // 2, 1 * nI + 1, size=nT)
  tau = np.random.randint(1, 5, nI)

  if uniform_flow:
    a = np.ones(nI)
    b = np.ones(nI)
  else:
    a = np.random.randint(2, 5, nI)
    b = np.random.randint(5, 10, nI)

  s0 = np.random.randint(5, 8, nI)

  if uniform_penalty:
    h = np.ones(nT) * 2
    p = np.ones(nT) * 3
  else:
    h = np.random.randint(1, 5, nT)
    p = np.random.randint(2, 6, nT)

  if uniform_c:
    c = np.ones(nI)
  else:
    c = np.random.randint(2, 4, nI)

  return dict(
    D=D.astype(float).tolist(),
    a=a.astype(float).tolist(),
    b=b.astype(float).tolist(),
    I=I,
    T=list(T),
    L=L,
    c=c,
    U=U,
    tau=tau.astype(int).tolist(),
    s0=s0.astype(float).tolist(),
    h=h,
    p=p)


NON_TRIVIAL_INS = {
  'D': [1.0, 0.0],
  'a': [2.0],
  'b': [6.0],
  'I': ['fl_0'],
  'T': [0, 1],
  'L': 2,
  'c': np.array([1]),
  'U': 18,
  'tau': [1],
  's0': [6.0],
  'h': np.array([4, 1]),
  'p': np.array([2, 3])
}


class ArgumentParser(argparse.ArgumentParser):
  def print_help(self, file=None):
    import json
    super(ArgumentParser, self).print_help()
    print("\ninstance type notation:\n")
    print(json.dumps(INSTANCE_TYPES, indent=2))


if __name__ == '__main__':
  import sys
  import json

  I, T = sys.argv[1:]
  m = create_instance(int(I), int(T))
  with open(f"test/test_{T}.json", 'w') as f:
    json.dump(m, f)

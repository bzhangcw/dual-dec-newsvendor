# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: pyrp
# @file: /util.py
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 9:25:21 pm
# @description:

import random
import json
import numpy as np


def create_instance(nI: int, nT: int):
  I = [f"fl_{i}" for i in range(nI)]
  T = range(nT)
  L = 2  # np.random.random() * 0.3
  U = np.random.randint(1, 10) + 12
  D = np.random.randint(nI // 2, 2 * nI + 1, size=nT)
  tau = np.random.randint(1, 2, nI)
  a = np.random.randint(2, 5, nI)
  b = np.random.randint(5, 10, nI)
  s0 = np.random.randint(5, 8, nI)

  # h = np.ones(nT) * 2
  # p = np.ones(nT) * 3
  h = np.random.randint(1, 5, nT)
  p = np.random.randint(2, 6, nT)
  c = np.ones(nI)
  # c = np.random.randint(2, 4, nI)
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


if __name__ == '__main__':
  import sys
  import json

  I, T = sys.argv[1:]
  m = create_instance(int(I), int(T))
  with open(f"test/test_{T}.json", 'w') as f:
    json.dump(m, f)

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
  D = np.random.randint(nI // 2, nI, size=nT)
  tau = np.random.randint(2, 5, nI)
  a = np.random.randint(2, 5, nI)
  b = np.random.randint(5, 10, nI)
  h = 11
  p = 18
  s0 = np.random.randint(5, 8, nI)
  return dict(
    D=D.astype(float).tolist(),
    a=a.astype(float).tolist(),
    b=b.astype(float).tolist(),
    I=I,
    T=list(T),
    L=L,
    U=U,
    tau=tau.astype(int).tolist(),
    s0=s0.astype(float).tolist(),
    h=h,
    p=p)


def create_instance_vec(nI: int, nT: int, nIns: int = 100):
  """create randomly instances:
    D is of shape (nIns, None)
  Args:
      nI (int): [description]
      nT (int): [description]
      nIns (int): number of samples
  Returns:
      [type]: [description]
  """
  I = [f"fl_{i}" for i in range(nI)]
  T = range(nT)
  L = np.random.random() * 0.3
  U = np.random.random() * 0.5 + 1.2
  # D = np.random.randint(nI // 2, nI, size=nT)
  a = np.random.random(nI) * 0.5
  b = np.random.random(nI) * 0.5 + 0.5
  h = 1
  p = 2
  s0 = 1
  D = np.random.randint(nI // 2, nI, size=(nIns, nT))
  return dict(
    Darr=D,
    D=D.astype(float).tolist(),
    a=a.tolist(),
    b=b.tolist(),
    I=I,
    T=T,
    L=L,
    U=U,
    tau=2,
    s0=s0,
    h=h,
    p=p)


if __name__ == '__main__':
  import sys
  import json
  I, T  = sys.argv[1:]
  m = create_instance(int(I), int(T))
  with open(f"test/test_{T}.json", 'w') as f:
    json.dump(m, f)

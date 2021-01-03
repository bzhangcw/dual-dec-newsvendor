cd repair


### 1
from coptpy import *
import pandas as pd
from pyrp.util import *
import argparse
from pyrp.model_single_dp import single_dp
from pyrp.model_single import single_mip

num_i = 10
num_t = 20
problem = create_instance(num_i, num_t)
scale = 20
l_0, t_0 = np.ones(scale) * 0.6, np.ones(scale) * 0.4
lambdas = l_0.copy()
thetas = t_0.copy()
h, b = problem['h'], problem['p']
T = problem['T'][:scale]
D = problem['D']

c = [h * thetas[t] - b * lambdas[t] for t in T]

I = problem['I']
numI = len(problem['I'])
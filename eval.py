import os
import pickle as pk

import pandas as pd

pd.set_option("display.float_format", lambda x: f"{x: .2f}")
INSTANCE_DIR = './instances'

dfs = []
methods = [
    # "normal" convex sg
    "normal_sg",
    # "volume" convex sg
    "volume_sg"
]


def get_last(df, serie):
  return df[serie].apply(lambda x: x[-1])


for fname in os.listdir(INSTANCE_DIR):
  if not fname.endswith("pk"):
    continue
  n, i, t = fname.split("_")[1:4]
  print(n, i, t)
  data = pk.load(open(f"{INSTANCE_DIR}/{fname}", 'rb'))
  df = pd.DataFrame(data)
  method_vals = {}
  for method in methods:
    for who in ['lb', 'val', 'primal_k']:
      method_vals[f"{method}_{who}"] = get_last(df, f"{method}_{who}")

  df = df.assign(I=i, T=t, **method_vals)

  dfs.append(df)

df_all = pd.concat(dfs, sort=False).reset_index(drop=True)

df_out = df_all[['I', 'T', 'bench_lb', 'bench_val'] +
                list(method_vals.keys())].query("bench_lb > 0")
group_vals = {}
for method in methods:
  for who in ['lb', 'val']:
    group_vals[f"{method}_{who}_gap"] = df_out.eval(
        f"({method}_{who} - bench_{who}) / bench_{who}").apply("{:.2%}".format)
df_out = df_out.assign(**group_vals).sort_values(list(group_vals.keys()))

latex_string = df_out.to_latex()
df_out.to_csv("eval.all.csv")
print(latex_string)

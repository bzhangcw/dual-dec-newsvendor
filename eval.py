import os
import pickle as pk

import pandas as pd

pd.set_option("display.float_format", lambda x: f"{x: .2f}")
INSTANCE_DIR = './instances'

dfs = []
methods = [
    # "normal" regular sg
    "normal_sg",
    # "avg" convex sg
    "convex_sg"
]


def get_last(df, serie):
  try:
    return df[serie].apply(lambda x: x[-1])
  except:
    return df[serie]

for fname in os.listdir(INSTANCE_DIR):
  if not fname.endswith("pk"):
    continue
  n, i, t = fname.split("_")[1:4]
  print(n, i, t)
  data = pk.load(open(f"{INSTANCE_DIR}/{fname}", 'rb'))
  df = pd.DataFrame(data)
  method_vals = {}
  for method in methods:
    for who in ['lb', 'val', 'time']:
      method_vals[f"{method}_{who}"] = get_last(df, f"{method}_{who}")

  df = df.assign(I=i, T=t, **method_vals)

  dfs.append(df)

df_all = pd.concat(dfs, sort=False).reset_index(drop=True)

df_out = df_all[['I', 'T', 'bench_lb', 'bench_val', 'bench_time'] +
                list(method_vals.keys())].query("bench_lb > 0")
group_vals = {}
for method in methods:
  for who in ['lb', 'val']:
    group_vals[f"{method}_{who}_gap"] = df_out.eval(
        f"({method}_{who} - bench_{who}) / bench_{who}").apply("{:.2%}".format)
df_out = df_out.assign(**group_vals).sort_values(list(group_vals.keys()))

# sorted colums
cols = ['I', 'T', 'bench_lb', 'bench_val', 'bench_time']
for method in methods:
  cols += [f'{method}_lb', f'{method}_val', f'{method}_time', f'{method}_lb_gap', f'{method}_val_gap']

df_out = df_out[cols]

latex_string = df_out.to_latex()
df_out.to_csv("eval.all.csv")
print(latex_string)

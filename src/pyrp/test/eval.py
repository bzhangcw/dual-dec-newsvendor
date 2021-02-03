


def cv_func1(*args):
  """
  eval: z_bar - lambda_k d_k
  Args:
    z_bar:
    lambda_k:
    d_k:

  Returns:

  """
  z_bar, lambda_k, d_k, g_k = args
  return z_bar - lambda_k.dot(d_k)

def cv_func2(*args):
  """
  eval: lambda_k d_k
  Args:
    z_bar:
    lambda_k:
    d_k:

  Returns:

  """
  z_bar, lambda_k, d_k, g_k = args
  return lambda_k.dot(g_k)
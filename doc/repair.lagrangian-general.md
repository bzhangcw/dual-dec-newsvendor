---
@license: %MIT License%:~ http://www.opensource.org/licenses/MIT
@project: repair
@file: /repair.lagrangian.md
@created: Tuesday, 15th December 2020
@author: C. Zhang (chuwzhang@gmail.com)
@modified: C. Zhang (chuwzhang@gmail.com>)
   Tuesday, 15th December 2020 4:55:31 pm
@description: 
---


consider the following program

$$\begin{aligned}
  &\min c^\top y \\
\mathbf{s.t.} & \\
  & Ax - y = d \\
  & x \in \Omega_x, y \ge 0 
\end{aligned}$$


consider the lagrangian relaxation, the dual function is:

$$
%\begin{equation}
\begin{aligned}
\phi(\lambda) &= \min_{x,y} (c - \lambda)^\top y  + \lambda^\top Ax  - \lambda ^\top d \\
  &=\min_x \lambda^\top Ax - \lambda^\top d\\
\end{aligned}
%\end{equation}
$$

in the subgradient algorithm, we compute $y^k = Ax^k - d$
one subgradient of $\phi$ at $k$-th iteration is:

$$s^k = Ax^k -d \in \partial\phi^k$$


$$\begin{aligned}
&y^k \in \partial \phi^{k},\; \lambda^{k+1} = \tilde \lambda^k + s^{k+1}\cdot \bar y^k,\;s^{k+1} = \frac{s^0\cdot(\rho - l^k)}{\|\bar y^k\|^2} \\
& x^{k+1} = \arg \min_x \phi^{k+1}, \;  y^{k+1} = Ax^{k+1} - d\; \\
& \bar x^{k+1} = \alpha x^{k+1} + (1-\alpha)\cdot \bar x^k 
\end{aligned}
$$


heuristic step:
$$y^{k+1} = Ax^{k+1} - d $$

we wish to show the decrease of primal - lower bound gap, where $l^k =\max_k (\lambda^k)^\top y^k$ and $\tilde \lambda^k, \tilde y^k$ is the associated optimizers. Notice:

$$\begin{aligned}
l^{k+1} =& \max\{l^k, \phi^{k+1}\}
\end{aligned}$$

> try to compute the gap

the gap may note be strictly decreasing?


**(1. not good)**

$$\begin{aligned}
&|\bar z^{k+1} - l^{k+1}| = |(1-\alpha) \bar z^{k} + \alpha z^{k+1} - \max\{l^k, \langle\lambda^{k+1}, y^{k+1}\rangle\}| \\
\le & (1-\alpha) \cdot | (\bar z^k - l^k) | + \alpha \cdot | z^{k+1}  -  \langle\lambda^{k+1}, y^{k+1}\rangle | \\
\le &  (1-\alpha) \cdot | (\bar z^k - l^k) | + \alpha \cdot | \bar z^{k+1}  - l^{k+1}| + \alpha \cdot | z^{k+1} - \langle\lambda^{k+1}, y^{k+1}\rangle | + \alpha \cdot | \bar z^{k+1} + z^{k+1}| 
\end{aligned}
$$

**(2.using subgrad)**

since $y^{k+1} \in \partial\phi^{k+1}$

$$\lang y^{k+1}, (\lambda^{k+1} - \tilde \lambda^k) \rang \le  \phi(\lambda^{k+1}) - \phi(\tilde \lambda ^k) = \phi^{k+1} - l^k$$

we have:

$$\begin{aligned}
  \max\{l^k, \phi^{k+1}\} &= l^k + \max\{0,  \phi^{k+1} - l^k \} \\
  & \ge l^k + \max\{0, \lang y^{k+1}, (\lambda^{k+1} - \tilde \lambda^k) \rang\} \\
  & \ge l^k + \lang y^{k+1}, \frac{(\rho - l^k)}{\|\bar y^k\|^2}\bar y^k\rang
  
\end{aligned}$$

then:

$$\begin{aligned}
  \bar z^{k+1} - l^{k+1} &= (1-\alpha) \bar z^{k} + \alpha z^{k+1} - \max\{l^k, \phi^{k+1}\} \\ 
  & \le (1-\alpha)\bar z^k + \alpha z^{k+1} -  l^k - \lang y^{k+1}, \frac{(\rho - l^k)}{\|\bar y^k\|^2}\bar y^k \rang
\end{aligned}$$
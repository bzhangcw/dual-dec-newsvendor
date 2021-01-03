---
@license: %MIT License%:~ http://www.opensource.org/licenses/MIT
@project: repair
@file: /repair.det.old.md
@created: Sunday, 29th November 2020
@author: C. Zhang (chuwzhang@gmail.com)
@modified: C. Zhang (chuwzhang@gmail.com>)
   Sunday, 29th November 2020 10:38:26 pm
@description: 
---
# Deterministic (old)

We first consider the deterministic problem.

The problem can be solved with subgradient method in polynomial time and the solution is exact.  If we allow tolerance $\epsilon \ge 0$ on subgradient method, the complexity is:

$$O\left(\frac{1}{\epsilon^2}\cdot\tau\cdot|I|\cdot|T|^3\right)$$ 


## Subgradient method

Relax binding constraints of $q$

$\Omega_i$ defined as the region of $x_{(i,\cdot)}, u_{(i,\cdot)}, s_{(i,\cdot)}, \forall i\in I$.

we notice $z_{\mathsf{LD}}(\lambda, \theta)$ is unbounded unless:
$$\lambda, \theta \in \{\lambda, \theta \ge 0 \big | (1-\lambda_t - \theta_t) \ge 0,\forall t\in T\}$$

we have:
$$\begin{aligned}
z_{\mathsf{LD}}(\lambda, \theta) = \sum_t 
      d_t(b\lambda_t -h \theta_t) + \min_{x, s, u} \left[  \sum_i \sum_t u_{i,t}(h\theta_t - b\lambda_t) \right]
\end{aligned}$$

We wish to solve:
$$\sup_{(\lambda, \theta)}z_{\mathsf{LD}}$$

We can solve for each $i\in I$ independently at each iteration of a subgradient method.

Notice:

- at iteration $k$, suppose multipliers $\lambda^k + \theta^k \le 1$, if $( x^\star,  s^\star,  u^\star)$ solves the relaxed minimization problem, then it is also feasible for the original problem (compute $q$ accordingly). The optimality gap can easily be calculated by simple evaluations.
- at each iteration $k$, the sub-gradients: $\mathcal P$ is the orthogonal projection onto $\mathcal D =\left\{(\lambda, \theta) \;| \; \lambda + \theta \le 1\right\}$

$$\begin{aligned}
  &\nabla \lambda^k = b\cdot \left(d -  (U^k)^\top e\right) \\
  &\nabla \theta^k = h\cdot \left((U^k)^\top e - d\right) \\
  &\theta^{k+1} = \mathcal P (\theta^k + a^k\nabla\theta^k ) \\
  &\lambda^{k+1} = \mathcal P (\lambda^k + a^k\nabla\lambda^k )
\end{aligned}$$

- the projection $\mathcal P$ can be computed very easily. Since the projection $(\tilde\lambda, \tilde\theta)$ onto $\mathcal D$ can be formulated as the model $\min_{\lambda\ge 0, \theta \ge 0, \lambda + \theta \le e} ||\tilde\lambda-\lambda||^2 + ||\tilde\theta - \theta||^2$, and solved analytically.



## Subproblem for each plane
The subproblem $\forall i\in I$ is defined as follows:

$$\begin{aligned}
c_t \equiv (h\theta_t - b\lambda_t) \\
\min_{\Omega_i} \sum_t c_t \cdot u_{i,t}
\end{aligned}$$

The model describes a problem to maximize total utility while keeping the lifespan safely away from the lower bound $L$. Define state: $y_t = \left[m_t,s_t \right]^\top$, where $m_t$ **denotes the remaining time of the undergoing maintenance**. $s_t$ is the remaining lifespan.

At each period $t$ we decide whether the plane $i$ is idle or waiting (for the maintenance), working, or starting a maintenance, i.e.: 

$$(u_t, x_t) \in \left\{(1, 0), (0,0), (0, 1)\right\}$$

We have the optimal equation:
$$V_n(u_t, x_t | m_t, s_t) = c_t \cdot u_t + \min_{u,x} V_{n-1}(...)$$

Complexity: let $s_0$ be the initial lifespan and finite time horizon be $|T|$, we notice the states for remaining maintenance waiting time is finite, $m_t \in \{0, 1, ..., \tau\}$. 

Let total number of possible periods to initiate a maintenance be $n_1$, and working periods be $n_2$. If we ignore lower bound $L$ on $s$, total number of possible values of $s$ is bounded above: $|s| = \sum_i^{|T|}\sum_j^{|T| - i} 1=(|T| + 1)(\frac{1}{2}|T| + 1)$ since $n_1 + n_2 \le |T|$. For each subproblem we have at most 3 actions, thus we conclude this problem can be solved by dynamic programming in polynomial time, the complexity is: $O\left(\tau\cdot|T|^3 \right)$

## Recovery of integral solution
compute $\min c ^\top | x - x^\star|$ where $x^\star$ is the (possibly) fractional solution achieving the best bound.

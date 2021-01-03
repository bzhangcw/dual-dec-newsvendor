---
header-includes:
  - |
    ```{=html}
    <script src="https://cdn.jsdelivr.net/npm/mermaid@8.4.0/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({ startOnLoad: true });</script>
    ```
  - |
    ```{=latex}
    \usepackage[UTF8, heading=true]{ctex}
    \definecolor{tufeijilk}{RGB}{68,87,151}
    \hypersetup{colorlinks=true,linkcolor=tufeijilk,urlcolor=cyan}
    ```
bibliography: [./repair.bib]
linkcitations: true
date: \today
author: Chuwen
---
# Progress summary

- Polynomial-time algorithm for deterministic problem:
  - The problem can be solved with subgradient method in polynomial time. If we allow tolerance $\epsilon \ge 0$ on subgradient method, the worst complexity is $O\left(\frac{1}{\epsilon^2}\cdot\tau\cdot|I|\cdot|T|^3\right)$. 
  - Converge and rate: 
    - we can only retrieve a feasible primal solution from the simplest subgradient method by @polyak_general_nodate.
    - Good approximation to optimal solution can be found via the volume algorithm by @barahona_volume_2000. 
    - The rate and convergence of such class of algorithm can be found in @nesterov_primal-dual_2009, @nedic_approximate_2009.
    - todo: try alternative formulation: $U^\top e - d + \epsilon_+ - \epsilon_- = 0$
  - Details: 
    - The subproblem at each subgradient iteration on dual problem can be solved by dynamic programming, at the cost of $O\left(\tau\cdot|T|^3 \right)$.
    - The dual variables can be solved **analytically**.
  - Computations has been done for DP, subgradient method (volume algorithm).

a quick look at the results ($|I| = 10, |T| = 20, 10$ randomly generated instances)

```{=latex}
\begin{tabular}{lrrrrr}
\toprule
{} &      sg\_lb &     sg\_val &   bench\_lb &  bench\_sol &  primal\_gap \\
\midrule
0 &  14.499735 &  17.533016 &  16.000000 &         16 &    0.095814 \\
1 &  32.631830 &  35.403596 &  31.979908 &         34 &    0.041282 \\
2 &   9.267048 &  12.402154 &   2.999999 &         10 &    0.240215 \\
3 &  52.727507 &  55.299756 &  49.496651 &         54 &    0.024070 \\
4 &   0.000000 &   4.745779 &   0.000000 &          0 &         inf \\
5 &  15.927653 &  16.950710 &  16.000000 &         16 &    0.059419 \\
6 &  50.000000 &  52.318332 &  50.000000 &         50 &    0.046367 \\
7 &   8.000000 &  10.682970 &   8.663961 &         10 &    0.068297 \\
8 &  34.000000 &  35.615792 &  32.916046 &         34 &    0.047523 \\
9 &  24.000000 &  25.193067 &  24.000000 &         24 &    0.049711 \\
\bottomrule
\end{tabular}
```
<!--
- infinite dimensional? so we can study the static
- risk measure instead of expectation?
- quadratic or any kind of differentiable function instead of a minimax
 -->

# The air-repair model

> Notation

- $I, T$ - set of plane, time periods, respectively 
- $b, h$ - demand withdraw and plane idle cost, respectively
- $\tau$ - lead time for maintenance
  
The demand is stochastic with some distribution $f\in \mathscr F$

- $\boldsymbol d_t$ - demand/number of planes needed at time $t$

> Decision

- $x_{it}$ - 0 - 1 variable, 1 if plane $i$ starts a maintenance at time $t$
- $u_{it}$ - 0 - 1 variable, 1 if plane is working at time $t$
- $s_{it} \ge 0$ - the lifespan of plane $i$ at time $t$

The DRO/SP model, the goal is to minimize unsatisfied demand and surplus (idle) flights, using a newsvendor-like objective function

$$\begin{aligned}
& q_t \equiv b \cdot (d_t - \sum_i u_{it})_+ + h \cdot  ( \sum_i u_{it} - d_t)_+  \\
  & \inf \max_{f\in \mathscr F}\mathbb E_f \left[ \sum_t q_t  \right] \\
  \mathbf{s.t.}  & \\
  & q_t \ge b\cdot \left (d_t - \sum_i u_{it} \right) & \forall t \in T \\
  & q_t \ge h\cdot \left (\sum_i u_{it} - d_t \right ) & \forall t \in T \\
  &  s_{i, t+1} =  s_{i t}  - \alpha_i  u_{it} + \beta_i  x_{i, t- \tau} & \forall i \in I, t \in T\\
  &  x_{it} +  u_{i, t} \le 1& \forall i \in I, t \in T\\
  &  x_{it} + x_{i\rho} + u_{i, \rho} \le 1& \forall i \in I,  t\in T, \rho = t + 1, ..., t+\tau \\
  &   s_{i t} \ge L& \forall i \in I, t \in T 
\end{aligned}$$

We define the last four sets of constraint as $\Omega_i$, which describe the non-overlapping requirements during a maintenance.

# Deterministic

We first consider the deterministic problem.

The problem can be solved with subgradient method in polynomial time and the solution is exact.  If we allow tolerance $\epsilon \ge 0$ on subgradient method, the complexity is:

$$O\left(\frac{1}{\epsilon^2}\cdot\tau\cdot|I|\cdot|T|^3\right)$$ 


## Subgradient method

Relax binding constraints of $q$


$$\begin{aligned}
  z_{\mathsf{LD}}(\lambda, \mu)& = \inf_{x, s, u} \left[ \sum_t 
      q_t (1-\lambda_t - \theta_t) + d_t(b\lambda_t -h \theta_t)
    + \sum_i \sum_t u_{i,t}(h\theta_t - b\lambda_t) \right] \\ 
  \mathbf {s.t. }  & \\
  & x_{(i,\cdot)}, u_{(i,\cdot)}, s_{(i,\cdot)} \in \Omega_i
\end{aligned}$$

$\Omega_i$ defined as the region of $x_{(i,\cdot)}, u_{(i,\cdot)}, s_{(i,\cdot)}, \forall i\in I$.

we notice $z_{\mathsf{LD}}(\lambda, \theta)$ is unbounded unless:
$$\lambda, \theta \in \{\lambda, \theta \ge 0 \big | (1-\lambda_t - \theta_t) \ge 0,\forall t\in T\}$$

we have:
$$\begin{aligned}
z_{\mathsf{LD}}(\lambda, \theta) = \sum_t 
      d_t(b\lambda_t -h \theta_t) + \inf_{x, s, u} \left[  \sum_i \sum_t u_{i,t}(h\theta_t - b\lambda_t) \right]
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

- the projection $\mathcal P$ can be computed very easily. Since the projection $(\tilde\lambda, \tilde\theta)$ onto $\mathcal D$ can be formulated as the model $\inf_{\lambda\ge 0, \theta \ge 0, \lambda + \theta \le e} ||\tilde\lambda-\lambda||^2 + ||\tilde\theta - \theta||^2$, and solved analytically.



## Subproblem for each plane
The subproblem $\forall i\in I$ is defined as follows:

$$\begin{aligned}
c_t \equiv (h\theta_t - b\lambda_t) \\
\inf_{\Omega_i} \sum_t c_t \cdot u_{i,t}
\end{aligned}$$

The model describes a problem to maximize total utility while keeping the lifespan safely away from the lower bound $L$. Define state: $y_t = \left[m_t,s_t \right]^\top$, where $m_t$ **denotes the remaining time of the undergoing maintenance**. $s_t$ is the remaining lifespan.

At each period $t$ we decide whether the plane $i$ is idle or waiting (for the maintenance), working, or starting a maintenance, i.e.: 

$$(u_t, x_t) \in \left\{(1, 0), (0,0), (0, 1)\right\}$$

We have the optimal equation:
$$V_n(u_t, x_t | m_t, s_t) = c_t \cdot u_t + \inf_{u,x} V_{n-1}(...)$$

Complexity: let $s_0$ be the initial lifespan and finite time horizon be $|T|$, we notice the states for remaining maintenance waiting time is finite, $m_t \in \{0, 1, ..., \tau\}$. 

Let total number of possible periods to initiate a maintenance be $n_1$, and working periods be $n_2$. If we ignore lower bound $L$ on $s$, total number of possible values of $s$ is bounded above: $|s| = \sum_i^{|T|}\sum_j^{|T| - i} 1=(|T| + 1)(\frac{1}{2}|T| + 1)$ since $n_1 + n_2 \le |T|$. For each subproblem we have at most 3 actions, thus we conclude this problem can be solved by dynamic programming in polynomial time, the complexity is: $O\left(\tau\cdot|T|^3 \right)$




# Stochastic

We use boldface notation to denote random variables. We let the vector $\boldsymbol q = [\boldsymbol q_1, ..., \boldsymbol q_{|T|}]^\top, \boldsymbol d = [\boldsymbol d_1,...,\boldsymbol d_{|T|}]^\top$, $\Xi_d$ be the support for $\boldsymbol{d}$. For simplicity, we let $\boldsymbol e$ be the vector of ones of corresponding dimension in matrix-vector calculations.

The DRO/SP model, the goal is to minimize worst-case expected unsatisfied demand and surplus (idle) flights

$$\begin{aligned}
  & \inf \sup_{f\in \mathscr F}\mathbb E_f \left[ \sum_t \boldsymbol q_t  \right] \\
  \mathbf{s.t.}  & \\
  & \boldsymbol q \ge b\cdot \left (\boldsymbol d - \boldsymbol U^\top \boldsymbol{e} \right) & \forall \boldsymbol d \in \Xi_d\\
  & \boldsymbol q \ge h\cdot \left ( \boldsymbol U^\top \boldsymbol{e}  - \boldsymbol d \right ) & \forall \boldsymbol d \in \Xi_d \\
  & \boldsymbol x_{(i,\cdot)}, \boldsymbol u_{(i,\cdot)}, \boldsymbol s_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$


Same relaxation scheme can be used on the DRO models:

- Mean-variance, in @delage_distributionally_2010.
- Likelihood, in @wang_likelihood_2016

<!-- ## Independent Demand

Suppose $\boldsymbol{d}_t, t = 1, ..., |T|$ is independent  -->

## Mean-variance
With moment uncertainty for $\boldsymbol d: \mathbb{E}(\boldsymbol d) = \mu_0, ...$, in @delage_distributionally_2010. The DRO model is equivalent to the following problem:

$$\begin{aligned}
\inf_{\boldsymbol{x}, \boldsymbol{Q}, \boldsymbol{\beta}, r, s} & \left(\gamma_{2} \boldsymbol{\Sigma}_{0}-\boldsymbol{\mu}_{0} \boldsymbol{\mu}_{0}^{\top}\right) \bullet \boldsymbol{Q}+r+\left(\boldsymbol{\Sigma}_{0} \bullet \boldsymbol{P}\right)-2 \boldsymbol{\mu}_{0}^{\top} \boldsymbol{p} + \gamma_{1} s \\
\mathbf { s.t. } & \\
& \boldsymbol{d}^{\top} \boldsymbol{Q} \boldsymbol{d} -\boldsymbol{d^\top\beta} + r \ge \sum_t \boldsymbol q_t & \forall \boldsymbol d \in \Xi_d \\
& \boldsymbol{Q} \succeq 0, \boldsymbol{\beta} \in \mathbb{R}^{|T|}, 
\begin{bmatrix}
  \boldsymbol{P} & \boldsymbol{p} \\
  \boldsymbol{p}^\top & s
\end{bmatrix} \succeq 0, \; 
\boldsymbol \beta = 2 (\boldsymbol p + \boldsymbol{Q\mu}_0)\\
& \boldsymbol q \ge b\cdot \left (\boldsymbol d - \boldsymbol U^\top \boldsymbol{e} \right) & \forall \boldsymbol d \in \Xi_d\\
  & \boldsymbol q \ge h\cdot \left ( \boldsymbol U^\top \boldsymbol{e}  - \boldsymbol d \right ) & \forall \boldsymbol d \in \Xi_d \\
& \boldsymbol x_{(i,\cdot)}, \boldsymbol u_{(i,\cdot)}, \boldsymbol s_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$

## Finite support and likelihood robust
The problem is, let $\boldsymbol Q = [\boldsymbol{q}^1, ..., \boldsymbol{q}^N]$

$$\begin{aligned}
  & \sup_{\beta, \theta, \Omega_i, \forall i} \theta + \beta \gamma +  \beta N - \underbrace{\beta \mathbf N^\top \log(\frac{\beta \mathbf N}{\boldsymbol{Q} e-\theta \mathbf 1})}_{\mathcal D_{KL}(\beta \mathbf N | \boldsymbol{Q} e-\theta \mathbf 1)}  \\
  \textbf {s.t.} \\
  & \beta \ge 0 \\
  & \boldsymbol{Q} e \ge \theta \mathbf 1 \\ 
  & \boldsymbol q^n \ge b\cdot \left (\boldsymbol d^n - \boldsymbol{U}^\top e \right) & \forall n = 1, ..., N\\
  & \boldsymbol q^n \ge h\cdot \left ( \boldsymbol{U}^\top e  -\boldsymbol d^n  \right ) & \forall n = 1, ..., N \\
  & \boldsymbol x_{(i,\cdot)}, \boldsymbol u_{(i,\cdot)}, \boldsymbol s_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$


Relax binding constraints for $\boldsymbol Q, \boldsymbol U$:
$$\boldsymbol z_{\mathsf{LD}} = \sup_{\boldsymbol Q} ...+ \sum_n (b\lambda^n - h\theta^n)^\top \boldsymbol{d}^n + \sum_n(\lambda^n +\theta^n)^\top q^n  \\
+ \sup_{\boldsymbol U}\sum_i\sum_t(\sum_nh\theta^n_t - b\lambda^n_t)\boldsymbol u_{it}$$

We can optimize for $\boldsymbol Q, \boldsymbol U$ separately, at each step, subproblems can be solved in polynomial time.

# Reference


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
    \usepackage{booktabs}
    \definecolor{tufeijilk}{RGB}{68,87,151}
    \hypersetup{colorlinks=true,linkcolor=tufeijilk,urlcolor=cyan}
    ```
bibliography: [./repair.bib]
linkcitations: true
date: \today
author: Chuwen
---


# Stochastic

```
this file is dedicated to some thoughts on stochastic properties
```

We want to show the same subgradient algorithm works for both dynamic and static models.

## Some review

Fruitful research has been done in the field of stochastic programming. Traditionally, stochastic programming approaches solve the expected objective that might be too optimistic. (see ...) Robust optimization, in contrast, optimizes a worst-case objective subject to the ambiguity set (see ...). Recently, the distributionally robust methods (see ...) provide a paradigm to minimize the worst-case risk ...

The multistage or dynamic models are known to be intractable, where at each stage decision is made after the realization of uncertain events. SAA... Furthermore, linear decision rules (LDR), see @, and @bertsimas_adaptive_2019 provides detailed analysis on LDR named after *adaptive distributionally robust optimization*.

We notice the stochastic version inherits the property that it could be decomposed into a set of independent subproblems by relaxing linking constraints. The idea regarding Lagrangian relaxation to dynamic optimization models is not new. @hawkins_langrangian_2003 develops the theory of Lagrangian relaxation on so-called *weakly coupled Markov decision process* with applications to queueing networks, supply-chain management problems, and multiarmed bandits, et cetera.  It provides analysis of both infinite and finite horizon versions of the problem.  @adelman_relaxations_2008 later contributes to the bound and optimality gap for both Lagrangian and linear programming relaxations.

## Dynamic / Multistage model


We now consider the optimization model under uncertainty.  Suppose demand $\boldsymbol{d}$ is random with respect to some unknown distribution $f \in \mathcal F$. Similarly, we wish to solve stochastic model that minimizes expected summation of shortages and surpluses deviated from the demand unfold within a finite horizon.

We use boldface notation to denote random variables and corresponding decision variables.  
Let $\Xi_d$ be the support for random variable $\boldsymbol{d}$. Let $\boldsymbol y = \left[\boldsymbol m,\boldsymbol s \right]$ be the variable under uncertainty.  Since $\boldsymbol y$ sufficiently represents the state at period $t$, we can write the multistage optimization model using dynamic programming equations.

Define $z_{t}$ is the optimal value with $t$ periods to go. We are interested in the expected value with known initial state $y_0$, consider the following multistage stochastic optimization problem:

$$z_T(y_0) = \min_{\boldsymbol\epsilon, \boldsymbol\delta, \boldsymbol U, \boldsymbol X}
\mathbb{E}_f \left[ \sum_t^{|T|}h \cdot \boldsymbol \epsilon_t + p \cdot \boldsymbol \delta_t \;\Big|\; y_0 \right ]$$

While the decisions are taken under conditions:
$$\sum_i \boldsymbol u_{it} - \boldsymbol\epsilon_t + \boldsymbol\delta_t = \boldsymbol{d}_t, \quad \\
\boldsymbol U_{(i,\cdot)}, \boldsymbol X_{(i,\cdot)}, \boldsymbol S_{(i,\cdot)} \in \Omega_i, \forall i\in I$$

Assume the data process $\boldsymbol d_1, ...,\boldsymbol d_t$ is Markovian, similar to the deterministic problem, the Bellman iteration can be written as:

$$\begin{aligned}
  V_{t}(\boldsymbol y, \boldsymbol{d}_t) & = 
\min_{\small{\boldsymbol\epsilon_t, \boldsymbol\delta_t, \boldsymbol u_{it}, \boldsymbol x_{it}}}  
h \cdot \boldsymbol \epsilon_t + p \cdot \boldsymbol \delta_t + \mathbb E_{f} \left [ V_{t-1}(\boldsymbol y', \boldsymbol{d}'_{t-1}) \big | \boldsymbol y, \boldsymbol{d}_t\right] \\
z_t(\boldsymbol y)& = \mathbb{E}_f\left[V_{t}(\boldsymbol y, \boldsymbol{d}_t)\right ]
\end{aligned}$$


We now investigate the Lagrangian relaxation. We let $z_t^\mathsf{LD}, V_t^\mathsf{LD}$ for the Lagrangian for $z, V$, respectively. The analysis is similar to existing results in @adelman_relaxations_2008, @hawkins_langrangian_2003. The difference lies in the fact that we do not enforce $\lambda_t$ to be identical across the stages $t = 1, ..., |T|$, which is convenient for infinite dimensional problems.


**Proposition 1.** Lagrangian relaxation provides a lower bound for any multiplier $\lambda = (\lambda_1, ..., \lambda_{|T|})$ such that $\lambda_t \in [-p, h],\; \forall t=1,..., |T|$.
$$V_{t}(\boldsymbol y, \boldsymbol d_t) \ge V_{t}^\mathsf{LD}(\boldsymbol y, \boldsymbol d_t) \equiv -\lambda_t \boldsymbol d_t + \sum_{i\in I} V_{it}(\boldsymbol y_i, \boldsymbol d_t)$$

Where $V_{it}$ is the optimal equation for each $i$

$$V_{it}(\boldsymbol y, \boldsymbol d_t) = \min_{\boldsymbol u_{it}, \boldsymbol x_{it}}   \boldsymbol u_{it} \lambda_t + \mathbb E_{f} \left [ V_{i,t-1}(\boldsymbol y', \boldsymbol{d}'_t) \big | \boldsymbol y, \boldsymbol{d}_t \right]$$

**PF.** Relax binding constraints, since any feasible solution to the primal problem is the solution to the relaxed problem, we have:

$$\begin{aligned}
  V_{t}(\boldsymbol y, \boldsymbol d_t) & \ge 
\min_{\small{\boldsymbol\epsilon_t, \boldsymbol\delta_t, \boldsymbol u_{it}, \boldsymbol x_{it}}}  
(h - \lambda_t )\cdot \boldsymbol \epsilon_t + (p + \lambda_t) \cdot \boldsymbol \delta_t 
+ \sum_i \boldsymbol{u}_{it} \lambda_t - \lambda_t \boldsymbol d_t
+ \mathbb E_{f} \left [ V_{t-1}(\boldsymbol y', \boldsymbol{d}'_t) \big | \boldsymbol y, \boldsymbol{d}_t \right ] \\
\end{aligned}$$

We set $\lambda_t \in [-p, h]$ otherwise RHS is unbounded, we have:

$$\begin{aligned}
  V_{t}(\boldsymbol y, \boldsymbol d_t) & \ge 
\min_{\small{\boldsymbol u_{it}, \boldsymbol x_{it}}}  
 \sum_i \boldsymbol{u}_{it} \lambda_t - \lambda_t \boldsymbol d_t
+ \mathbb E_{f} \left [ V_{t-1}(\boldsymbol y', \boldsymbol{d}'_t) \big | \boldsymbol y, \boldsymbol{d}_t\right] \\
& = - \lambda_t \boldsymbol d_t + \sum_{i\in I} V_{it}(\boldsymbol y_i, \boldsymbol d_t)
\end{aligned}$$

*The last line can be verified by induction similar to* @hawkins_langrangian_2003. This completes the proof. $\quad\blacksquare$

**Proposition 2.** $V_t^\mathsf{LD}(\boldsymbol y, \boldsymbol d_t)$ is convex in $\lambda_t$. Suppose $\boldsymbol u^\star_{it}, \boldsymbol x^\star_{it}$ is the solution to $V_{it}(\boldsymbol y)$, we have $\displaystyle\sum_i \boldsymbol u^\star_{it} - \boldsymbol d_t \in \partial V^\mathsf{LD}(\boldsymbol y, \boldsymbol d_t)$. 

**PF.** the convexity can be verified..., from @shapiro_lectures_2014


**Remark**: here multiplier $\lambda$ is still a function of $d$, i.e., $\lambda = \lambda(d)$, this is not good if we have infinite number of scenarios/realizations. Can we make $\lambda_t$ constant w.t. $d_t$?

 <!-- We first have to show this is convex, then maybe piecewise linear then the subgradient exists -->

a. try expectation (marginal distribution)

$$\begin{aligned}
  z_t^L(y) &  = \mathbb E_f 
  \left (-\lambda_t d_t + \sum_i V_{it}(y_i, d_t)\right ) 
  = \mathbb E \left [ - \lambda_td_t  + \sum_i  \min_{u_{it}}\lambda_t u_{it} 
  + \mathbb E_{f} \left [ V_{i,t-1}(\boldsymbol y', \boldsymbol{d}'_t) \big | \boldsymbol y, \boldsymbol{d}_t \right] \right ] \\
  & = ...
\end{aligned}$$

discrete case:

$$\begin{aligned}
  z_t^L(y) &  = \sum_{\eta \in \Xi_t} \mathbb \pi(\eta) \cdot (- \lambda_t d_t + \lambda_t \sum_i u_{it}^\star + V_{it}(\boldsymbol y', \eta')
\end{aligned}$$


## (Static) Distributionally Robust Model

For DRO model, the goal is to minimize worst-case expected unsatisfied demand and surplus (idle) flights

$$\begin{aligned}
  & \min \max_{f\in \mathscr F}\mathbb E_f  \left[e^\top( p \cdot\boldsymbol{\delta}  + h\cdot \boldsymbol \epsilon)\right] \\
  \mathbf{s.t.}  & \\
  & \boldsymbol{U} ^\top e + \boldsymbol \delta - \boldsymbol \epsilon  = \boldsymbol d & \forall \boldsymbol d \in \Xi_d\\
  & \boldsymbol U_{(i,\cdot)}, \boldsymbol X_{(i,\cdot)}, \boldsymbol S_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$


We show that same Lagrangian relaxation scheme can be applied to the DRO models and that the subgradient method produces approximation to the optimal value. 

- Mean-variance, in @delage_distributionally_2010.
- Likelihood, in @wang_likelihood_2016


### Moment Uncertainty
With moment uncertainty for $\boldsymbol d: \mathbb{E}(\boldsymbol d) = \mu_0, ...$, in @delage_distributionally_2010. The DRO model is equivalent to the following problem:

$$\begin{aligned}
\min_{\boldsymbol{U}, \boldsymbol{Q}, \boldsymbol{\beta}, r, s} & \left(\gamma_{2} \boldsymbol{\Sigma}_{0}-\boldsymbol{\mu}_{0} \boldsymbol{\mu}_{0}^{\top}\right) \bullet \boldsymbol{Q}+r+\left(\boldsymbol{\Sigma}_{0} \bullet \boldsymbol{P}\right)-2 \boldsymbol{\mu}_{0}^{\top} \boldsymbol{p} + \gamma_{1} s \\
\mathbf { s.t. } & \\
& \boldsymbol{Q} \succeq 0, \boldsymbol{\beta} \in \mathbb{R}^{|T|}, 
\begin{bmatrix}
  \boldsymbol{P} & \boldsymbol{p} \\
  \boldsymbol{p}^\top & s
\end{bmatrix} \succeq 0, \; 
\boldsymbol \beta = 2 (\boldsymbol p + \boldsymbol{Q\mu}_0)\\
& \boldsymbol{U} ^\top e + \boldsymbol \delta - \boldsymbol \epsilon  = \boldsymbol d & \forall \boldsymbol d \in \Xi_d\\
& \boldsymbol{d}^{\top} \boldsymbol{Q} \boldsymbol{d} -\boldsymbol{d^\top\beta} + r \ge e^\top( p \cdot\boldsymbol{\delta}  + h\cdot \boldsymbol \epsilon) & \forall \boldsymbol d \in \Xi_d \\
& \boldsymbol X_{(i,\cdot)}, \boldsymbol U_{(i,\cdot)}, \boldsymbol S_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$

semi-infinite constraints are equivalent to (substitute $\boldsymbol\epsilon = \boldsymbol u + \boldsymbol \delta - \boldsymbol d$，we have immediately)

$$\begin{bmatrix}
  \boldsymbol Q &  (he- \boldsymbol \beta)/2 \\
  (he- \boldsymbol \beta)^\top/2 & r - (h+p)e^\top \boldsymbol \delta - h e^\top   \boldsymbol U^\top e
\end{bmatrix} \succeq 0$$

wrap up:

$$\begin{aligned}
\min_{\boldsymbol{x}, \boldsymbol{Q}, \boldsymbol{\beta}, r, s} & \left(\gamma_{2} \boldsymbol{\Sigma}_{0}-\boldsymbol{\mu}_{0} \boldsymbol{\mu}_{0}^{\top}\right) \bullet \boldsymbol{Q}+r+\left(\boldsymbol{\Sigma}_{0} \bullet \boldsymbol{P}\right)-2 \boldsymbol{\mu}_{0}^{\top} \boldsymbol{p} + \gamma_{1} s \\
\mathbf { s.t. } & \\
& \boldsymbol{Q} \succeq 0, \boldsymbol{\beta} \in \mathbb{R}^{|T|}, 
\begin{bmatrix}
  \boldsymbol{P} & \boldsymbol{p} \\
  \boldsymbol{p}^\top & s
\end{bmatrix} \succeq 0, \; 
\boldsymbol \beta = 2 (\boldsymbol p + \boldsymbol{Q\mu}_0)\\
& \begin{bmatrix}
  \boldsymbol Q &  (he- \boldsymbol \beta)/2 \\
  (he- \boldsymbol \beta)^\top/2 & r - (h+p)e^\top \boldsymbol \delta - h e^\top   \boldsymbol U^\top e
\end{bmatrix} \succeq 0 \\
& \boldsymbol X_{(i,\cdot)}, \boldsymbol U_{(i,\cdot)}, \boldsymbol S_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$

### Finite support and likelihood robust
The problem is, let $\boldsymbol Q = [\boldsymbol{q}^1, ..., \boldsymbol{q}^N]$

$$\begin{aligned}
  & \max_{\beta, \theta, \Omega_i, \forall i} \theta + \beta \gamma +  \beta N - \underbrace{\beta \mathbf N^\top \log(\frac{\beta \mathbf N}{\boldsymbol{Q} e-\theta \mathbf 1})}_{\mathcal D_{KL}(\beta \mathbf N | \boldsymbol{Q} e-\theta \mathbf 1)}  \\
  \textbf {s.t.} \\
  & \beta \ge 0 \\
  & \boldsymbol{Q} e \ge \theta \mathbf 1 \\ 
  & \boldsymbol{U} ^\top e + \boldsymbol \delta - \boldsymbol \epsilon  = \boldsymbol d^n & \forall n = 1, ..., N \\
  & \boldsymbol x_{(i,\cdot)}, \boldsymbol u_{(i,\cdot)}, \boldsymbol s_{(i,\cdot)} \in \Omega_i & \forall i\in I
\end{aligned}$$


# Reference

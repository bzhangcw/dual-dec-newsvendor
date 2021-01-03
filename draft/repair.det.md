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

<!--
- infinite dimensional? so we can study the static
- risk measure instead of expectation?
- quadratic or any kind of differentiable function instead of a minimax
 -->

# The repair model

## Formulation

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

The DRO/SP model, the goal is to minimize unsatisfied demand and surplus (idle) flights. A minimax objective function that is widely used in Newsvendor problems can be written as follows:

$$\min_{u,x,s} b \cdot (d_t - \sum_i u_{it})_+ + h \cdot  ( \sum_i u_{it} - d_t)_+ $$

Alternatively, we use the following objective function with $\delta_t, \epsilon_t$ indicating unsatisfied demand and surplus, respectively. Let $z$ be the objective function


$$\begin{aligned}
  z = &\min_{x_{it}, u_{it}, \delta_t^+, \delta_t^-} \sum_t (b\cdot  \delta_t^+ + h \cdot \delta_t^-)\\
  \mathbf{s.t.}  & \\
  &  \sum_i u_{it} + \delta_t^+ - \delta_t^- = d_t& \forall t \in T \\
  &  s_{i, t+1} =  s_{i t}  - \alpha_i  u_{it} + \beta_i  x_{i, t- \tau} & \forall i \in I, t \in T\\
  &  x_{it} +  u_{i, t} \le 1& \forall i \in I, t \in T\\
  &  x_{it} + x_{i\rho} + u_{i, \rho} \le 1& \forall i \in I,  t\in T, \rho = t + 1, ..., t+\tau \\
  &   s_{i t} \ge L& \forall i \in I, t \in T 
\end{aligned}$$

We define the last four sets of constraint as $\Omega_i$, which describe the non-overlapping requirements during a maintenance for each $i$.  

Let $U, X, S \in \mathbb R^{|I|\times |T|}_+$ be the matrix of $u_{it}, x_{it}$ and $s_{it}$, $U_{(i,.)}$ be the $i$th row of $U$. Let $\delta, \epsilon$ be the vector of $\delta_t^+, \delta_t^-$, respectively. It allows a more compact formulation.

$$\begin{aligned}
  & \min_{U, X, S}  e^\top (b\cdot  \delta + h \cdot \epsilon)\\
  \mathbf{s.t.}  & \\
  &  U^\top e + \delta - \epsilon = d& \forall t \in T \\
  & X_{(i,\cdot)}, U_{(i,\cdot)}, S_{(i,\cdot)} \in \Omega_i & \forall i \in I 
\end{aligned}$$

We propose a polynomial-time approximation to this problem by Lagrangian relaxation and a subgradient method.  At each iteration of the dual search procedure, a set of sub-problems are solved by dynamic programming.  The convergence of any black-box subgradient method can be found in (@polyak_general_nodate, and books by Nesterov, Bertsimas, ... to be added), and the complexity are verified on the level of $O(\frac{1}{\epsilon^2})$. We refer further analysis on the rate and convergence of such class of algorithm to @nesterov_primal-dual_2009, @nedic_approximate_2009. Since regular sugradient method does not grant primal feasibility, there are methods...  We use the volume algorithm described in @barahona_volume_2000 to update the dual multipliers while approximating a primal feasible solutions to the linear relaxation.  The volume algorithm applied to our problem has further properties.  Besides the lower bound acquired in the dual relaxation, the convex combination of past iterations in the algorithm gives an upper bound to the original problem. This explicitly bounds the optimal value. Although the solution terminated at the subgradient method is not guaranteed to be integral, it gives a tight interval that asymptotically approaches to the optimal value.

If we allow a tolerance $\epsilon \ge 0$ on subgradient method, the worst overall complexity is $O\left(\frac{1}{\epsilon^2}\cdot\tau\cdot|I|\cdot|T|^3\right)$. 

## Lagrangian Relaxation

```
todo
- can do better on complexity
```

The Lagrangian is introduced by relaxing the equality constraint, so we have:

$$\begin{aligned} 
z_{\mathsf{LD}}  &= - \sum_t \lambda_t d_t + \min_{\delta_t^+, \delta_t^-, U} \sum_t \left [ (b + \lambda_t) \cdot \delta_t^+ + (h-\lambda_t)\cdot \delta_t^- \right ] + \sum_i \sum_t\lambda_t u_{it} \\
 \end{aligned}$$

$z_{\mathsf{LD}}(\lambda)$ is unbounded unless $-b \le \lambda_t \le h$, it reduces to a set of low dimensional minimization problems for each $i$:


$$\begin{aligned}
  z_{\mathsf{LD}} &= - \sum_t \lambda_t d_t  + \min_{U}\sum_i \sum_t\lambda_t u_{it} \\ 
  \mathbf {s.t. }  & \\
  & X_{(i,\cdot)}, U_{(i,\cdot)}, S_{(i,\cdot)} \in \Omega_i \\
  & -b \le \lambda_t \le h
\end{aligned}$$

Next we provide analysis on properties of the subproblem.

### Subproblem for each plane


In the dual search process, one should solve a set of subproblems $\forall i\in I$ defined as follows:

$$\begin{aligned}
\min_{\Omega_i} \sum_t \lambda_t \cdot u_{i,t}
\end{aligned}$$

The model describes a problem to minimize total cost while keeping the lifespan safely away from the lower bound $L$.  We solve this by dynamic programming.  

Define state: $y_t = \left[m_t,s_t \right]^\top$, where $m_t$ **denotes the remaining time of the undergoing maintenance**. $s_t$ is the remaining lifespan.  At each period $t$ we decide whether the plane $i$ is idle or waiting (for the maintenance), working, or starting a maintenance, i.e.: 

$$(u_t, x_t) \in \left\{(1, 0), (0,0), (0, 1)\right\}$$

We have the Bellman equation:
$$V_n(u_t, x_t | m_t, s_t) = \lambda_t \cdot u_t + \min_{u,x} V_{n-1}(...)$$

Complexity: let $s_0$ be the initial lifespan and finite time horizon be $|T|$, we notice the states for remaining maintenance waiting time is finite, $m_t \in \{0, 1, ..., \tau\}$. 

Let total number of possible periods to initiate a maintenance be $n_1$, and working periods be $n_2$. If we ignore lower bound $L$ on $s$, total number of possible values of $s$ is bounded above: $|s| = \sum_i^{|T|}\sum_j^{|T| - i} 1=(|T| + 1)(\frac{1}{2}|T| + 1)$ since $n_1 + n_2 \le |T|$. For each subproblem we have at most 3 actions, thus we conclude this problem can be solved by dynamic programming in polynomial time, the complexity is: $O\left(\tau\cdot|T|^3 \right)$

### Subgradient Method

Lagrange multipliers is updated by a subgradient method. (volume algorithm, etc.)

Note at each iteration $k$, optimal solution for $z_{\textsf{LD}}^k$ is $(\epsilon_t)^\star = (\delta_t)^\star = 0$, we use the following (heuristic) procedure to retrieve primal feasible solution:

$$\begin{aligned}
  &(\epsilon)^k = \max\{0, (U^k)^\top e - d\} \\
  &(\delta)^k = \max\{0, d - (U^k)^\top e\}
\end{aligned}$$

**The Volume Algorithm HERE**


Notice:

- At iteration $k$, suppose $-b \le \lambda^k_t \le h, \forall t \in T$, we use dynamic programming to solve the relaxed minimization problem, then the (integral) solution $( X^k,  S^k,  U^k)$ is also feasible for the original problem (compute $\delta, \epsilon$ accordingly). The primal value $z^k$ is the upper bound for optimal solution $z^\star$:  $z^k\ge z^\star$.

- In the volume algorithm, we consider the convex combination $\bar X$ of past iterations $\{X^1, ..., X^k\}$.  We update $\bar X \leftarrow \alpha X^k  + (1-\alpha) \bar X$.  It's easy to verify $\bar z \ge z^\star \ge z_{\textsf{LD}}^k$, where  $\bar z$ is the primal objective value for $\bar X$ and $z_{\textsf{LD}}^k$ is the dual value for $X^k$. By the termination criterion $|\bar z - z_{\textsf{LD}}^k| \le \epsilon_z$ for some small value $\epsilon_z >0$, we conclude the $\bar z$ converges to the optimal value $z^\star$.

- While $\bar z \to z^\star$, there is no guarantee for the solution $\bar
X, \bar U$ being integral via the volume algorithm; $\bar
X, \bar U$ is feasible only to the linear relaxation.

- Remark: 
  - The projection for dual variables is simple since there is only a box constraint. More computation would be needed if we use the minimax objective function, i.e., $q \ge h\cdot (U^\top e - d), q\ge b\cdot (d-U^\top e)$, in which case two set of multipliers are needed, say $\lambda, \mu \ge 0$, and the projection should be done onto:
    $$\{(\lambda,\mu)|\lambda +\mu \le 1\}$$

### Rounding

- *compute $\min c ^\top | x - x^\star|$ where $x^\star$ is the (possibly) fractional solution achieving the best bound, using DP. 

still working on this.

### Numerical Experiments

In this section, In this section, we report numerical results to demonstrate the efficiency and effectiveness of our proposed algorithms for solving the repair problem (**ref here**). We parallelize the subproblems to available cores solved by dynamic programming.

(details on the algorithm, parameters, et cetera.)

#### Convergence of Lagrange Relaxation
We randomly generated 5-8 instances for each problem class with size $|I| = 10, 15, 20$ and $|T| = 25, 30$. We use Gurobi 9.1 to compute benchmarks: lower bound $\mathsf{bench\_lb}$ and primal objective value $\mathsf{bench\_sol}$ within 300 seconds.  The value and bound for subgradient methods are $\mathsf{subgrad\_val}$, $\mathsf{subgrad\_lb}$, respectively. We set the maximum iterations to 400 so that the subgradient method terminates at a comparable time with Gurobi. At last, we compare $\mathsf{primal\_gap}$ and $\mathsf{bound\_gap}$ in the last two columns.  All the computations have been performed on a Mac mini (2018) with 3.2 GHz 6-Core Intel Core i7 processor and a RAM of 32 GB.

It can be observed that the subgradient method performed closely to commercial mixed-integer linear solver.  

```{=latex}
\begin{table}
\caption{Computational results on convergence to optimal solution $z^\star$} \label{tab:sgsconv} 
\begin{tabular}{|l|l|r|r|r|r|l|l|}
\toprule
 $|I|$ & $|T|$ & $\mathsf{bench\_lb}$ &  $\mathsf{bench\_sol}$ & $\mathsf {subgrad\_val}$ &  $\mathsf{subgrad\_lb}$ & $\mathsf{primal\_gap}$ & $\mathsf{bound\_gap}$ \\
\midrule
 15 &  25 &   50.545103 &   52.000000 &    51.567854 &   50.593575 &     -0.83\% &     0.10\% \\
 20 &  25 &   58.583531 &   76.000000 &    70.658525 &   69.975157 &     -7.03\% &    19.45\% \\
 20 &  25 &  144.000000 &  144.000000 &   144.715790 &  143.375955 &      0.50\% &    -0.43\% \\
 10 &  30 &   50.160760 &   52.000000 &    52.366787 &   52.000000 &      0.71\% &     3.67\% \\
 10 &  30 &   50.000000 &   50.000000 &    50.394692 &   50.000000 &      0.79\% &     0.00\% \\
 15 &  25 &   88.000000 &   88.000000 &    88.725505 &   88.000000 &      0.82\% &     0.00\% \\
 10 &  25 &   49.999998 &   49.999998 &    50.420987 &   50.000000 &      0.84\% &     0.00\% \\
 10 &  25 &   48.968605 &   50.000000 &    50.422554 &   50.000000 &      0.85\% &     2.11\% \\
 10 &  30 &   81.999998 &   82.000000 &    82.718656 &   81.938236 &      0.88\% &    -0.08\% \\
 20 &  25 &   52.198486 &   53.999995 &    54.480932 &   53.974198 &      0.89\% &     3.40\% \\
 20 &  25 &  146.000000 &  146.000000 &   147.319376 &  145.898549 &      0.90\% &    -0.07\% \\
 20 &  25 &  118.000000 &  118.000000 &   119.063879 &  118.000000 &      0.90\% &     0.00\% \\
 15 &  25 &   88.000000 &   88.000000 &    88.788297 &   88.000000 &      0.90\% &     0.00\% \\
 10 &  30 &   28.507084 &   30.000000 &    30.268855 &   30.000000 &      0.90\% &     5.24\% \\
 20 &  25 &  136.236668 &  138.000000 &   139.251805 &  137.915722 &      0.91\% &     1.23\% \\
 10 &  30 &   86.655991 &   88.000000 &    88.818326 &   88.000000 &      0.93\% &     1.55\% \\
 10 &  30 &   60.000000 &   60.000000 &    60.565028 &   60.000000 &      0.94\% &     0.00\% \\
 10 &  25 &   72.000000 &   72.000000 &    72.698958 &   72.000000 &      0.97\% &     0.00\% \\
 15 &  25 &   84.000000 &   84.000000 &    84.837668 &   84.000000 &      1.00\% &     0.00\% \\
 10 &  30 &   44.775258 &   50.000000 &    50.583272 &   49.454663 &      1.17\% &    10.45\% \\
 10 &  25 &   40.000000 &   40.000000 &    40.766048 &   39.747977 &      1.92\% &    -0.63\% \\
 10 &  30 &   33.175978 &   35.999999 &    36.747449 &   34.966511 &      2.08\% &     5.40\% \\
 10 &  25 &    9.386239 &   14.000000 &    14.342575 &   14.000000 &      2.45\% &    49.15\% \\
 15 &  25 &   34.000000 &   34.000000 &    35.802835 &   34.000000 &      5.30\% &     0.00\% \\
\bottomrule
\end{tabular}
\small 
\end{table}
```

# Analysis




# Reference


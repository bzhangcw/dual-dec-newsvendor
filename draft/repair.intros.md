---
author: Chuwen Zhang
link-citations: true
# === Latex options ===
fontsize: 10pt
title: "A fleet maintenance problem"
bibliography: [./repair.bib]
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

---

# Fleet maintenance problem


## Similar Problems and Related Literature

### Workforce scheduling and rostering
Workforce scheduling and rostering is very similar to our problem. While scheduling generally considers the size of the workforce for each shift where the robustness is usually considered, the rostering counterpart assigns employees to fill the tasks. 

First, determine the number of agents to be assigned to each shift or time period. This is usually referred to as "shift scheduling" or simply "scheduling". See the review on scheduling with nondeterministic demand, @defraeye_staffing_2016. The robustness can usually be ensured by imposing chance constraints on service levels induced from arrival rate. See @liao_distributionally_2013, @excoffier_joint_2016, @gans_parametric_2015
  
Second, a rostering procedure combines shifts into rosters and assigns rosters to individual employees. See a review on deterministic rostering problem: @burke_state_2004, @de_causmaecker_categorisation_2011. As for robust rostering, see a computational example in @zhao_exact_2012. 

Our maintenance model serves like a combination of both.

### Air maintenance scheduling

Starting from the review paper:

- Aircraft maintenance operations: state of the art, see @van_den_bergh_aircraft_2013

There is one very similar to our model, see @sanchez_optimisation_2020. It models engine status as a continuous variable $0\le s\le 1$ where $s = 1$ corresponds to perfect working condition. Minor difference, the maintenance intervals are predefined.

No known robust or stochastic version.

### Generator/power plant maintenance scheduling

The problem involves key decision of starting maintenance for a group of generators in power plants, say $x_{it}$, in discrete time periods. Usually the generator is allowed to be repaired **at most once** in the horizon. Do not consider recurrent maintenance.

recent studies:

- MILP or Binary QP: Using a Bender's decomposition  @canto_application_2008. Using meta-heuristics, @dahal_gasa-based_2000, @dahal_generator_2007


### Unit commitment

A little bit similar to Hydro-Thermal UC problem (compare the dynamics of reservoir to lifespan dynamics). While in our model, There is a lead-time in the dynamic equations.

- well-studied deterministic problem.

- plenty of resources on stochastic and robust version of UC.


## Inventory theory

The problem falls into the category of multi-item, multi-period models. 


# Problem Description
A fleet has a set of airplanes to operate flight tasks between destinations. 

The lifespan of a plane decreases if it is scheduled with flights. Once the lifespan reaches a safety lower bound, the plane cannot be assigned to any task and a maintenance plan is initiated immediately. The plane comes back from repair operations after a fixed amount of time, then the condition is restored with lifespan prolonged. Account for uncertainty, a group of backup planes rent from other companies are and kept at the base. Furthermore, a relatively large cost is charged if current running fleet are insufficient to meet the demand.

We denote for each time period $t \in T$, number of planes needed for operation is $D_t$. For each plane $i$ in the fleet $I$, at each time period, decreased lifespan is $\alpha_i$ is static. The plane comes back from maintenance after time $\tau$, then current lifespan is prolonged by a fixed amount $\beta_i$. Once the lifespan hits lower bound $L_i$, the plane is not allowed for assignments.

The goal is to satisfy task requirements while keeping a low backup level at the base. We wish to make a plan to schedule the maintenance and to minimize total number of backup and idle planes.

## Formulations

> Notation

- $I, T$ - set of plane, time periods, respectively 
- $h_i, c_i$ - holding and maintenance cost
- $r, \rho$ -  rent / unsatisfied demand cost per period

The demand is stochastic with some distribution $f\in \mathscr F$

- $\tilde D_t$ - demand/number of planes needed at time $t$

> Decision

- $x_{it}$ - 0 - 1 variable, 1 if plane $i$ is at base (not working)
- $u_{it}$ - 0 - 1 variable, 1 if plane $i$ is assigned to work
- $m_{it}$ - 0 - 1 variable, 1 if plane $i$ starts a maintenance
- $s_{it}$ - the lifespan of plane $i$ at time $t$
- $v_{t}$ - number of unsatisfied demand
- $p$ - number of backup planes
 
The DRO/SP model:


$$\begin{aligned}
  & \inf \max_{f\in \mathscr F} \mathbb E_f\big[r\cdot p + \sum_t\rho  \cdot  v_t + \sum_{i,t}h_i \cdot  x_{it} + \sum_{i,t}c_i \cdot m_{it}\big ]\\
  \mathbf{s.t. }  & \\
  & s_{i, t+1} - s_{i t} = \alpha_i u_{it} - \beta_i m_{i, t- \tau} \\
  & m_{i, t- \tau} + x_{it} + u_{it}= x_{i,t+1} + m_{i, t+1} + u_{i,t+1}\\
  & s_{it} \ge L\cdot u_{it} \\
  & \sum_i u_{it} + v_t + p \ge \tilde  D_t\\
  & x_{it},m_{it},u_{it} \in \{0, 1\},\; \forall i\in I, t \in T\\
  & s_{it}\ge 0,\; \forall i\in I, t \in T\\
  &  p \ge 0,\; v_t \ge 0,\; \forall t
\end{aligned}$$ 

The first set of constraints track the lifespan for each plane. The second set describes the status of a plane must be one of the following: at base, occupied, start a maintenance, and at maintenance. The next set requires immediate overhaul once the lower bound is reached. We have the demand constraint at last. May need extra constraints to make sense (budget, etc.)

## Note and todo

### Two stage? 

At first stage we decide number of rent planes for backup, then at second stage we decide the operation plans.

### Algorithm for deterministic model

The model can be decomposed by relaxing the demand constraints, then solve a subproblem for each plane individually. The subproblem should be very easy to solve.


# Vasicek Bond Pricing Calculator


This repository implements an advanced bond pricing solver under the Vasicek interest rate model using:
1. Monte Carlo simulation with control variates for variance reduction.
2. Quasi-Monte Carlo (QMC) via Sobol sequences for faster convergence.

This approach is known to significantly improve accuracy while reducing computational cost compared to traditional Monte Carlo methods.

---

## Background: Vasicek Model and Bond Pricing

The Vasicek model describes the evolution of interest rates using the stochastic differential equation (SDE):

\[
dr_t = \kappa (\theta - r_t) dt + \sigma dW_t
\]

where:
- \( r_t \) = short-term interest rate at time \( t \),
- \( \kappa \) = speed of mean reversion,
- \( \theta \) = long-term mean interest rate,
- \( \sigma \) = volatility of interest rate,
- \( dW_t \) = Wiener process (Brownian motion).

The zero-coupon bond price under the Vasicek model has a closed-form solution:

\[
P(0,T) = A(T) e^{-B(T) r_0}
\]

where:

\[
B(T) = \frac{1 - e^{-\kappa T}}{\kappa}
\]

\[
A(T) = \exp \left( \left( \theta - \frac{\sigma^2}{2\kappa^2} \right) (B(T) - T) - \frac{\sigma^2}{4\kappa} B(T)^2 \right)
\]

This analytical solution is used as a control variate to improve Monte Carlo estimates.

---

## Overall features

✅ Monte Carlo Simulation; Estimates bond price using thousands of stochastic rate paths.  
✅ Control Variates; Uses analytical Vasicek bond price to reduce variance.  
✅ Quasi-Monte Carlo with Sobol sequences*; Faster convergence vs. traditional Monte Carlo.  
✅ Automatic simulation capping; Limits simulations to \(2^{16} = 65536\) to avoid excessive computation.  

---



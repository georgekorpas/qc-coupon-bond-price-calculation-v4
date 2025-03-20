import numpy as np
import scipy.stats as stats
import json

# Fixed parameters for the Vasicek model
KAPPA = 0.1  # Mean reversion speed
THETA = 0.03  # Long-term mean interest rate
MAX_SIMULATIONS = 2**16  # 65,536 max limit

def vasicek_bond_price(T, r0, sigma, kappa, theta):
    """
    Computes the theoretical zero-coupon bond price under the Vasicek model.
    This serves as a control variate for variance reduction in Monte Carlo.
    """
    B_T = (1 - np.exp(-kappa * T)) / kappa
    A_T = np.exp((theta - (sigma ** 2) / (2 * kappa ** 2)) * (B_T - T) - (sigma ** 2) * (B_T ** 2) / (4 * kappa))
    return A_T * np.exp(-B_T * r0)

def next_power_of_2(n):
    """Rounds `n` up to the nearest power of 2, capped at MAX_SIMULATIONS."""
    return min(2 ** int(np.ceil(np.log2(n))), MAX_SIMULATIONS)

def generate_sobol_sequence(dim, num_samples):
    """
    Generates Sobol low-discrepancy sequences for Quasi-Monte Carlo simulation.
    """
    from scipy.stats.qmc import Sobol
    sobol = Sobol(d=dim, scramble=True)  # Scrambled Sobol for better uniformity
    return sobol.random(num_samples)

def simulate_short_rate_quasi_mc(total_time, initial_rate, volatility, num_simulations, time_step=0.01):
    """
    Simulates short rate evolution using a Vasicek-like model with Quasi-Monte Carlo sampling.
    """
    num_steps = int(round(total_time / time_step))
    time_grid = np.linspace(0, total_time, num_steps + 1)

    # Generate Sobol sequence for better sampling
    sobol_samples = generate_sobol_sequence(num_steps, num_simulations)
    normal_samples = stats.norm.ppf(sobol_samples)  # Convert to normal distribution

    rate_paths = np.full((num_simulations, num_steps + 1), initial_rate)

    for step in range(1, num_steps + 1):
        dW = normal_samples[:, step - 1] * np.sqrt(time_step)
        dr = KAPPA * (THETA - rate_paths[:, step - 1]) * time_step + volatility * dW
        rate_paths[:, step] = rate_paths[:, step - 1] + dr

    return rate_paths, time_grid

def compute_discount_factors(rate_paths, time_grid):
    """
    Computes discount factors using numerical integration.
    """
    dt = np.diff(time_grid)
    integral = np.cumsum(rate_paths[:, :-1] * dt, axis=1)
    discount_factors = np.exp(-integral)
    return discount_factors

def monte_carlo_bond_price(total_time, initial_rate, volatility, num_simulations, time_step=0.01):
    """
    Computes bond prices using Monte Carlo with Control Variates and Quasi-Monte Carlo.
    """
    rate_paths, time_grid = simulate_short_rate_quasi_mc(total_time, initial_rate, volatility, num_simulations, time_step)
    discount_factors = compute_discount_factors(rate_paths, time_grid)

    # Monte Carlo estimation
    final_discount_factors = discount_factors[:, -1]
    mc_estimate = np.mean(final_discount_factors)

    # Control variate adjustment using Vasicek model
    closed_form_price = vasicek_bond_price(total_time, initial_rate, volatility, KAPPA, THETA)
    adjusted_mc_estimate = mc_estimate - (np.mean(final_discount_factors) - closed_form_price)

    # Variance computation
    variance = np.var(final_discount_factors)

    return round(float(adjusted_mc_estimate), 10), round(float(variance), 10)

def run(input_data, solver_params=None, extra_arguments=None):
    """
    Runs the bond pricing simulation using the improved Monte Carlo method.
    """
    initial_rate = input_data["Initial Interest Rate"]
    volatility = input_data["Volatility"]
    bond_maturity = input_data["Maturity Time"] / 12  # Convert months to years

    # Retrieve NumberOfSimulations from input.json and round to nearest power of 2, capping at MAX_SIMULATIONS
    original_num_simulations = solver_params.get("NumberOfSimulations", 10000)  # Default: 10,000 (if missing from input.json)
    num_simulations = next_power_of_2(original_num_simulations)

    # Compute bond price statistics
    estimated_price, variance = monte_carlo_bond_price(bond_maturity, initial_rate, volatility, num_simulations)

    return {
        "bond_price": estimated_price,
        "variance": variance
    }
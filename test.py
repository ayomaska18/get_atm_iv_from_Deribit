import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def heston_model_simulation(data, period, T=1.0, N=None):
    """
    Simulate the Heston model given the ETH/USDT price ratio data and lookback period.
    
    Parameters:
    - data: DataFrame containing the price ratio data with 'Timestamp' and 'Price Ratio' columns.
    - period: Lookback period for the rolling window.
    - T: Time horizon for the simulation (default: 1 year).
    - N: Number of time steps (if None, will default to high-frequency steps).
    
    Returns:
    - t: Time array.
    - S: Simulated ETH/USDT price array.
    - V: Simulated variance array (scaled to percentage).
    """
    
    def estimate_heston_parameters(price_data):
        # Here you would implement a method to estimate the Heston model parameters
        # using historical price data. This can be done using the method of moments,
        # maximum likelihood estimation, or other statistical techniques.
        # For simplicity, we return hardcoded values.
        S0 = price_data['Price Ratio'].iloc[-1]  # Last price as initial price
        V0 = np.var(price_data['log_return'])  # Variance of log returns as initial variance
        mu = np.mean(price_data['log_return'])  # Mean of log returns as drift
        kappa = 2.0  # Rate of mean reversion
        theta = V0  # Long-term variance
        sigma = 0.1  # Volatility of variance
        rho = -0.7  # Correlation between asset price and variance
        return S0, V0, mu, kappa, theta, sigma, rho

    # Convert Timestamp column to datetime data type
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    data['log_return'] = np.log(data['Price Ratio'] / data['Price Ratio'].shift(1))
    data.dropna(subset=['log_return'], inplace=True)

    # Estimate parameters
    S0, V0, mu, kappa, theta, sigma, rho = estimate_heston_parameters(data)

    # Set default number of time steps if not provided
    if N is None:
        N = 252 * 6 * 24 * 60  # Number of time steps (6 intervals per minute, 60 minutes per hour, 24 hours per day, 252 trading days)

    dt = T / N  # Time step
    S = np.zeros(N)
    V = np.zeros(N)
    t = np.linspace(0, T, N)
    S[0] = S0
    V[0] = V0
    np.random.seed(42)
    for i in range(1, N):
        Z1 = np.random.normal()
        Z2 = np.random.normal()
        W1 = np.sqrt(dt) * Z1
        W2 = np.sqrt(dt) * (rho * Z1 + np.sqrt(1 - rho ** 2) * Z2)
        S[i] = S[i-1] * np.exp((mu - 0.5 * V[i-1]) * dt + np.sqrt(V[i-1]) * W1)
        V[i] = np.abs(V[i-1] + kappa * (theta - V[i-1]) * dt + sigma * np.sqrt(V[i-1]) * W2)

    # Convert variance to percentage
    V *= 100

    return t, S, V

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

# Example usage
lookback_period = 150  # Example lookback period
t, S, V = heston_model_simulation(data, lookback_period)

# Plot the results
fig, ax1 = plt.subplots(figsize=(14, 7))

color = 'tab:blue'
ax1.set_xlabel('Time')
ax1.set_ylabel('ETH/USDT Price', color=color)
ax1.plot(t, S, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Variance (%)', color=color)
ax2.plot(t, V, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  
plt.title('Heston Model Simulation for ETH/USDT Price Ratio')
plt.show()

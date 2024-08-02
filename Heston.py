import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

csv_file_atm_iv = 'atm_iv_ETH.csv'
data_atm_iv = pd.read_csv(csv_file_atm_iv)

def atm_iv(data, period:int):
    lookback_period = str(period) + 'T'
    start_date='2024-07-18'
    df = data.copy()
    # Convert Timestamp column to datetime data type
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    df = df[df['Timestamp'] >= pd.to_datetime(start_date)]

    # Turn atm iv into numeric
    df['ATM IV'] = pd.to_numeric(df['ATM IV'], errors='coerce')

    # Drop N/A columns
    df.dropna(subset=['ATM IV'], inplace=True)

    df.set_index('Timestamp', inplace=True)
    resampled_data = df.resample(lookback_period).mean().reset_index()

    return resampled_data



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

data5 = vol_by_heston(data.copy(), 150)
data6 = vol_by_heston(data.copy(), 200)
data7 = vol_by_heston(data.copy(), 250)
# data8 = vol_by_garch(data.copy(), 300)
atm_iv_data_1 = atm_iv(data_atm_iv.copy(), 150)
atm_iv_data_2 = atm_iv(data_atm_iv.copy(), 200)
atm_iv_data_3 = atm_iv(data_atm_iv.copy(), 250)
# atm_iv_data_4 = atm_iv(data_atm_iv.copy(), 300)

fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(data5['Timestamp'], data5['heston_vol'], label='Period 150', color='blue')
ax.plot(data6['Timestamp'], data6['heston_vol'], label='Period 200', color='purple')
ax.plot(data7['Timestamp'], data7['heston_vol'], label='Period 250', color='black')
# ax.plot(data8['Timestamp'], data8['garch_vol'], label='Period 300', color='grey')
ax.plot(atm_iv_data_1['Timestamp'], atm_iv_data_1['ATM IV'], label='atm_iv_150', color='red')
ax.plot(atm_iv_data_2['Timestamp'], atm_iv_data_2['ATM IV'], label='atm_iv_200', color='orange')
ax.plot(atm_iv_data_3['Timestamp'], atm_iv_data_3['ATM IV'], label='atm_iv_250', color='yellow')
# ax.plot(atm_iv_data_4['Timestamp'], atm_iv_data_4['ATM IV'], label='atm_iv_300', color='green')


plt.xlabel('Time')
plt.ylabel('Annualized Volatility (%)')
plt.title('Different Period Rolling Heston Model')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('diff_lookback_heston.png', dpi=300)
plt.show()

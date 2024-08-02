import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model
from sklearn.metrics import mean_squared_error

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

def vol_by_garch(data, period):
    lookback_period = str(period) + 'T'
    df = data.copy()
    # Convert Timestamp column to datetime data type
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    start_date='2024-07-18'
    df = df[df['Timestamp'] >= pd.to_datetime(start_date)]

    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))

    # Fit GARCH(1,1) model
    garch_model = arch_model(df['log_return'].dropna(), vol='Garch', p=1, q=1)
    garch_fit = garch_model.fit(disp='off')

    # Extract conditional volatility (annualized)
    intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
    df['garch_vol'] = garch_fit.conditional_volatility * np.sqrt(intervals_per_year) * 100

    df.set_index('Timestamp', inplace=True)
    resampled_data = df.resample(lookback_period).mean().reset_index()

    return resampled_data

lookback_periods = [200, 300, 400]
scaling_factors = [1, 2, 3, 4]


fig, axes = plt.subplots(3, 4, figsize=(20, 15), sharex=True, sharey=True)

fig.suptitle('GARCH Volatility Model', fontsize=16)

for i, period in enumerate(lookback_periods):
    garch_vol_data = vol_by_garch(data.copy(), period)
    atm_iv_data = atm_iv(data_atm_iv.copy(), period)
    
    for j, scaling_factor in enumerate(scaling_factors):
        # Adjust the forecasted volatility
        garch_vol_data[f'adjusted_garch_vol_{j}'] = garch_vol_data['garch_vol'] * scaling_factor

        # Calculate MSE and RMSE for adjusted volatility
        merged_data = pd.merge(garch_vol_data[['Timestamp', f'adjusted_garch_vol_{j}']], atm_iv_data[['Timestamp', 'ATM IV']], on='Timestamp', how='inner')
        mse = mean_squared_error(merged_data['ATM IV'], merged_data[f'adjusted_garch_vol_{j}'])
        rmse = np.sqrt(mse)

        print(f'Lookback Period: {period} min, Scaling Factor: {scaling_factor}')
        print(f'MSE: {mse:.4f}')
        print(f'RMSE: {rmse:.4f}')

        # Plot the data
        ax = axes[i, j]
        ax.plot(garch_vol_data['Timestamp'], garch_vol_data[f'adjusted_garch_vol_{j}'], label=f'Adjusted GARCH Vol (x{scaling_factor})', color='blue')
        ax.plot(atm_iv_data['Timestamp'], atm_iv_data['ATM IV'], label='ATM IV', color='orange')
        ax.set_title(f'Period: {period} min, Scale: x{scaling_factor}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.legend()
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='upper right')

        textstr = f'MSE: {mse:.4f}\nRMSE: {rmse:.4f}'
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))


plt.tight_layout()
plt.savefig('diff_lookback_garch.png', dpi=300)
plt.show()

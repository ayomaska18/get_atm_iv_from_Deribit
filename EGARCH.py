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


def vol_by_egarch(data, period):
    lookback_period = str(period) + 'T'
    df = data.copy()

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    start_date='2024-07-18'
    df = df[df['Timestamp'] >= pd.to_datetime(start_date)]

    df.sort_values('Timestamp', inplace=True)

    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    
    # Fit EGARCH(1,1) model
    egarch_model = arch_model(df['log_return'].dropna(), vol='EGarch', p=1, q=1, rescale=False)

    egarch_fit = egarch_model.fit(disp='off')
    
    # Extract conditional volatility (annualized)
    intervals_per_year = 365 * 24 * 60 * 6  # Annualize the volatility
    df['egarch_vol'] = egarch_fit.conditional_volatility / 10000 * np.sqrt(intervals_per_year) * 100

    df.set_index('Timestamp', inplace=True)
    resampled_data = df.resample(lookback_period).mean().reset_index()

    return resampled_data

lookback_periods = [200, 300, 400]
scaling_factors = [1, 2, 3, 4]

fig, axes = plt.subplots(len(lookback_periods), len(scaling_factors), figsize=(20, 15), sharex=True, sharey=True)

fig.suptitle('EGARCH Volatility Model', fontsize=16)

for i, period in enumerate(lookback_periods):
    egarch_vol_data = vol_by_egarch(data.copy(), period)
    atm_iv_data = atm_iv(data_atm_iv.copy(), period)
    
    for j, scaling_factor in enumerate(scaling_factors):
        # Adjust the EGARCH volatility
        egarch_vol_data[f'adjusted_egarch_vol_{j}'] = egarch_vol_data['egarch_vol'] * scaling_factor

        # Calculate MSE and RMSE for adjusted volatility
        merged_data = pd.merge(egarch_vol_data[['Timestamp', f'adjusted_egarch_vol_{j}']], atm_iv_data[['Timestamp', 'ATM IV']], on='Timestamp', how='inner')
        mse = mean_squared_error(merged_data['ATM IV'], merged_data[f'adjusted_egarch_vol_{j}'])
        rmse = np.sqrt(mse)

        print(f'Lookback Period: {period} min, Scaling Factor: {scaling_factor}')
        print(f'MSE: {mse:.4f}')
        print(f'RMSE: {rmse:.4f}')

        # Plot the data
        ax = axes[i, j]
        ax.plot(egarch_vol_data['Timestamp'], egarch_vol_data[f'adjusted_egarch_vol_{j}'], label=f'Adjusted EGARCH Vol (x{scaling_factor})', color='blue')
        ax.plot(atm_iv_data['Timestamp'], atm_iv_data['ATM IV'], label='ATM IV', color='orange')
        ax.set_title(f'Period: {period} min, Scale: x{scaling_factor}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='upper right')

        # Annotate with MSE and RMSE
        textstr = f'MSE: {mse:.4f}\nRMSE: {rmse:.4f}'
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))

plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust rect to make space for the suptitle
plt.savefig('diff_lookback_egarch.png', dpi=300)
plt.show()

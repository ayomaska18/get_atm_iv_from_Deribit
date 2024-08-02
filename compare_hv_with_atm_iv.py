import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import numpy as np


### ATM IV Data ###
# Load ATM IV data
csv_file_iv = 'atm_iv_ETH.csv'
atm_iv_data = pd.read_csv(csv_file_iv)

# Convert Timestamp column to datetime data type
atm_iv_data['Timestamp'] = pd.to_datetime(atm_iv_data['Timestamp'])

# Turn ATM IV into numeric
atm_iv_data['ATM IV'] = pd.to_numeric(atm_iv_data['ATM IV'], errors='coerce')

# Drop N/A columns
atm_iv_data.dropna(subset=['ATM IV'], inplace=True)

# Set the Timestamp column as the index
atm_iv_data.set_index('Timestamp', inplace=True)

# Resample data to 1-minute intervals and calculate the mean for each interval
resampled_iv_data = atm_iv_data.resample('1T').mean().reset_index()

### Historical Volatility Data ###
# Load price ratio data
csv_file_price_ratio = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
price_ratio_data = pd.read_csv(csv_file_price_ratio)

def vol_by_historical_volatility(data, period:int):
    df = data.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.sort_values('Timestamp', inplace=True)
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    lookback_period = 6 * period  # Define lookback window for rolling calculation
    df['rolling_vol'] = df['log_return'].rolling(window=lookback_period).std()
    intervals_per_year = 365 * 24 * 60 * 6  # Annualize the rolling volatility
    df['hv_vol'] = df['rolling_vol'] * np.sqrt(intervals_per_year)
    df.dropna(subset=['hv_vol'], inplace=True)
    return df[['Timestamp', 'hv_vol']]

# Calculate historical volatilities for different periods
hv_data_150 = vol_by_historical_volatility(price_ratio_data, 150)
hv_data_200 = vol_by_historical_volatility(price_ratio_data, 200)
hv_data_250 = vol_by_historical_volatility(price_ratio_data, 250)
hv_data_300 = vol_by_historical_volatility(price_ratio_data, 300)

# Downsample historical volatility data to 1-minute intervals
hv_data_150.set_index('Timestamp', inplace=True)
hv_data_200.set_index('Timestamp', inplace=True)
hv_data_250.set_index('Timestamp', inplace=True)
hv_data_300.set_index('Timestamp', inplace=True)

hv_data_150 = hv_data_150.resample('1T').mean().reset_index()
hv_data_200 = hv_data_200.resample('1T').mean().reset_index()
hv_data_250 = hv_data_250.resample('1T').mean().reset_index()
hv_data_300 = hv_data_300.resample('1T').mean().reset_index()

### Plotting ###
fig, ax = plt.subplots(figsize=(14, 7))

# Plot historical volatilities
ax.plot(hv_data_150['Timestamp'], hv_data_150['hv_vol'], label='HV Period 150', color='blue')
ax.plot(hv_data_200['Timestamp'], hv_data_200['hv_vol'], label='HV Period 200', color='purple')
ax.plot(hv_data_250['Timestamp'], hv_data_250['hv_vol'], label='HV Period 250', color='green')
ax.plot(hv_data_300['Timestamp'], hv_data_300['hv_vol'], label='HV Period 300', color='grey')

# Plot ATM IV
ax.plot(resampled_iv_data['Timestamp'], resampled_iv_data['ATM IV'], label='ATM IV', color='red')

plt.xlabel('Time')
plt.ylabel('Annualized Volatility')
plt.title('Compare HV with ATM IV')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Customize the x-axis with major locators and formatters
ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))

# Save and show the figure
plt.savefig('compare_hv_with_atm_iv.png', dpi=300)
plt.show()

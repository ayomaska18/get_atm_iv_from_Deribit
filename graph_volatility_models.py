import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

# Convert Timestamp column to datetime data type
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Sort by Timestamp
data.sort_values('Timestamp', inplace=True)

# Calculate log returns
data['log_return'] = np.log(data['Price Ratio'] / data['Price Ratio'].shift(1))
print(data['log_return'].head())

# Define lookback window
lookback_period = 6 * 100 # 60 data points for 10 minutes

# Calculate rolling standard deviation of log returns
data['rolling_vol'] = data['log_return'].rolling(window=lookback_period).std()

# Annualize the rolling volatility
# Since we are calculating per 10-second volatility, annualization factor is sqrt(10-second intervals in a year)
intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
data['annualized_vol'] = data['rolling_vol'] * np.sqrt(intervals_per_year)

# Drop NaN values that result from the rolling operation
data.dropna(subset=['annualized_vol'], inplace=True)

# Plot the annualized volatility with a line chart
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(data['Timestamp'], data['annualized_vol'], label='Annualized Volatility')
plt.xlabel('Time')
plt.ylabel('Annualized Volatility')
plt.title('10-Minute Rolling Historical Volatility')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Save the figure
plt.savefig('./10-Minute_Rolling_Historical_Volatility_LineChart.png', dpi=300)
plt.show()

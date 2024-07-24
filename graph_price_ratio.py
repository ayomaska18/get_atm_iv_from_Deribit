import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

# Convert Timestamp column to datetime data type
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Filter data for the specified date range
start_date = '2024-07-18'
end_date = '2024-07-20'
filtered_data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] < pd.to_datetime(end_date) + pd.Timedelta(days=1))]

# Convert Price Ratio to numeric and drop N/A values
filtered_data['Price Ratio'] = pd.to_numeric(filtered_data['Price Ratio'], errors='coerce')
filtered_data.dropna(subset=['Price Ratio'], inplace=True)

# Plot the data
fig, ax = plt.subplots(figsize=(14, 7))
sns.lineplot(x='Timestamp', y='Price Ratio', data=filtered_data, ax=ax)
plt.xlabel('Time')
plt.ylabel('Price Ratio')
plt.title('ETHUSDT Price Ratio 18-20 JUL 24')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Set major x-axis locator and formatter for better readability
ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))

plt.show()

# Save the figure
fig.savefig('18-20JUL24_Price_Ratio_ETHUSDT.png', dpi=fig.dpi)

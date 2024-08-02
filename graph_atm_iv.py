# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import matplotlib.dates as mdates

# csv_file = 'atm_iv_ETH.csv'
# data = pd.read_csv(csv_file)

# # turn timestamp column into datetime data type
# data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# # filter out data for that day
# date_filter = '2024-07-18'
# filtered_data = data[data['Timestamp'].dt.date == pd.to_datetime(date_filter).date()]

# # add new column for time
# filtered_data['Time'] = filtered_data['Timestamp'].dt.strftime('%H:%M:%S')

# # turn atm iv into numeric
# filtered_data['ATM IV'] = pd.to_numeric(filtered_data['ATM IV'], errors='coerce')

# # drop N/A columns
# filtered_data.dropna(subset=['ATM IV'], inplace=True)

# filtered_data['Time'] = pd.to_datetime(filtered_data['Time'], format='%H:%M:%S')



# fig, ax = plt.subplots(figsize=(14, 7))
# sns.lineplot(x='Time', y='ATM IV', data=filtered_data, ax=ax)
# plt.xlabel('Time')
# plt.ylabel('ATM IV')
# plt.title('ATM IV 15 JUL 24')
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()

# ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# plt.show()

# fig.savefig('15JUL24_ATM_IV_BTC.png', dpi=fig.dpi)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load data
csv_file = 'atm_iv_ETH.csv'
data = pd.read_csv(csv_file)

# Convert Timestamp column to datetime data type
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Turn atm iv into numeric
data['ATM IV'] = pd.to_numeric(data['ATM IV'], errors='coerce')

# Drop N/A columns
data.dropna(subset=['ATM IV'], inplace=True)

data.set_index('Timestamp', inplace=True)
resampled_data = data.resample('150T').mean().reset_index()

print(resampled_data.head())

# Plot the data with a line chart
fig, ax = plt.subplots(figsize=(14, 7))
sns.lineplot(x='Timestamp', y='ATM IV', data=resampled_data, ax=ax)
plt.xlabel('Time')
plt.ylabel('ATM IV')
plt.title('ATM IV over Time')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Customize the x-axis with major locators and formatters
ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))

# Save and show the figure
plt.savefig('ATM_IV_over_Time.png', dpi=300)
plt.show()


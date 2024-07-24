import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

csv_file = 'atm_iv_ETH.csv'
data = pd.read_csv(csv_file)

data['Timestamp'] = pd.to_datetime(data['Timestamp'])

date_filter = '2024-07-18'
filtered_data = data[data['Timestamp'].dt.date == pd.to_datetime(date_filter).date()]


filtered_data['Time'] = filtered_data['Timestamp'].dt.strftime('%H:%M:%S')

filtered_data['ATM IV'] = pd.to_numeric(filtered_data['ATM IV'], errors='coerce')
filtered_data.dropna(subset=['ATM IV'], inplace=True)

filtered_data['Time'] = pd.to_datetime(filtered_data['Time'], format='%H:%M:%S')

fig, ax = plt.subplots(figsize=(14, 7))
sns.lineplot(x='Time', y='ATM IV', data=filtered_data, ax=ax)
plt.xlabel('Time')
plt.ylabel('ATM IV')
plt.title('ATM IV 18 JUL 24')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

plt.show()

fig.savefig('18JUL24_ATM_IV.png', dpi=fig.dpi)


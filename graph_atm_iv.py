import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

csv_file = 'atm_iv.csv'
data = pd.read_csv(csv_file)

data['Timestamp'] = pd.to_datetime(data['Timestamp'])

data['Time'] = data['Timestamp'].dt.strftime('%H:%M:%S')

data['ATM IV'] = pd.to_numeric(data['ATM IV'], errors='coerce')
data.dropna(subset=['ATM IV'], inplace=True)

data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S')

fig, ax = plt.subplots(figsize=(14, 7))
sns.lineplot(x='Time', y='ATM IV', data=data, ax=ax)
plt.xlabel('Time')
plt.ylabel('ATM IV')
plt.title('ATM IV 14 JUL 24')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

plt.show()

fig.savefig('14JUL24_ATM_IV.png', dpi=fig.dpi)

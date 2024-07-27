import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

def vol_by_hisotrical_volatility(data, period:int):
    # Convert Timestamp column to datetime data type
    df= data.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    print(df['log_return'].head())

    # Define lookback window
    lookback_period = 6 * period # 60 data points for 10 minutes

    # Calculate rolling standard deviation of log returns
    df['rolling_vol'] = df['log_return'].rolling(window=lookback_period).std()

    # Annualize the rolling volatility
    # Since we are calculating per 10-second volatility, annualization factor is sqrt(10-second intervals in a year)
    intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
    df['hv_vol'] = df['rolling_vol'] * np.sqrt(intervals_per_year)

    # Drop NaN values that result from the rolling operation
    df.dropna(subset=['hv_vol'], inplace=True)

    return df

data1 = vol_by_hisotrical_volatility(data.copy(),10)
data2 = vol_by_hisotrical_volatility(data.copy(),20)
data3 = vol_by_hisotrical_volatility(data.copy(),60)
data4 = vol_by_hisotrical_volatility(data.copy(),100)
data5 = vol_by_hisotrical_volatility(data.copy(),150)
data6 = vol_by_hisotrical_volatility(data.copy(),200)
data7 = vol_by_hisotrical_volatility(data.copy(),250)
data8 = vol_by_hisotrical_volatility(data.copy(),300)

fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(data1['Timestamp'], data1['hv_vol'], label='period 10', color='red')
ax.plot(data2['Timestamp'], data2['hv_vol'], label='period 20', color='orange')
ax.plot(data3['Timestamp'], data3['hv_vol'], label='period 60', color='yellow')
ax.plot(data4['Timestamp'], data4['hv_vol'], label='period 100', color='green')
ax.plot(data5['Timestamp'], data5['hv_vol'], label='period 150', color='blue')
ax.plot(data6['Timestamp'], data6['hv_vol'], label='period 200', color='purple')
ax.plot(data7['Timestamp'], data7['hv_vol'], label='period 250', color='blue')
ax.plot(data8['Timestamp'], data8['hv_vol'], label='period 300', color='grey')

plt.xlabel('Time')
plt.ylabel('Annualized Volatility')
plt.title('Different Period Rolling Historical Volatility')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


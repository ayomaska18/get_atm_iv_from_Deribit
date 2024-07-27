import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# Load data
csv_file = './uniswap_data_ratio/ETHUSDT_price_ratio.csv'
data = pd.read_csv(csv_file)

def vol_by_hisotrical_volatility(data):
    # Convert Timestamp column to datetime data type
    df= data.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    print(df['log_return'].head())

    # Define lookback window
    lookback_period = 6 * 400 # 60 data points for 10 minutes

    # Calculate rolling standard deviation of log returns
    df['rolling_vol'] = df['log_return'].rolling(window=lookback_period).std()

    # Annualize the rolling volatility
    # Since we are calculating per 10-second volatility, annualization factor is sqrt(10-second intervals in a year)
    intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
    df['hv_vol'] = df['rolling_vol'] * np.sqrt(intervals_per_year)

    # Drop NaN values that result from the rolling operation
    df.dropna(subset=['hv_vol'], inplace=True)

    return df

def vol_by_garch(data):
    df = data.copy()
    # Convert Timestamp column to datetime data type
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    print(df['log_return'].head())

    # Fit GARCH(1,1) model
    garch_model = arch_model(df['log_return'].dropna(), vol='Garch', p=400, q=400)
    garch_fit = garch_model.fit(disp='off')

    # Extract conditional volatility (annualized)
    intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
    df['garch_vol'] = garch_fit.conditional_volatility * np.sqrt(intervals_per_year)

    return df

def vol_by_egarch(data):
    df = data.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.sort_values('Timestamp', inplace=True)
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    
    # Fit EGARCH(1,1) model
    egarch_model = arch_model(df['log_return'].dropna(), vol='EGarch', p=400, q=400, rescale=False)
    egarch_fit = egarch_model.fit(disp='off')
    
    # Extract conditional volatility (annualized)
    intervals_per_year = 365 * 24 * 60 * 6  # Annualize the volatility
    df['egarch_vol'] = egarch_fit.conditional_volatility / 10000 * np.sqrt(intervals_per_year)
    return df

def vol_by_heston(data):
    df = data.copy()
    # Convert Timestamp column to datetime data type
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)

    # Calculate log returns
    df['log_return'] = np.log(df['Price Ratio'] / df['Price Ratio'].shift(1))
    print(df['log_return'].head())

    # Placeholder Heston model
    # Here we use the same rolling window approach as a simplified proxy for Heston model.
    lookback_period = 6 * 400 # 60 data points for 10 minutes

    # Calculate rolling mean and standard deviation of log returns
    df['heston_vol'] = df['log_return'].rolling(window=lookback_period).std()

    # Annualize the rolling volatility
    intervals_per_year = 365 * 24 * 60 * 6  # 6 intervals per minute, 60 minutes per hour, 24 hours per day, 365 days per year
    df['heston_vol'] = df['heston_vol'] * np.sqrt(intervals_per_year)

    # Drop NaN values that result from the rolling operation
    df.dropna(subset=['heston_vol'], inplace=True)

    return df

hv_data = vol_by_hisotrical_volatility(data)
gar_data = vol_by_garch(data)
hes_data = vol_by_heston(data)
egar_data = vol_by_egarch(data)

# Plot the annualized volatility with a line chart
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(hv_data['Timestamp'], hv_data['hv_vol'], label='Annualized Historical Volatility', color='blue')
ax.plot(gar_data['Timestamp'], gar_data['garch_vol'], label='Annualized GARCH Volatility', color='orange')
ax.plot(hes_data['Timestamp'], hes_data['heston_vol'], label='Annualized Heston Volatility', color='green')
ax.plot(egar_data['Timestamp'], egar_data['egarch_vol'], label='Annualized Heston Volatility', color='red')
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

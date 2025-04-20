import sys

import eastern
import shinybroker as sb
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta

asset_symbol = "MSFT"

############ Risk Tolerance Calculation
asset_data_vix = sb.fetch_historical_data(
    contract=sb.Contract({
        'symbol': 'VIX',  # or 'VX' for VIX futures
        'secType': 'IND',  # Futures contract type
        'exchange': 'CBOE',  # CBOE Futures Exchange for VIX futures
        'currency': 'USD',
    }),
    barSizeSetting='1 day',
    durationStr='1 Y'
)
# print(asset_data_vix)
# Extract the DataFrame from the result
df = asset_data_vix['hst_dta']

# Ensure timestamp is in datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Create a new DataFrame with just the date and scaled high value
risktol_df = pd.DataFrame({
    'Timestamp': df['timestamp'].dt.date,
    'risk_tolerance': df['high'] * 0.01
})

# Print header
# print("Timestamp   risk_tolerance")

# Print each row
# for _, row in risktol_df.iterrows():
#     print(f"{row['Timestamp']}  {row['risk_tolerance']:.4f}")

############ Asset related
asset_data = sb.fetch_historical_data(
    contract=sb.Contract({
        'symbol': asset_symbol,
        'secType': 'STK',
        'exchange': 'SMART',
        'currency': 'USD',
    }),
    barSizeSetting='1 day',
    durationStr='1 Y'
)

############ Set initial parameters
inventory = 0

def get_risk_tolerance(date_str):
    date = pd.to_datetime(date_str).normalize()
    risktol_df['Timestamp'] = pd.to_datetime(risktol_df['Timestamp']).dt.normalize()
    row = risktol_df[risktol_df['Timestamp'] == date]
    if not row.empty:
        return row['risk_tolerance'].values[0]
    else:
        return "Date not found."
# print(get_risk_tolerance('2025-04-17'))


def log_ratio(stock_data):
    # Convert 'close' column to an array
    close_array = stock_data['hst_dta']['close'].values
    # Calculate the natural logarithm (base e) of the ratios
    log_ratios = np.log(close_array[1:]/close_array[:-1])
    # Prepend 0 to the log_ratios array for the first element
    log_ratios = np.insert(log_ratios, 0, 0)
    return log_ratios

# # Calculate daily volatility (standard deviation)
asset_volatility_daily = np.std(log_ratio(asset_data))
# Annualized the volatility by multiplying by the square root of 252 (trading days in a year)
asset_volatility_annualized = asset_volatility_daily * np.sqrt(252)
print(f"{asset_symbol} annualized volatility is {asset_volatility_annualized}")

#Time left in trading week
now = datetime.now(pytz.timezone('US/Eastern'))
#now = eastern.localize(datetime(2024, 4, 17, 14, 30))  # YYYY, MM, DD, HH, MM
wd = now.isoweekday()

if wd >= 6:
    print("Market is closed for the week.")
else:
    market_close = datetime(now.year, now.month, now.day + (5 - wd), 16, 0, tzinfo=pytz.timezone('US/Eastern'))
    print(f"Time left in trading week: {market_close - now}")
import requests
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

# ---------------------------
# 1. Retrieve Data from BLS API
# ---------------------------
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
headers = {'Content-type': 'application/json'}

# Request unemployment rate data (Series ID: LNS14000000) from 2014 to 2025
payload = {
    "seriesid": ["LNS14000000"],
    "startyear": "2014",
    "endyear": "2025",
    # "registrationkey": "YOUR_API_KEY"  # Optional: add your API key if available
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

if data.get('status') != "REQUEST_SUCCEEDED":
    print("Error in API request:", data.get("message", "Unknown error"))
    exit(1)

# ---------------------------
# 2. Parse and Process the Data
# ---------------------------
records = []
series_data = data['Results']['series'][0]
for entry in series_data['data']:
    period = entry['period']
    # Process only monthly data (format "MXX")
    if period.startswith("M"):
        month = period[1:3]  # Extract month number
        year = entry['year']
        date = pd.to_datetime(f"{year}-{month}-01")
        value = float(entry['value'])
        records.append({'date': date, 'unemployment_rate': value})

# Create a DataFrame and sort by date
df = pd.DataFrame(records)
df = df.sort_values('date')
df.set_index('date', inplace=True)

# ---------------------------
# 3. Seasonal Decomposition
# ---------------------------
# Decompose the time series to observe trend, seasonality, and residuals.
# We use a period of 12 for monthly data.
decomposition = seasonal_decompose(df['unemployment_rate'], model='additive', period=12)
decomposition.plot()
plt.suptitle("Seasonal Decomposition of US Unemployment Rate", fontsize=16)
plt.show()

# ---------------------------
# 4. Forecasting Using ARIMA
# ---------------------------
# Fit an ARIMA model (order chosen as (1,1,1) for demonstration) to forecast future values.
model = ARIMA(df['unemployment_rate'], order=(1, 1, 1))
model_fit = model.fit()

# Forecast the next 12 months
forecast_steps = 12
forecast = model_fit.forecast(steps=forecast_steps)

# Create a date range for the forecasted period
last_date = df.index[-1]
future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')
forecast_series = pd.Series(forecast, index=future_dates)

# ---------------------------
# 5. Plot Historical Data and Forecast
# ---------------------------
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['unemployment_rate'], label='Historical Unemployment Rate', marker='o')
plt.plot(forecast_series.index, forecast_series, label='Forecasted Unemployment Rate', color='red', marker='o')
plt.xlabel('Date')
plt.ylabel('Unemployment Rate (%)')
plt.title('US Unemployment Rate Forecast (2014 onward)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

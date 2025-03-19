import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm
from pandas.tseries.offsets import DateOffset

# Download historical data for AAPL (6 months)
ticker = 'AAPL'
df = yf.download(ticker, period='6mo')

# Daily returns
df['Return'] = df['Close'].pct_change()

# Moving averages
df['MA_5'] = df['Close'].rolling(window=5).mean()
df['MA_20'] = df['Close'].rolling(window=20).mean()

# Exponential Moving Average (EMA)
df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()

# Volatility (rolling STD of returns)
df['Volatility'] = df['Return'].rolling(window=10).std()

# Momentum indicator
df['Momentum'] = df['Close'] - df['Close'].shift(10)

# RSI (Relative Strength Index)
delta = df['Close'].diff()
up = delta.clip(lower=0)
down = -1 * delta.clip(upper=0)
ema_up = up.ewm(com=13, adjust=False).mean()
ema_down = down.ewm(com=13, adjust=False).mean()
rs = ema_up / ema_down
df['RSI'] = 100 - (100 / (1 + rs))

# MACD and Signal Line
exp1 = df['Close'].ewm(span=12, adjust=False).mean()
exp2 = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = exp1 - exp2
df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

# Drop NaN values from indicators
df.dropna(inplace=True)

# Define features and target variable
features = ['MA_5', 'MA_20', 'EMA_10', 'Volatility', 'Momentum', 'RSI', 'MACD', 'Signal_Line']

# Split data into training and testing sets based on date:
# Train on data before the last 2 months, test on the last 2 months.
test_start_date = df.index.max() - DateOffset(months=2)
train_df = df[df.index < test_start_date]
test_df = df[df.index >= test_start_date]

X_train = train_df[features]
y_train = train_df['Close']
X_test = test_df[features]
y_test = test_df['Close']

# ARIMA model fitting and forecasting using training set and forecasting for test period
arima_order = (2, 1, 2)
arima_model = sm.tsa.ARIMA(y_train, order=arima_order).fit()
arima_predictions = arima_model.forecast(steps=len(y_test))

# Define machine learning models
models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(random_state=0),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=0),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=0)
}

# Dictionary to store predictions from all models
predictions = {'ARIMA': arima_predictions}

# Fit each model and predict on the test set
for name, model in models.items():
    model.fit(X_train, y_train)
    predictions[name] = model.predict(X_test)

# Plotting predictions with actual dates on the x-axis
plt.figure(figsize=(14, 8))
plt.plot(y_test.index, y_test.values, label='Actual Close Prices', color='black', linewidth=2)

# Define colors and line styles for clarity
colors = ['red', 'blue', 'green', 'orange', 'purple']
linestyles = ['--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 5))]

# Plot each model's predictions
for (model_name, pred_values), color, ls in zip(predictions.items(), colors, linestyles):
    plt.plot(y_test.index, pred_values, label=model_name, color=color, linestyle=ls, linewidth=2)

plt.title('Stock Close Price Prediction Comparison (Last 6 Months)', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Close Price', fontsize=14)
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Calculate and print RMSE for evaluation
print("Root Mean Squared Error (RMSE):")
for model_name, pred_values in predictions.items():
    rmse = np.sqrt(mean_squared_error(y_test, pred_values))
    print(f"{model_name}: {rmse:.4f}")

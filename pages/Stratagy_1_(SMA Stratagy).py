import streamlit as st
import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Load API credentials from .env
load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv("ALPACA_SECRET_KEY")

# App title
st.title("📈 50-Day vs 200-Day SMA Crossover Strategy")

# Introduction
st.markdown("""
Welcome to the **Simple Moving Average (SMA) Crossover Analysis Tool**!

This strategy helps you identify potential **buy** or **sell** signals based on the crossover of two SMAs:

- 🔵 **50-Day SMA**: Reflects the medium-term price trend.
- 🔴 **100-Day SMA**: Reflects the longer-term price trend.

---

📌 **How it works:**

- **Golden Cross** (📈): When 50-Day SMA crosses **above** 200-Day SMA → _Bullish signal_
- **Death Cross** (📉): When 50-Day SMA crosses **below** 200-Day SMA → _Bearish signal_
""")

# Input stock symbol
symbol = st.text_input("Enter Stock Symbol:", "AAPL").upper()

if symbol:
    try:
        # Initialize Alpaca client
        client = StockHistoricalDataClient(api_key=API_KEY, secret_key=API_SECRET)

        # Target: 200+ trading days → Need ~500 calendar days for safety
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=500)

        # Request data
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )
        stock_data = client.get_stock_bars(request).df

        # Make sure we're only using this stock's data
        stock_data = stock_data[stock_data.index.get_level_values("symbol") == symbol]
        st.write(f"📅 Total trading days fetched: **{len(stock_data)}**")

        if len(stock_data) < 200:
            st.warning("⚠️ Warning: Less than 200 trading days of data available. Results may be inaccurate.")

        # Calculate SMAs
        stock_data['SMA_50'] = stock_data['close'].rolling(window=50).mean()
        stock_data['SMA_200'] = stock_data['close'].rolling(window=100).mean()

        # Latest SMA values
        latest_50 = stock_data['SMA_50'].iloc[-1]
        latest_200 = stock_data['SMA_200'].iloc[-1]

        st.write(f"**Latest 50-Day SMA:** ${latest_50:.2f}")
        st.write(f"**Latest 200-Day SMA:** ${latest_200:.2f}")

        # Signal logic
        if latest_50 > latest_200:
            st.success("✅ Golden Cross Detected: **Bullish Trend** 📈")
        else:
            st.error("❌ Death Cross Detected: **Bearish Trend** 📉")

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(stock_data.index.get_level_values("timestamp"), stock_data['close'], label='Close Price', alpha=0.6)
        ax.plot(stock_data.index.get_level_values("timestamp"), stock_data['SMA_50'], label='50-Day SMA', color='blue')
        ax.plot(stock_data.index.get_level_values("timestamp"), stock_data['SMA_200'], label='200-Day SMA', color='red')
        ax.set_title(f"{symbol} Price with 50 & 200-Day SMAs")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error("🚫 Error fetching or processing data.")
        st.exception(e)

st.subheader("📉 The Lagging Problem in SMA-Based Strategies")


st.markdown('''
While SMA crossovers (like the 50-day vs 200-day strategy) are powerful, they **lag behind price movements**.

This means they may **confirm a trend after it's already underway**, causing late entries or exits.

For example, by the time a "Golden Cross" happens, the price might have already moved significantly upwards — reducing potential profit.

---
### 🔄 Introducing an Offset
To address this lag, we introduce a new variable: **`offset`**.

This offset allows us to **adjust the sensitivity of our signals**, enabling the strategy to respond earlier to potential trend shifts.

We'll explore whether **adding a constant offset to SMA differences** or **shifting SMA periods** can help generate more timely signals.
''')


# st.subheader("🤖 Trend Prediction using Linear Regression")

# st.markdown("""
# To enhance our strategy, we're introducing a **simple linear regression model** that uses:

# - ✅ **Current Price**
# - 📘 **50-Day SMA**
# - 🔴 **200-Day SMA**

# The model is trained to classify the **next 10-day trend** as:

# - **Buy** → If price is expected to go up significantly  
# - **Sell** → If price is expected to drop  
# - **Hold** → If change is insignificant

# This model helps us anticipate trends earlier instead of waiting for crossover confirmations.
# """)



import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# Core financial logic imports
from single_asset import (
    fetch_data,
    compute_returns,
    compute_metrics,
    backtest_buy_and_hold,
    moving_average_strategy,
)
from portfolio import show_portfolio_page

def run_linear_regression(prices: pd.Series, forecast_days: int = 30):
    """
    Computes a linear trend and forecasts future price points using ML regression.
    """
    # Prepare data arrays for scikit-learn
    y_values = prices.values.reshape(-1, 1)
    x_axis = np.arange(len(y_values)).reshape(-1, 1)

    regressor = LinearRegression()
    regressor.fit(x_axis, y_values)

    # Generate historical trend line and future projections
    historical_trend = regressor.predict(x_axis).flatten()
    future_x = np.arange(len(y_values), len(y_values) + forecast_days).reshape(-1, 1)
    future_forecast = regressor.predict(future_x).flatten()

    return historical_trend, future_forecast

def show_single_asset_page():
    # Requirement 5 & 21: Automatically refresh the app every 5 minutes (300,000 ms)
    # This ensures data remains 'real-time' without manual intervention
    st_autorefresh(interval=5 * 60 * 1000, key="data_refresh_timer")

    st.title("Quant A - Single Asset Dashboard")
    
    # Sidebar Configuration
    st.sidebar.header("Asset Settings")
    ticker = st.sidebar.text_input("Ticker Symbol", value="BTC-USD")
    
    period = st.sidebar.selectbox(
        "Time Horizon",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=5,
    )
    interval = st.sidebar.selectbox(
        "Sampling Interval",
        ["1m", "5m", "15m", "30m", "1h", "1d"],
        index=5,
    )

    st.sidebar.header("Strategy Parameters")
    fast_ma = st.sidebar.number_input("Short Window (MA)", min_value=5, value=20)
    slow_ma = st.sidebar.number_input("Long Window (MA)", min_value=10, value=50)

    try:
        # Data Retrieval
        market_data = fetch_data(ticker, period=period, interval=interval)
        if market_data.empty:
            st.error("No data found for this ticker.")
            return

        # Core Metrics Display
        current_price = float(market_data["Close"].iloc[-1])
        st.metric(label=f"Current {ticker} Price", value=f"{current_price:,.4f}")

        asset_returns = compute_returns(market_data["Close"])
        base_metrics = compute_metrics(asset_returns, market_data["Close"])

        st.subheader("Performance Summary (Buy & Hold)")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        metric_col1.metric("Total Return", f"{base_metrics['cumulative_return']:.2%}")
        metric_col2.metric("Volatility", f"{base_metrics['vol_daily']:.2%}")
        
        sharpe = base_metrics['sharpe']
        metric_col3.metric("Sharpe Ratio", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")
        metric_col4.metric("Max Drawdown", f"{base_metrics['max_drawdown']:.2%}")

        # ML Prediction Section (Requirement 62 Bonus)
        st.subheader("Predictive Analysis (Linear Regression)")
        forecast_horizon = st.slider("Forecast Range (Days)", 7, 90, 30)
        
        trend_line, future_projection = run_linear_regression(market_data["Close"], forecast_horizon)
        
        # Build the visualization dataframe for history and forecast
        history_viz = pd.DataFrame({
            "Market Price": market_data["Close"],
            "Regression Trend": trend_line
        }, index=market_data.index)
        
        projection_dates = pd.date_range(
            start=market_data.index[-1], 
            periods=forecast_horizon + 1, 
            freq='D'
        )[1:]
        
        forecast_viz = pd.DataFrame({"ML Projection": future_projection}, index=projection_dates)
        
        # Merge for a continuous chart
        prediction_chart = pd.concat([history_viz, forecast_viz])
        st.line_chart(prediction_chart)

        # Strategy Backtesting
        st.subheader("Trend Following Strategy (MA Crossover)")
        strategy = moving_average_strategy(
            market_data["Close"], 
            short_window=fast_ma, 
            long_window=slow_ma
        )

        comparison_plot = pd.DataFrame({
            "Benchmark (B&H)": backtest_buy_and_hold(asset_returns),
            "Strategy (MA)": strategy["portfolio"]
        })
        
        st.line_chart(comparison_plot)

        # Strategy Metrics
        s_metrics = strategy["metrics"]
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        s_col1.metric("Strategy Perf.", f"{s_metrics['cumulative_return']:.2%}")
        s_col2.metric("Strategy Vol.", f"{s_metrics['vol_daily']:.2%}")
        s_col3.metric("Strategy Sharpe", f"{s_metrics['sharpe']:.2f}")
        s_col4.metric("Strategy Max DD", f"{s_metrics['max_drawdown']:.2%}")

    except Exception as e:
        st.error(f"Execution Error: {str(e)}")

# Global App Configuration
st.set_page_config(page_title="Quant B Portfolio Dashboard", layout="wide")

# Main Navigation
nav_choice = st.sidebar.radio(
    "Application Module",
    ["Quant A - Asset Analysis", "Quant B - Portfolio Manager"],
)

if "Quant A" in nav_choice:
    show_single_asset_page()
else:
    show_portfolio_page()

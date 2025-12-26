import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression

def fetch_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Download market data and handle multi-index columns from yfinance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            return pd.DataFrame()
        
        # Flatten multi-index columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

def compute_returns(close_series: pd.Series) -> pd.Series:
    """Calculate simple percentage returns."""
    return close_series.pct_change().dropna()

def compute_metrics(returns: pd.Series, prices: pd.Series) -> dict:
    """Calculate key performance and risk indicators."""
    if returns.empty:
        return {
            "cumulative_return": 0.0, 
            "vol_daily": 0.0, 
            "sharpe": 0.0, 
            "max_drawdown": 0.0
        }

    # Cumulative Return
    total_perf = float((1.0 + returns).prod() - 1.0)
    
    # Volatility and Sharpe Ratio (annualized)
    daily_vol = float(returns.std())
    sharpe = float((returns.mean() / daily_vol) * np.sqrt(252)) if daily_vol != 0 else 0.0
    
    # Drawdown calculation
    peaks = prices.cummax()
    drawdown_series = prices / peaks - 1.0
    max_dd = float(drawdown_series.min())

    return {
        "cumulative_return": total_perf,
        "vol_daily": daily_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd
    }

def backtest_buy_and_hold(returns: pd.Series, initial_capital: float = 100.0) -> pd.Series:
    """Simulate a basic buy and hold strategy equity curve."""
    return initial_capital * (1.0 + returns).cumprod()

def moving_average_strategy(prices: pd.Series, short_window: int = 20, long_window: int = 50, initial_capital: float = 100.0) -> dict:
    """Execute a Trend Following strategy based on MA crossovers."""
    asset_returns = compute_returns(prices)
    
    fast_ma = prices.rolling(window=short_window).mean()
    slow_ma = prices.rolling(window=long_window).mean()

    # Generate signal and shift to avoid look-ahead bias
    raw_signal = (fast_ma > slow_ma).astype(int)
    positions = raw_signal.shift(1).reindex(asset_returns.index).fillna(0)
    
    # Strategy performance
    strategy_returns = asset_returns * positions
    equity_curve = backtest_buy_and_hold(strategy_returns, initial_capital)
    
    # Extract metrics
    performance_metrics = compute_metrics(strategy_returns, equity_curve)

    return {
        "portfolio": equity_curve,
        "metrics": performance_metrics,
        "short_ma": fast_ma,
        "long_ma": slow_ma
    }
def run_linear_regression(prices: pd.Series, forecast_days: int = 30):
    """
    Perform a simple linear regression to forecast future price trends.
    """
    # Prepare data for regression (using index as X)
    y = prices.values.reshape(-1, 1)
    X = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    # Predict historical trend
    trend = model.predict(X).flatten()

    # Forecast future points
    future_X = np.arange(len(y), len(y) + forecast_days).reshape(-1, 1)
    forecast = model.predict(future_X).flatten()

    return trend, forecast

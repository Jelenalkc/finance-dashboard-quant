import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# --- LOGIQUE DE CALCUL ---

def fetch_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

def compute_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()

def compute_metrics(returns: pd.Series, close: pd.Series) -> dict:
    """Calcule les métriques avec les noms attendus par le fichier principal."""
    if returns.empty:
        return {
            "cumulative_return": 0.0, 
            "vol_daily": 0.0, 
            "sharpe": 0.0, 
            "max_drawdown": 0.0
        }

    cum_ret = float((1.0 + returns).prod() - 1.0)
    vol = float(returns.std())
    sharpe_ratio = float((returns.mean() / vol) * np.sqrt(252)) if vol != 0 else 0.0
    
    rolling_max = close.cummax()
    drawdown = close / rolling_max - 1.0
    mdd = float(drawdown.min())

    return {
        "cumulative_return": cum_ret,
        "vol_daily": vol,
        "sharpe": sharpe_ratio,
        "max_drawdown": mdd
    }

def backtest_buy_and_hold(returns: pd.Series, initial_capital: float = 100.0) -> pd.Series:
    return initial_capital * (1.0 + returns).cumprod()

def moving_average_strategy(close: pd.Series, short_window: int = 20, long_window: int = 50, initial_capital: float = 100.0) -> dict:
    asset_returns = compute_returns(close)
    short_ma = close.rolling(window=short_window).mean()
    long_ma = close.rolling(window=long_window).mean()

    signal = (short_ma > long_ma).astype(int)
    positions = signal.shift(1).reindex(asset_returns.index).fillna(0)
    
    strat_returns = asset_returns * positions
    portfolio_value = backtest_buy_and_hold(strat_returns, initial_capital)
    
    # Appel de compute_metrics qui renvoie maintenant les bons noms
    metrics = compute_metrics(strat_returns, portfolio_value)

    return {
        "portfolio": portfolio_value,
        "metrics": metrics,
        "short_ma": short_ma,
        "long_ma": long_ma
    }
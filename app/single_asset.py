import yfinance as yf
import pandas as pd
import numpy as np


def fetch_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """
    Récupère les données de prix via yfinance.
    """
    data = yf.download(ticker, period=period, interval=interval)

    # On sécurise bien : data doit être un DataFrame non vide
    if data is None or len(data) == 0:
        raise ValueError("Aucune donnée trouvée pour ce ticker / ces paramètres.")

    return data


def compute_returns(close: pd.Series) -> pd.Series:
    """
    Calcule les rendements (returns) à partir d'une série de prix de clôture.
    """
    returns = close.pct_change().dropna()
    return returns


def compute_metrics(returns: pd.Series, close: pd.Series) -> dict:
    """
    Calcule les métriques de base : perf cumulée, vol, Sharpe approx, max drawdown.
    """
    # Perf cumulée (Buy & Hold)
    cumulative_return = float((1 + returns).prod() - 1)

    # Volatilité (écart-type des rendements)
    vol_daily = float(returns.std())

    # Sharpe approximatif (annualisé, sans taux sans risque)
    if vol_daily != 0.0:
        sharpe = float((returns.mean() / vol_daily) * np.sqrt(252))
    else:
        sharpe = np.nan

    # Max drawdown
    rolling_max = close.cummax()
    drawdown = close / rolling_max - 1
    max_drawdown = float(drawdown.min())

    return {
        "cumulative_return": cumulative_return,
        "vol_daily": vol_daily,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
    }


def backtest_buy_and_hold(returns: pd.Series, initial_capital: float = 100.0) -> pd.Series:
    """
    Backtest Buy & Hold : on investit initial_capital au début et on laisse courir.
    Renvoie la valeur du portefeuille dans le temps.
    """
    cum_returns = (1.0 + returns).cumprod()
    portfolio_value = initial_capital * cum_returns
    return portfolio_value

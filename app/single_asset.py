import yfinance as yf
import pandas as pd
import numpy as np


def fetch_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """
    Récupère les données de prix via yfinance.
    """
    data = yf.download(ticker, period=period, interval=interval)

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
    # Perf cumulée (Buy & Hold ou stratégie)
    cumulative_return = float((1.0 + returns).prod() - 1.0)

    # Volatilité (écart-type des rendements)
    vol_daily = float(returns.std())

    # Sharpe approximatif (annualisé, sans taux sans risque)
    if vol_daily != 0.0:
        sharpe = float((returns.mean() / vol_daily) * np.sqrt(252))
    else:
        sharpe = np.nan

    # Max drawdown
    rolling_max = close.cummax()
    drawdown = close / rolling_max - 1.0
    max_drawdown = float(drawdown.min())

    return {
        "cumulative_return": cumulative_return,
        "vol_daily": vol_daily,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
    }


def backtest_buy_and_hold(returns: pd.Series, initial_capital: float = 100.0) -> pd.Series:
    """
    Backtest générique : à partir de rendements, calcule la valeur du portefeuille.
    """
    cum_returns = (1.0 + returns).cumprod()
    portfolio_value = initial_capital * cum_returns
    return portfolio_value


def moving_average_strategy(
    close: pd.Series,
    short_window: int = 20,
    long_window: int = 50,
    initial_capital: float = 100.0,
) -> dict:
    """
    Stratégie de croisement de moyennes mobiles :

    - MA courte > MA longue => investi (position = 1)
    - sinon => pas investi (position = 0)
    """
    if short_window >= long_window:
        raise ValueError(
            "Le paramètre 'Short MA window' doit être strictement inférieur à 'Long MA window'."
        )

    # Rendements de l'actif (pour Buy & Hold ou stratégie)
    asset_returns = compute_returns(close)

    # Moyennes mobiles
    short_ma = close.rolling(window=short_window).mean()
    long_ma = close.rolling(window=long_window).mean()

    # Signal : 1 si short_ma > long_ma, sinon 0
    raw_signal = (short_ma > long_ma).astype(int)

    # On prend la position le jour suivant le signal
    positions = raw_signal.shift(1).reindex(asset_returns.index).fillna(0)

    # Rendements de la stratégie
    strategy_returns = asset_returns * positions

    # Backtest du portefeuille de la stratégie
    portfolio_value = backtest_buy_and_hold(strategy_returns, initial_capital)

    # Metrics de la stratégie
    metrics = compute_metrics(strategy_returns, close.loc[asset_returns.index])

    return {
        "portfolio": portfolio_value,
        "short_ma": short_ma,
        "long_ma": long_ma,
        "positions": positions,
        "metrics": metrics,
    }

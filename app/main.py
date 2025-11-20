import streamlit as st
import numpy as np

from single_asset import (
    fetch_data,
    compute_returns,
    compute_metrics,
    backtest_buy_and_hold,
)

# Configuration de la page
st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.title("Single Asset Dashboard - Quant A")

# 1) Choix de l'actif
ticker = st.sidebar.text_input("Ticker (Yahoo Finance)", value="BTC-USD")

# 2) Période & intervalle
period = st.sidebar.selectbox(
    "Period",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"],
    index=5,
)
interval = st.sidebar.selectbox(
    "Interval",
    ["1m", "5m", "15m", "30m", "1h", "1d"],
    index=5,
)

st.write(f"### Données pour : `{ticker}`")

try:
    # 3) Récupération des données via le module single_asset
    data = fetch_data(ticker, period=period, interval=interval)

    # 4) Dernier prix
    last_price = float(data["Close"].iloc[-1])
    st.metric(label="Dernier prix (Close)", value=round(last_price, 4))

    # 5) Calcul des rendements et des métriques
    returns = compute_returns(data["Close"])
    metrics = compute_metrics(returns, data["Close"])

    cumulative_return = metrics["cumulative_return"]
    vol_daily = metrics["vol_daily"]
    sharpe = metrics["sharpe"]
    max_drawdown = metrics["max_drawdown"]

    # 6) Affichage des métriques
    st.subheader("Metrics de base")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Perf cumulée (Buy & Hold)", f"{cumulative_return * 100:.2f}%")
    col2.metric("Volatilité (std des returns)", f"{vol_daily * 100:.2f}%")

    # np.isnan(sharpe) renvoie un booléen car sharpe est un float
    if sharpe is not None and not np.isnan(sharpe):
        col3.metric("Sharpe (approx.)", f"{sharpe:.2f}")
    else:
        col3.metric("Sharpe (approx.)", "N/A")

    col4.metric("Max Drawdown", f"{max_drawdown * 100:.2f}%")

    # 7) Graphique du prix de clôture
    st.subheader("Historique du prix de clôture")
    st.line_chart(data["Close"], use_container_width=True)

    # 8) Backtest Buy & Hold simple
    st.subheader("Backtest Buy & Hold (capital initial = 100)")
    portfolio_value = backtest_buy_and_hold(returns, initial_capital=100.0)
    st.line_chart(portfolio_value, use_container_width=True)

    # 9) Affichage du tableau brut
    with st.expander("Voir les dernières lignes de données"):
        st.dataframe(data.tail())

except ValueError as ve:
    st.error(str(ve))
except Exception as e:
    st.error(f"Erreur lors de la récupération ou du traitement des données : {e}")

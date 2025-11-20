import streamlit as st
import pandas as pd
import numpy as np

from single_asset import (
    fetch_data,
    compute_returns,
    compute_metrics,
    backtest_buy_and_hold,
    moving_average_strategy,
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

# 3) Paramètres de la stratégie Moyennes Mobiles
short_window = st.sidebar.number_input(
    "Short MA window", min_value=5, max_value=60, value=20, step=1
)
long_window = st.sidebar.number_input(
    "Long MA window", min_value=10, max_value=200, value=50, step=1
)

st.write(f"### Données pour : `{ticker}`")

try:
    # 4) Récupération des données
    data = fetch_data(ticker, period=period, interval=interval)

    # 5) Dernier prix
    last_price = float(data["Close"].iloc[-1])
    st.metric(label="Dernier prix (Close)", value=round(last_price, 4))

    # 6) Rendements & metrics pour Buy & Hold
    returns = compute_returns(data["Close"])
    bh_metrics = compute_metrics(returns, data["Close"])

    bh_cum_return = bh_metrics["cumulative_return"]
    bh_vol_daily = bh_metrics["vol_daily"]
    bh_sharpe = bh_metrics["sharpe"]
    bh_max_dd = bh_metrics["max_drawdown"]

    # 7) Affichage des metrics Buy & Hold
    st.subheader("Metrics Buy & Hold")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Perf cumulée", f"{bh_cum_return * 100:.2f}%")
    col2.metric("Volatilité (std returns)", f"{bh_vol_daily * 100:.2f}%")

    if bh_sharpe is not None and not np.isnan(bh_sharpe):
        col3.metric("Sharpe (approx.)", f"{bh_sharpe:.2f}")
    else:
        col3.metric("Sharpe (approx.)", "N/A")

    col4.metric("Max Drawdown", f"{bh_max_dd * 100:.2f}%")

    # 8) Graphique du prix de clôture
    st.subheader("Historique du prix de clôture")
    st.line_chart(data["Close"], use_container_width=True)

    # 9) Backtest Buy & Hold (portefeuille)
    st.subheader("Backtest Buy & Hold (capital initial = 100)")
    bh_portfolio = backtest_buy_and_hold(returns, initial_capital=100.0)
    st.line_chart(bh_portfolio, use_container_width=True)

    # 🔟 Stratégie Moyennes Mobiles
    st.subheader("Stratégie Moyennes Mobiles (MA)")

    try:
        ma_result = moving_average_strategy(
            data["Close"],
            short_window=short_window,
            long_window=long_window,
            initial_capital=100.0,
        )

        ma_portfolio = ma_result["portfolio"]
        ma_metrics = ma_result["metrics"]

        # Comparaison des deux portefeuilles
        comparison_df = pd.DataFrame(
            {
                "Buy & Hold": bh_portfolio,
                "MA Strategy": ma_portfolio,
            }
        )

        st.write("Comparaison de la valeur du portefeuille (Buy & Hold vs Stratégie MA)")
        st.line_chart(comparison_df, use_container_width=True)

        # Metrics de la stratégie MA
        st.write("Metrics de la stratégie MA")
        ma_cum_return = ma_metrics["cumulative_return"]
        ma_vol_daily = ma_metrics["vol_daily"]
        ma_sharpe = ma_metrics["sharpe"]
        ma_max_dd = ma_metrics["max_drawdown"]

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Perf cumulée MA", f"{ma_cum_return * 100:.2f}%")
        col6.metric("Volatilité MA", f"{ma_vol_daily * 100:.2f}%")

        if ma_sharpe is not None and not np.isnan(ma_sharpe):
            col7.metric("Sharpe MA", f"{ma_sharpe:.2f}")
        else:
            col7.metric("Sharpe MA", "N/A")

        col8.metric("Max Drawdown MA", f"{ma_max_dd * 100:.2f}%")

    except ValueError as ve_strategy:
        # Erreur spécifique à la stratégie (ex: short_window >= long_window)
        st.warning(str(ve_strategy))

    # 1️⃣1️⃣ Données brutes
    with st.expander("Voir les dernières lignes de données"):
        st.dataframe(data.tail())

except ValueError as ve:
    st.error(str(ve))
except Exception as e:
    st.error(f"Erreur lors de la récupération ou du traitement des données : {e}")

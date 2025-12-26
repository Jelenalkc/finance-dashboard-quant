import streamlit as st
import pandas as pd
import numpy as np

# Internal module imports for financial logic and multi-asset page
from single_asset import (
    fetch_data,
    compute_returns,
    compute_metrics,
    backtest_buy_and_hold,
    moving_average_strategy,
)
from portfolio import show_portfolio_page

def show_single_asset_page():
    st.title("Quant A - Single Asset Dashboard")

    # Sidebar: Asset selection
    ticker = st.sidebar.text_input("Ticker (Yahoo Finance)", value="BTC-USD")

    # Sidebar: Timeframe settings
    period = st.sidebar.selectbox(
        "Analysis Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=5,
    )
    interval = st.sidebar.selectbox(
        "Data Interval",
        ["1m", "5m", "15m", "30m", "1h", "1d"],
        index=5,
    )

    # Sidebar: Moving Average Strategy parameters
    short_window = st.sidebar.number_input(
        "Short MA Window", min_value=5, max_value=60, value=20, step=1
    )
    long_window = st.sidebar.number_input(
        "Long MA Window", min_value=10, max_value=200, value=50, step=1
    )

    st.write(f"### Historical Data for: `{ticker}`")

    try:
        # Load market data
        data = fetch_data(ticker, period=period, interval=interval)

        # Display latest closing price
        last_price = float(data["Close"].iloc[-1])
        st.metric(label="Latest Close Price", value=f"{last_price:,.4f}")

        # Benchmark calculations (Buy & Hold)
        returns = compute_returns(data["Close"])
        bh_metrics = compute_metrics(returns, data["Close"])

        # Metric extraction for UI display
        perf = bh_metrics["cumulative_return"]
        vol = bh_metrics["vol_daily"]
        sharpe = bh_metrics["sharpe"]
        mdd = bh_metrics["max_drawdown"]

        st.subheader("Buy & Hold Benchmark Metrics")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Cumulative Perf.", f"{perf:.2%}")
        m_col2.metric("Daily Volatility", f"{vol:.2%}")

        if sharpe is not None and not np.isnan(sharpe):
            m_col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
        else:
            m_col3.metric("Sharpe Ratio", "N/A")

        m_col4.metric("Max Drawdown", f"{mdd:.2%}")

        # Price History Visualization
        st.subheader("Historical Price Chart (Close)")
        st.line_chart(data["Close"], use_container_width=True)

        # Equity Curve Visualization
        st.subheader("Buy & Hold Equity Curve (Initial Capital = 100)")
        bh_equity = backtest_buy_and_hold(returns, initial_capital=100.0)
        st.line_chart(bh_equity, use_container_width=True)

        # Moving Average Strategy Execution
        st.subheader("Moving Average (MA) Strategy Results")

        try:
            strategy_results = moving_average_strategy(
                data["Close"],
                short_window=short_window,
                long_window=long_window,
                initial_capital=100.0,
            )

            ma_equity = strategy_results["portfolio"]
            ma_metrics = strategy_results["metrics"]

            # Strategy vs. Benchmark comparison
            comparison_df = pd.DataFrame(
                {
                    "Buy & Hold": bh_equity,
                    "MA Strategy": ma_equity,
                }
            )

            st.write("Equity Curve Comparison: Strategy vs. Benchmark")
            st.line_chart(comparison_df, use_container_width=True)

            # Strategy specific metrics
            st.write("Quantitative Metrics (Strategy)")
            s_perf = ma_metrics["cumulative_return"]
            s_vol = ma_metrics["vol_daily"]
            s_sharpe = ma_metrics["sharpe"]
            s_mdd = ma_metrics["max_drawdown"]

            s_col1, s_col2, s_col3, s_col4 = st.columns(4)
            s_col1.metric("Strategy Perf.", f"{s_perf:.2%}")
            s_col2.metric("Strategy Vol.", f"{s_vol:.2%}")

            if s_sharpe is not None and not np.isnan(s_sharpe):
                s_col3.metric("Strategy Sharpe", f"{s_sharpe:.2f}")
            else:
                s_col3.metric("Strategy Sharpe", "N/A")

            s_col4.metric("Strategy Max DD", f"{s_mdd:.2%}")

        except ValueError as strategy_error:
            st.warning(f"Strategy Warning: {strategy_error}")

        # Data inspection panel
        with st.expander("Show Raw Historical Data (Last 5 rows)"):
            st.dataframe(data.tail())

    except ValueError as val_error:
        st.error(f"Input Error: {val_error}")
    except Exception as general_error:
        st.error(f"An unexpected error occurred during data processing: {general_error}")


# Main application configuration
st.set_page_config(page_title="Quant A Finance Dashboard", layout="wide")

# Navigation Sidebar
module_selection = st.sidebar.radio(
    "Select Module",
    ["Quant A - Single Asset", "Quant B - Portfolio"],
)

# Route to the appropriate page function
if module_selection.startswith("Quant A"):
    show_single_asset_page()
else:
    show_portfolio_page()

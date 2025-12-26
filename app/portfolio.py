import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

def show_portfolio_page():
    st.title("Quant B - Portfolio Management")

    # Asset selection (Multi-Asset)
    # User must select at least 3 assets for a valid simulation
    tickers = st.multiselect(
        "Select your assets (Min. 3)",
        ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD", "EURUSD=X"],
        default=["AAPL", "MSFT", "BTC-USD"]
    )

    if len(tickers) < 3:
        st.warning("Please select at least 3 assets for the simulation.")
        return

    # Analysis period selection
    period = st.selectbox("Analysis period", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)

    if st.button("Run Analysis"):
        with st.spinner('Downloading market data...'):
            
            # Data retrieval logic
            try:
                # Disable auto_adjust to inspect raw columns first
                raw_data = yf.download(tickers, period=period, auto_adjust=False)
            except Exception as e:
                st.error(f"Download error: {e}")
                return

            if raw_data.empty:
                st.error("No data retrieved. Please check your connection or tickers.")
                return

            # Intelligent price column selection (prefer Adj Close for returns)
            if 'Adj Close' in raw_data.columns:
                data = raw_data['Adj Close']
            elif 'Close' in raw_data.columns:
                st.warning("Notice: 'Adj Close' not found, using 'Close' prices instead.")
                data = raw_data['Close']
            else:
                st.error("Critical error: Could not locate price columns in the retrieved data.")
                return

            # Clean missing values
            data = data.dropna()

            # Strategy Configuration (Weights)
            st.subheader("Allocation Strategy")
            st.caption("Define the weight for each asset (Sum must equal 1.0)")
            
            asset_weights = {}
            columns = st.columns(len(tickers))
            
            for i, ticker in enumerate(tickers):
                # Default to equal weighting
                default_weight = 1.0 / len(tickers)
                asset_weights[ticker] = columns[i].number_input(
                    f"{ticker} Weight", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=float(default_weight), 
                    step=0.05,
                    format="%.2f"
                )

            # Weight validation (handling float precision)
            total_weight = sum(asset_weights.values())
            if not (0.99 <= total_weight <= 1.01):
                st.warning(f"Current total weight is {total_weight:.2f}. It should be exactly 1.00 for a realistic simulation.")

            # Portfolio Calculation
            # Normalize prices to Base 1.0 to compare assets with different price scales
            normalized_prices = data / data.iloc[0]
            
            # Compute portfolio value: Sum(Normalized Price * Weight)
            data['Portfolio'] = 0.0
            for ticker in tickers:
                data['Portfolio'] += normalized_prices[ticker] * asset_weights[ticker]
            
            # Convert to Base 100 for better readability
            portfolio_value_100 = data['Portfolio'] * 100
            
            # Main Visualization
            st.subheader("Performance: Assets vs. Portfolio (Base 100)")
            
            chart_data = normalized_prices[tickers] * 100
            chart_data['MY PORTFOLIO'] = portfolio_value_100
            
            st.line_chart(chart_data)

            # Portfolio Metrics
            st.subheader("Performance & Risk Metrics")
            
            # Calculate daily returns
            portfolio_returns = data['Portfolio'].pct_change().dropna()
            
            metric_col1, metric_col2 = st.columns(2)
            
            # Cumulative Return
            total_return = (data['Portfolio'].iloc[-1] / data['Portfolio'].iloc[0]) - 1
            metric_col1.metric("Cumulative Return", f"{total_return:+.2%}")
            
            # Annualized Volatility (Assuming 252 trading days)
            annualized_vol = portfolio_returns.std() * np.sqrt(252)
            metric_col2.metric("Annualized Volatility", f"{annualized_vol:.2%}")

            # Correlation Matrix
            st.subheader("Correlation Matrix")
            
            asset_returns = data[tickers].pct_change().dropna()
            correlation = asset_returns.corr()
            
            fig = px.imshow(
                correlation, 
                text_auto=True, 
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="Asset Correlation Heatmap"
            )
            st.plotly_chart(fig)

            # Individual Risk Analysis
            st.subheader("Individual Asset Volatility (Risk)")
            individual_vol = asset_returns.std() * np.sqrt(252) 
            st.bar_chart(individual_vol)

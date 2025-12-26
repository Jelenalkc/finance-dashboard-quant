import os
import sys
import datetime as dt
import pandas as pd

# Path configuration to include the project root in the PYTHONPATH
# This ensures imports from the 'app' directory work correctly when run as a script
current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_path)

if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Import logic from the core calculation module
from app.single_asset import fetch_data, compute_returns, compute_metrics

# List of assets to be monitored in the automated daily report
WATCHLIST = ["BTC-USD", "AAPL", "MSFT"]

def generate_daily_report():
    """
    Retrieves historical data for the watchlist and exports key metrics to a CSV report.
    """
    report_entries = []

    for ticker in WATCHLIST:
        try:
            # Use 1 year of daily historical data for standard metric calculations
            market_data = fetch_data(ticker, period="1y", interval="1d")

            returns = compute_returns(market_data["Close"])
            performance_metrics = compute_metrics(returns, market_data["Close"])

            entry = {
                "ticker": ticker,
                "cumulative_return": performance_metrics["cumulative_return"],
                "vol_daily": performance_metrics["vol_daily"],
                "sharpe": performance_metrics["sharpe"],
                "max_drawdown": performance_metrics["max_drawdown"],
            }

        except Exception as e:
            # If processing fails for a specific ticker, log the error within the report
            entry = {
                "ticker": ticker,
                "cumulative_return": None,
                "vol_daily": None,
                "sharpe": None,
                "max_drawdown": None,
                "error": str(e),
            }

        report_entries.append(entry)

    # Create summary DataFrame
    summary_df = pd.DataFrame(report_entries)

    # Manage directory structure for automated exports
    reports_directory = os.path.join(root_path, "reports")
    os.makedirs(reports_directory, exist_ok=True)

    # Generate dated filename for archival purposes
    datestamp = dt.date.today().strftime("%Y-%m-%d")
    output_file = os.path.join(reports_directory, f"daily_report_{datestamp}.csv")

    # Export metrics using high float precision
    summary_df.to_csv(output_file, index=False, float_format="%.6f")
    print(f"Successfully generated daily report: {output_file}")

if __name__ == "__main__":
    generate_daily_report()

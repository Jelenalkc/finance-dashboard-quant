
This project is a comprehensive financial analytics platform built with Python and Streamlit. It integrates real-time market data to provide quantitative insights into individual assets and multi-asset portfolios.

The application is divided into two specialized modules:

Quant A – Single Asset Analytics

Real-time price retrieval using the yfinance API.

Calculation of core quantitative metrics including Cumulative Return, Annualized Volatility, Sharpe Ratio, and Maximum Drawdown.

Strategy backtesting engine comparing a Buy & Hold benchmark against a Moving Average Crossover strategy.

Quant B – Portfolio Management

Multi-asset portfolio simulation and performance tracking.

Risk analysis through asset correlation matrices and individual volatility assessment.

Dynamic weight allocation and rebalancing simulation.

Project Structure
Plaintext

## Project Structure

```text
finance-dashboard-quant/
├── app/
│   ├── main.py            # Streamlit entry point and navigation logic
│   ├── single_asset.py    # Quant A engine (data processing & strategies)
│   └── portfolio.py       # Quant B module (multi-asset analytics)
│
├── cron/
│   ├── daily_report.py    # Automated script for daily CSV report generation
│   └── run_report.sh      # Shell script for cron job automation
│
├── reports/               # Local storage for generated performance reports
│
├── requirements.txt       # Project dependencies (Streamlit, Pandas, Plotly, etc.)
└── README.md              # Project documentation
```
Installation and Setup
Local Environment
To run the dashboard locally, ensure you have Python 3.9+ installed, then follow these steps:

Clone the repository: git clone https://github.com/Jelenalkc/finance-dashboard-quant.git

Install the required dependencies: pip install -r requirements.txt

Launch the Streamlit application: streamlit run app/main.py

Automated Reporting
A performance report is automatically generated every day at midnight (00:00) via a Linux Cron job. The execution is handled by cron/runner.sh, which saves the results as CSV files in the reports/ directory on the AWS server.
(Note: This folder is ignored by Git (.gitignore) to keep the repository clean and separate production data from the source code)

Deployment
The application is optimized for deployment on AWS (EC2) using an Ubuntu environment. It utilizes nohup to maintain a persistent background process, allowing the dashboard to remain accessible via a public IP on port 8501.

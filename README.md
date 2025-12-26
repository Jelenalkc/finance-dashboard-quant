Quantitative Finance Dashboard
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
The project includes a background task located in the cron/ directory. This script is designed to be scheduled via a Linux crontab to generate automated performance reports in the reports/ folder every 24 hours.

Deployment
The application is optimized for deployment on AWS (EC2) using an Ubuntu environment. It utilizes nohup to maintain a persistent background process, allowing the dashboard to remain accessible via a public IP on port 8501.

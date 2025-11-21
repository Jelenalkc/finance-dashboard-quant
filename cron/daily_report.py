# cron/daily_report.py

import os
import sys
import datetime as dt
import pandas as pd

# --- Ajouter la racine du projet au PYTHONPATH ---
# Chemin du dossier courant (cron)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin de la racine du projet (un niveau au-dessus)
ROOT_DIR = os.path.dirname(CURRENT_DIR)

# On ajoute la racine du projet au sys.path si besoin
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Maintenant on peut importer depuis app.single_asset
from app.single_asset import fetch_data, compute_returns, compute_metrics

# Liste d'actifs à suivre dans le rapport quotidien
TICKERS = ["BTC-USD", "AAPL", "MSFT"]


def generate_daily_report():
    """
    Génère un rapport CSV des métriques de base pour chaque ticker.
    """
    rows = []

    for ticker in TICKERS:
        try:
            # On prend par exemple 1 an de données en daily
            data = fetch_data(ticker, period="1y", interval="1d")

            returns = compute_returns(data["Close"])
            metrics = compute_metrics(returns, data["Close"])

            row = {
                "ticker": ticker,
                "cumulative_return": metrics["cumulative_return"],
                "vol_daily": metrics["vol_daily"],
                "sharpe": metrics["sharpe"],
                "max_drawdown": metrics["max_drawdown"],
            }

        except Exception as e:
            # En cas de problème sur un ticker, on l'indique quand même dans le rapport
            row = {
                "ticker": ticker,
                "cumulative_return": None,
                "vol_daily": None,
                "sharpe": None,
                "max_drawdown": None,
                "error": str(e),
            }

        rows.append(row)

    # Création du DataFrame
    df = pd.DataFrame(rows)

    # Dossier de sortie pour les rapports
    reports_dir = os.path.join(ROOT_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    today = dt.date.today().strftime("%Y-%m-%d")
    filename = os.path.join(reports_dir, f"daily_report_{today}.csv")

    df.to_csv(filename, index=False, float_format="%.6f")
    print(f"Rapport sauvegardé dans : {filename}")


if __name__ == "__main__":
    generate_daily_report()

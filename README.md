# Finance Dashboard Quant

Projet de tableau de bord financier réalisé en **Python** avec **Streamlit**.

Le projet est fait à deux :

- **Quant A – Single Asset** (ma partie)  
  - Analyse d’un seul actif (ex : BTC-USD, AAPL, etc.)
  - Récupération automatique des prix avec `yfinance`
  - Calcul de métriques de base (rendement, volatilité, Sharpe, max drawdown)
  - Backtest de stratégies simples (Buy & Hold et stratégie de moyennes mobiles)

- **Quant B – Portfolio** (partie de mon binôme)  
  - Analyse de portefeuilles multi-actifs
  - Corrélations, volatilité de portefeuille, etc.
  - Implémentée dans le fichier `app/portfolio.py`

Les deux modules sont intégrés dans **une seule application Streamlit**.

---

## 1. Structure du projet

```text
finance-dashboard-quant/
├─ app/
│   ├─ main.py            # Point d'entrée Streamlit (menu Quant A / Quant B)
│   ├─ single_asset.py    # Logique Quant A (données, métriques, stratégies)
│   └─ portfolio.py       # Page Quant B (à compléter par mon binôme)
│
├─ cron/
│   └─ daily_report.py    # Script pour générer un rapport CSV quotidien
│
├─ reports/
│   └─ .gitignore         # Les fichiers CSV générés sont ignorés par Git
│
├─ requirements.txt
└─ README.md

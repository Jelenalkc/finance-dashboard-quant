#!/bin/bash

# 1. On se déplace à la racine du projet (C'est CRUCIAL pour les imports Python)
cd /workspaces/finance-dashboard-quant

# 2. On écrit la date dans le log pour prouver que ça se lance
echo "Lancement du Cron à $(date)"

# 3. On lance le script Python avec le bon interpréteur
/home/codespace/.python/current/bin/python cron/daily_report.py
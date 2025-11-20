# app/portfolio.py

import streamlit as st

def show_portfolio_page():
    """
    Page réservée au module Portfolio (Quant B).
    Ton binôme pourra la compléter.
    """
    st.title("Portfolio Dashboard - Quant B")

    st.info(
        "Page en construction pour le module Portfolio (Quant B).\n\n"
        "Idées pour ton binôme :\n"
        "- Sélectionner plusieurs tickers (liste ou multiselect)\n"
        "- Télécharger les prix historiques pour chaque actif\n"
        "- Calculer la matrice de corrélation\n"
        "- Calculer volatilité, rendement attendu, etc.\n"
        "- Simuler un portefeuille (poids des actifs) et afficher les metrics."
    )

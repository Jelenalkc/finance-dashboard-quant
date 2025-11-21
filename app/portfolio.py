import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

def show_portfolio_page():
    st.title("📊 Quant B - Gestion de Portefeuille")

    # 1. Sélection des actifs (Multi-Asset)
    # L'utilisateur doit pouvoir choisir au moins 3 actifs
    tickers = st.multiselect(
        "Choisissez vos actifs (Min. 3)",
        ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD", "EURUSD=X"],
        default=["AAPL", "MSFT", "BTC-USD"]
    )

    if len(tickers) < 3:
        st.warning("Veuillez sélectionner au moins 3 actifs pour la simulation.")
        return

    # 2. Sélection de la période
    period = st.selectbox("Période d'analyse", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)

    if st.button("Lancer l'analyse"):
        with st.spinner('Récupération des données...'):
            
            # --- DÉBUT DE LA SÉCURITÉ DE TÉLÉCHARGEMENT ---
            try:
                # On télécharge tout sans ajustement automatique pour voir les colonnes brutes
                raw_data = yf.download(tickers, period=period, auto_adjust=False)
            except Exception as e:
                st.error(f"Erreur lors du téléchargement : {e}")
                return

            # Vérification si le téléchargement a retourné quelque chose
            if raw_data.empty:
                st.error("Erreur : Aucune donnée n'a été récupérée. Vérifiez votre connexion.")
                return

            # Sélection intelligente de la colonne de prix
            if 'Adj Close' in raw_data.columns:
                data = raw_data['Adj Close']
            elif 'Close' in raw_data.columns:
                st.warning("Info : 'Adj Close' non trouvé, utilisation des prix de clôture 'Close'.")
                data = raw_data['Close']
            else:
                st.error("Erreur critique : Impossible de trouver les colonnes de prix dans les données reçues.")
                return

            # Nettoyage des données manquantes
            data = data.dropna()
            # --- FIN DE LA SÉCURITÉ ---

            # --- 3. DÉFINITION DES POIDS (NOUVEAU) ---
            st.subheader("⚖️ Définition de la Stratégie (Poids)")
            st.caption("Définissez la part de chaque actif dans votre portefeuille (La somme doit faire 1.0)")
            
            weights = {}
            # On crée des colonnes pour afficher les inputs proprement
            cols = st.columns(len(tickers))
            
            for i, ticker in enumerate(tickers):
                # On donne par défaut un poids égal (1/nombre d'actifs)
                default_weight = 1.0 / len(tickers)
                weights[ticker] = cols[i].number_input(
                    f"Poids {ticker}", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=float(default_weight), 
                    step=0.05,
                    format="%.2f"
                )

            # Vérification que la somme fait environ 1 (avec une petite marge d'erreur float)
            total_weight = sum(weights.values())
            if not (0.99 <= total_weight <= 1.01):
                st.warning(f"⚠️ La somme des poids est de {total_weight:.2f}. Elle devrait être égale à 1.00 pour une simulation réaliste.")

            # --- 4. CALCUL DU PORTEFEUILLE (NOUVEAU) ---
            # On normalise les prix (base 1) pour que tout commence au même point
            # Cela permet de comparer des actifs aux prix très différents (ex: Bitcoin vs Apple)
            normalized_data = data / data.iloc[0]
            
            # On calcule la valeur du portefeuille : Somme(Prix normalisé * Poids)
            data['Portfolio'] = 0 # Initialisation de la colonne
            for ticker in tickers:
                data['Portfolio'] += normalized_data[ticker] * weights[ticker]
            
            # On remet en base 100 pour l'affichage (plus lisible)
            # Si le portefeuille vaut 110, on a gagné 10%
            portfolio_value = data['Portfolio'] * 100
            
            # --- 5. VISUALISATION PRINCIPALE ---
            st.subheader("Performance : Actifs vs Mon Portefeuille (Base 100)")
            
            # On prépare les données pour le graphique : les actifs individuels + le portefeuille global
            chart_data = normalized_data[tickers] * 100
            chart_data['MY PORTFOLIO'] = portfolio_value
            
            st.line_chart(chart_data)

            # --- 6. MÉTRIQUES DU PORTEFEUILLE (NOUVEAU) ---
            st.subheader("📊 Métriques du Portefeuille")
            
            # Calcul des rendements quotidiens du portefeuille
            portfolio_returns = data['Portfolio'].pct_change().dropna()
            
            col1, col2 = st.columns(2)
            
            # Rendement cumulé (Performance totale sur la période)
            cum_return = (data['Portfolio'].iloc[-1] / data['Portfolio'].iloc[0]) - 1
            col1.metric("Rendement Cumulé", f"{cum_return:+.2%}")
            
            # Volatilité (écart-type annualisé)
            # 252 correspond au nombre moyen de jours de bourse par an
            port_volatility = portfolio_returns.std() * np.sqrt(252)
            col2.metric("Volatilité Annualisée", f"{port_volatility:.2%}")

            # --- 7. MATRICE DE CORRÉLATION (CLASSIQUE) ---
            st.subheader("Matrice de Corrélation")
            
            # Calcul des rendements individuels pour la corrélation
            returns = data[tickers].pct_change().dropna()
            corr_matrix = returns.corr()
            
            # Utilisation de Plotly pour une heatmap interactive
            fig = px.imshow(
                corr_matrix, 
                text_auto=True, 
                aspect="auto",
                color_continuous_scale='RdBu_r', # Rouge = Corrélation inverse, Bleu = Positive
                title="Corrélation entre les actifs"
            )
            st.plotly_chart(fig)

            # --- 8. VOLATILITÉ INDIVIDUELLE ---
            st.subheader("Volatilité par Actif (Risque)")
            volatility = returns.std() * np.sqrt(252) 
            st.bar_chart(volatility)
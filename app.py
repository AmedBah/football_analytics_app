import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from statsbombpy import sb

# Configuration de la page
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Template HTML/CSS sportif
st.markdown("""
<style>
    /* Importation de la police Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* Variables de style */
    :root {
        --primary-color: #00A1D6; /* Bleu sportif vif */
        --secondary-color: #1A3C34; /* Vert sombre football */
        --accent-color: #FFD700; /* Jaune pour accents */
        --bg-color: #F5F6F5; /* Fond gris clair */
        --card-bg: #FFFFFF;
        --text-color: #1A3C34;
        --shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Style global */
    body {
        font-family: 'Roboto', sans-serif;
        background-color: var(--bg-color);
        color: var(--text-color);
        margin: 0;
        padding: 0;
    }

    /* En-tête principal */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-align: center;
        margin: 2rem 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Sous-titre */
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--secondary-color);
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* Conteneur principal */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }

    /* Cartes */
    .card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--shadow);
        margin-bottom: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid var(--primary-color);
    }

    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }

    .card h3 {
        color: var(--secondary-color);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .card p, .card ul {
        color: var(--text-color);
        font-size: 1rem;
        line-height: 1.6;
    }

    .card ul {
        list-style-type: none;
        padding-left: 0;
    }

    .card ul li:before {
        content: "⚽ ";
        color: var(--accent-color);
    }

    /* Texte d'introduction */
    .intro-text {
        font-size: 1.2rem;
        text-align: center;
        color: var(--text-color);
        max-width: 900px;
        margin: 0 auto 3rem auto;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
        box-shadow: var(--shadow);
    }

    /* Boutons */
    .stButton>button {
        background-color: var(--primary-color);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 25px;
        font-weight: 700;
        text-transform: uppercase;
        border: none;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #007BB5;
    }

    /* Ajustement des colonnes */
    .stColumn {
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Fonctions pour charger les données StatsBomb (inchangées)
@st.cache_data
def load_competitions():
    return sb.competitions()

@st.cache_data
def load_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

@st.cache_data
def load_teams(competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    teams = pd.concat([matches['home_team'], matches['away_team']]).drop_duplicates().reset_index(drop=True)
    return teams

@st.cache_data
def load_players(team_name, competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    match_ids = matches[
        (matches['home_team'] == team_name) | (matches['away_team'] == team_name)
    ]['match_id'].tolist()
    
    if not match_ids:
        return pd.DataFrame()
    
    lineups = sb.lineups(match_id=match_ids[0])
    players = lineups.get(team_name, pd.DataFrame())
    return players

# Page d'accueil
def main():
    st.markdown("<h1 class='main-header'>⚽ Football Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class='intro-text'>
        Plongez dans l'univers de l'analyse footballistique avancée. Exploitez des données précises pour optimiser les performances des équipes et des joueurs comme jamais auparavant.
    </div>
    """, unsafe_allow_html=True)
    
    # Conteneur pour les fonctionnalités
    st.markdown("<div class='container'>", unsafe_allow_html=True)
    
    # Présentation des fonctionnalités avec colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>📊 Analyse d'Équipe</h3>
            <p>Explorez les performances collectives avec des outils visuels puissants.</p>
            <ul>
                <li>Classement et stats clés</li>
                <li>Comparaisons tactiques</li>
                <li>Heatmaps dynamiques</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <h3>👤 Analyse de Joueurs</h3>
            <p>Évaluez les talents individuels avec des métriques détaillées.</p>
            <ul>
                <li>Comparaisons inter-joueurs</li>
                <li>Suivi des performances</li>
                <li>Statistiques personnalisées</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card'>
            <h3>🔍 Analyse Tactique</h3>
            <p>Décryptez les schémas de jeu pour une stratégie gagnante.</p>
            <ul>
                <li>Cartes de chaleur</li>
                <li>Schémas de passes</li>
                <li>Analyse des mouvements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Données disponibles
    st.markdown("<h2 class='sub-header'>Données à Votre Portée</h2>", unsafe_allow_html=True)
    
    try:
        competitions = load_competitions()
        st.write("Compétitions disponibles dans StatsBomb :")
        st.dataframe(competitions.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.info("Vérifiez votre accès aux API StatsBomb.")

if __name__ == "__main__":
    main()
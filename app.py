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

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        color: #333333;
    }
    /* Amélioration de la visibilité du texte */
    p, li, h1, h2, h3, h4, h5, h6 {
        color: #333333;
    }
    .stMarkdown {
        color: #333333;
    }
    /* Assurer que le texte est visible sur fond sombre */
    div[data-testid="stVerticalBlock"] {
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour charger les données StatsBomb
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
    
    # Prendre le premier match pour obtenir les joueurs
    lineups = sb.lineups(match_id=match_ids[0])
    players = lineups.get(team_name, pd.DataFrame())
    return players

# Page d'accueil
def main():
    st.markdown("<h1 class='main-header'>⚽ Football Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class='card'>
        <h2 class='sub-header'>Bienvenue dans votre plateforme d'analyse footballistique</h2>
        <p>Cette application permet aux entraîneurs et analystes d'explorer et d'analyser les performances des équipes et des joueurs 
        grâce à la data science appliquée au football. Utilisez la barre de navigation ci-dessus pour accéder aux différentes sections d'analyse.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Présentation des fonctionnalités
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>📊 Analyse d'Équipe</h3>
            <p>Explorez les performances globales, comparez les équipes et visualisez les tendances tactiques.</p>
            <ul>
                <li>Classement et performance</li>
                <li>Comparaison entre équipes</li>
                <li>Heatmaps et zones d'action</li>
                <li>Corrélations statistiques</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <h3>👤 Analyse de Joueurs</h3>
            <p>Évaluez les performances individuelles, comparez les joueurs et suivez leur évolution.</p>
            <ul>
                <li>Comparaison intra-club et inter-club</li>
                <li>Analyse des variations de performance</li>
                <li>Suivi des performances dans le temps</li>
                <li>Chronologie annotée</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card'>
            <h3>🔍 Analyse Tactique</h3>
            <p>Visualisez les schémas tactiques, les zones d'influence et les circuits de jeu.</p>
            <ul>
                <li>Cartes de chaleur</li>
                <li>Schémas tactiques</li>
                <li>Flèches de mouvement</li>
                <li>Analyse des circuits préférentiels</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Données disponibles
    st.markdown("<h2 class='sub-header'>Données disponibles</h2>", unsafe_allow_html=True)
    
    try:
        competitions = load_competitions()
        st.write("Compétitions disponibles dans StatsBomb:")
        st.dataframe(competitions.head())
    except Exception as e:
        st.error(f"Erreur lors du chargement des données StatsBomb: {e}")
        st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

if __name__ == "__main__":
    main()

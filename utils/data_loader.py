#data_loader
import pandas as pd
import numpy as np
from statsbombpy import sb
import streamlit as st

# -----------------------------
# FONCTIONS DE CHARGEMENT
# -----------------------------

@st.cache_data
def load_competitions():
    """Charge la liste des compétitions disponibles dans StatsBomb."""
    try:
        competitions = sb.competitions()
        return competitions
    except Exception as e:
        st.error(f"Erreur lors du chargement des compétitions : {e}")
        return pd.DataFrame()

@st.cache_data
def load_matches(competition_id: int, season_id: int):
    """Charge les matchs d'une compétition spécifique."""
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        return matches
    except Exception as e:
        st.error(f"Erreur lors du chargement des matchs : {e}")
        return pd.DataFrame()

@st.cache_data
def load_teams(competition_id: int, season_id: int):
    """Retourne la liste des équipes participant à la compétition."""
    try:
        matches = load_matches(competition_id, season_id)
        if matches.empty:
            return []
        teams = pd.concat([matches['home_team'], matches['away_team']]).drop_duplicates().tolist()
        return teams
    except Exception as e:
        st.error(f"Erreur lors du chargement des équipes : {e}")
        return []

@st.cache_data
def load_players(team_name: str, competition_id: int, season_id: int):
    """Charge les joueurs d'une équipe à partir de la composition d’un match."""
    try:
        matches = load_matches(competition_id, season_id)
        match_ids = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]['match_id'].tolist()
        if not match_ids:
            return pd.DataFrame()
        lineups = sb.lineups(match_id=match_ids[0])
        return lineups.get(team_name, pd.DataFrame())
    except Exception as e:
        st.error(f"Erreur lors du chargement des joueurs : {e}")
        return pd.DataFrame()

#@st.cache_data
def load_events(match_id: int):
    """Charge tous les événements d’un match donné."""
    try:
        return sb.events(match_id=match_id)
    except Exception as e:
        st.error(f"Erreur lors du chargement des événements : {e}")
        return pd.DataFrame()

@st.cache_data
def load_filtered_events(match_id: int, event_type: str = None, team_name: str = None):
    """Filtre les événements d’un match selon le type et/ou l’équipe."""
    try:
        events = load_events(match_id)
        if event_type:
            events = events[events['type'] == event_type]
        if team_name:
            events = events[events['team'] == team_name]
        return events
    except Exception as e:
        st.error(f"Erreur lors du filtrage des événements : {e}")
        return pd.DataFrame()

import pandas as pd
import numpy as np
from statsbombpy import sb
import streamlit as st

# Fonction pour charger les compétitions disponibles dans StatsBomb
@st.cache_data
def load_competitions():
    """
    Charge les compétitions disponibles dans StatsBomb.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les informations sur les compétitions disponibles.
    """
    try:
        return sb.competitions()
    except Exception as e:
        st.error(f"Erreur lors du chargement des compétitions: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

# Fonction pour charger les matchs d'une compétition
@st.cache_data
def load_matches(competition_id, season_id):
    """
    Charge les matchs d'une compétition spécifique.
    
    Args:
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        pandas.DataFrame: DataFrame contenant les informations sur les matchs.
    """
    try:
        return sb.matches(competition_id=competition_id, season_id=season_id)
    except Exception as e:
        st.error(f"Erreur lors du chargement des matchs: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

# Fonction pour extraire les équipes d'une compétition
@st.cache_data
def load_teams(competition_id, season_id):
    """
    Extrait la liste des équipes participant à une compétition.
    
    Args:
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        list: Liste des noms d'équipes.
    """
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        teams = pd.concat([matches['home_team'], matches['away_team']]).drop_duplicates().reset_index(drop=True)
        return teams.tolist()
    except Exception as e:
        st.error(f"Erreur lors du chargement des équipes: {e}")
        # Retourner une liste vide en cas d'erreur
        return []

# Fonction pour charger les joueurs d'une équipe
@st.cache_data
def load_players(team_name, competition_id, season_id):
    """
    Charge les joueurs d'une équipe spécifique.
    
    Args:
        team_name (str): Nom de l'équipe.
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        pandas.DataFrame: DataFrame contenant les informations sur les joueurs.
    """
    try:
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
    except Exception as e:
        st.error(f"Erreur lors du chargement des joueurs: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

# Fonction pour charger les événements d'un match
@st.cache_data
def load_events(match_id):
    """
    Charge les événements d'un match spécifique.
    
    Args:
        match_id (int): ID du match.
        
    Returns:
        pandas.DataFrame: DataFrame contenant les événements du match.
    """
    try:
        return sb.events(match_id=match_id)
    except Exception as e:
        st.error(f"Erreur lors du chargement des événements: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

# Fonction pour charger les événements filtrés par type
@st.cache_data
def load_filtered_events(match_id, event_type=None, team_name=None):
    """
    Charge les événements d'un match filtrés par type et/ou équipe.
    
    Args:
        match_id (int): ID du match.
        event_type (str, optional): Type d'événement à filtrer.
        team_name (str, optional): Nom de l'équipe à filtrer.
        
    Returns:
        pandas.DataFrame: DataFrame contenant les événements filtrés.
    """
    try:
        events = sb.events(match_id=match_id)
        
        if event_type:
            events = events[events['type'] == event_type]
        
        if team_name:
            events = events[events['team'] == team_name]
        
        return events
    except Exception as e:
        st.error(f"Erreur lors du chargement des événements filtrés: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

# Fonction pour calculer les statistiques d'une équipe
@st.cache_data
def calculate_team_stats(team_name, competition_id, season_id):
    """
    Calcule les statistiques globales d'une équipe pour une compétition.
    
    Args:
        team_name (str): Nom de l'équipe.
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        dict: Dictionnaire contenant les statistiques de l'équipe.
    """
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        team_matches = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]
        
        stats = {
            'matches_played': len(team_matches),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0
        }
        
        for _, match in team_matches.iterrows():
            if match['home_team'] == team_name:
                if match['home_score'] > match['away_score']:
                    stats['wins'] += 1
                elif match['home_score'] == match['away_score']:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
                
                stats['goals_for'] += match['home_score']
                stats['goals_against'] += match['away_score']
            else:  # away_team == team_name
                if match['away_score'] > match['home_score']:
                    stats['wins'] += 1
                elif match['away_score'] == match['home_score']:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
                
                stats['goals_for'] += match['away_score']
                stats['goals_against'] += match['home_score']
        
        stats['points'] = stats['wins'] * 3 + stats['draws']
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        
        return stats
    except Exception as e:
        st.error(f"Erreur lors du calcul des statistiques d'équipe: {e}")
        # Retourner un dictionnaire vide en cas d'erreur
        return {}

# Fonction pour calculer les statistiques d'un joueur
@st.cache_data
def calculate_player_stats(player_name, team_name, competition_id, season_id):
    """
    Calcule les statistiques d'un joueur pour une équipe et une compétition.
    
    Args:
        player_name (str): Nom du joueur.
        team_name (str): Nom de l'équipe.
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        dict: Dictionnaire contenant les statistiques du joueur.
    """
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        match_ids = matches[
            (matches['home_team'] == team_name) | (matches['away_team'] == team_name)
        ]['match_id'].tolist()
        
        if not match_ids:
            return {}
        
        player_stats = {
            'matches_played': 0,
            'minutes_played': 0,
            'goals': 0,
            'assists': 0,
            'shots': 0,
            'passes': 0,
            'pass_accuracy': 0,
            'key_passes': 0,
            'tackles': 0,
            'interceptions': 0
        }
        
        # Cette partie est simplifiée car l'extraction des statistiques détaillées
        # nécessiterait une analyse approfondie des événements de chaque match
        # Dans une application réelle, il faudrait parcourir tous les événements
        # et calculer les statistiques en fonction des types d'événements
        
        # Simuler des statistiques fictives pour l'exemple
        player_stats['matches_played'] = np.random.randint(1, len(match_ids) + 1)
        player_stats['minutes_played'] = player_stats['matches_played'] * np.random.randint(60, 90)
        player_stats['goals'] = np.random.randint(0, 10)
        player_stats['assists'] = np.random.randint(0, 8)
        player_stats['shots'] = player_stats['goals'] * np.random.randint(2, 5)
        player_stats['passes'] = player_stats['matches_played'] * np.random.randint(30, 70)
        player_stats['pass_accuracy'] = np.random.randint(70, 95)
        player_stats['key_passes'] = np.random.randint(0, 20)
        player_stats['tackles'] = player_stats['matches_played'] * np.random.randint(1, 5)
        player_stats['interceptions'] = player_stats['matches_played'] * np.random.randint(1, 4)
        
        return player_stats
    except Exception as e:
        st.error(f"Erreur lors du calcul des statistiques de joueur: {e}")
        # Retourner un dictionnaire vide en cas d'erreur
        return {}

# Fonction pour créer un classement de la compétition
@st.cache_data
def create_standings(competition_id, season_id):
    """
    Crée un classement pour une compétition spécifique.
    
    Args:
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
        
    Returns:
        pandas.DataFrame: DataFrame contenant le classement.
    """
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        teams_data = {}
        
        for _, match in matches.iterrows():
            home_team = match['home_team']
            away_team = match['away_team']
            home_score = match['home_score']
            away_score = match['away_score']
            
            # Initialiser les équipes si elles n'existent pas encore
            if home_team not in teams_data:
                teams_data[home_team] = {'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'points': 0}
            if away_team not in teams_data:
                teams_data[away_team] = {'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'points': 0}
            
            # Mettre à jour les statistiques
            teams_data[home_team]['matches'] += 1
            teams_data[away_team]['matches'] += 1
            
            teams_data[home_team]['goals_for'] += home_score
            teams_data[home_team]['goals_against'] += away_score
            teams_data[away_team]['goals_for'] += away_score
            teams_data[away_team]['goals_against'] += home_score
            
            if home_score > away_score:  # Victoire à domicile
                teams_data[home_team]['wins'] += 1
                teams_data[home_team]['points'] += 3
                teams_data[away_team]['losses'] += 1
            elif home_score < away_score:  # Victoire à l'extérieur
                teams_data[away_team]['wins'] += 1
                teams_data[away_team]['points'] += 3
                teams_data[home_team]['losses'] += 1
            else:  # Match nul
                teams_data[home_team]['draws'] += 1
                teams_data[home_team]['points'] += 1
                teams_data[away_team]['draws'] += 1
                teams_data[away_team]['points'] += 1
        
        # Créer le dataframe
        standings = pd.DataFrame.from_dict(teams_data, orient='index')
        standings['team'] = standings.index
        standings['goal_difference'] = standings['goals_for'] - standings['goals_against']
        standings = standings.sort_values(by=['points', 'goal_difference', 'goals_for'], ascending=False).reset_index(drop=True)
        standings.index = standings.index + 1  # Commencer l'index à 1
        
        return standings
    except Exception as e:
        st.error(f"Erreur lors de la création du classement: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

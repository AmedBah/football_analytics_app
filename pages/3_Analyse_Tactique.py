import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from statsbombpy import sb
from mplsoccer import Pitch, VerticalPitch
import sys
import os

# Ajouter le répertoire parent au chemin pour importer les fonctions utilitaires
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import (
    load_competitions,
    load_matches,
    load_teams,
    load_events,
)

# Configuration de la page
st.set_page_config(
    page_title="Analyse Tactique",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1E88E5;
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
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-header'>🔍 Analyse Tactique</h1>", unsafe_allow_html=True)

# Barre latérale pour les filtres
st.sidebar.header("Filtres")

# Chargement des compétitions
try:
    competitions = load_competitions()
    if competitions.empty:
        st.error("Aucune compétition disponible. Vérifiez votre accès aux données StatsBomb.")
        st.stop()

    # Sélection de la compétition
    competition_options = competitions[
        ["competition_id", "competition_name", "season_id", "season_name"]
    ].drop_duplicates()
    competition_options["display_name"] = (
        competition_options["competition_name"] + " - " + competition_options["season_name"]
    )
    selected_competition = st.sidebar.selectbox(
        "Sélectionner une compétition",
        options=competition_options["display_name"].tolist(),
        index=0,
    )

    # Récupérer les IDs de la compétition et de la saison sélectionnées
    selected_comp_data = competition_options[
        competition_options["display_name"] == selected_competition
    ]
    competition_id = selected_comp_data["competition_id"].values[0]
    season_id = selected_comp_data["season_id"].values[0]

    # Chargement des équipes
    teams = load_teams(competition_id, season_id)
    if not teams:
        st.error("Aucune équipe disponible pour cette compétition.")
        st.stop()

    # Sélection de l'équipe
    selected_team = st.sidebar.selectbox(
        "Sélectionner une équipe",
        options=teams,
        index=0,
    )

    # Chargement des matchs
    matches = load_matches(competition_id, season_id)
    team_matches = matches[(matches["home_team"] == selected_team) | (matches["away_team"] == selected_team)]

    # Onglets pour les différentes analyses
    tab1, tab2, tab3 = st.tabs([
        "Carte de Chaleur",
        "Schéma Tactique",
        "Flèches de Mouvement",
    ])

    # Onglet 1: Carte de Chaleur
    with tab1:
        st.markdown("<h2 class='sub-header'>Carte de Chaleur (Heatmap)</h2>", unsafe_allow_html=True)

        # Sélection du type d'événement
        event_type = st.selectbox(
            "Sélectionner un type d'événement",
            options=["Passes", "Tirs", "Récupérations", "Pertes de balle", "Duels"],
            index=0,
        )

        # Sélection de la période
        period = st.radio(
            "Sélectionner une période",
            options=["Match complet", "1ère mi-temps", "2ème mi-temps"],
            horizontal=True,
        )

        # Créer un terrain de football
        pitch = Pitch(pitch_type="statsbomb", line_zorder=2, pitch_color="#22312b", line_color="#efefef")
        fig, ax = pitch.draw(figsize=(12, 8))

        # Extraire les positions des actions
        def extract_heatmap_data(team_name, matches, event_type, period):
            x_coords = []
            y_coords = []

            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                team_events = events[events["team"] == team_name]

                if period == "Match complet":
                    filtered_events = team_events
                elif period == "1ère mi-temps":
                    filtered_events = team_events[team_events["minute"] <= 45]
                elif period == "2ème mi-temps":
                    filtered_events = team_events[team_events["minute"] > 45]

                if event_type == "Passes":
                    filtered_events = filtered_events[filtered_events["type"] == "Pass"]
                elif event_type == "Tirs":
                    filtered_events = filtered_events[filtered_events["type"] == "Shot"]
                elif event_type == "Récupérations":
                    filtered_events = filtered_events[filtered_events["type"] == "Ball Recovery"]
                elif event_type == "Pertes de balle":
                    filtered_events = filtered_events[filtered_events["type"] == "Miscontrol"]
                elif event_type == "Duels":
                    filtered_events = filtered_events[filtered_events["type"] == "Duel"]

                for _, event in filtered_events.iterrows():
                    if "location" in event and isinstance(event["location"], list):
                        x_coords.append(event["location"][0])
                        y_coords.append(event["location"][1])

            return x_coords, y_coords

        x_coords, y_coords = extract_heatmap_data(selected_team, team_matches, event_type, period)

        # Créer la heatmap
        pitch.kdeplot(
            x=x_coords,
            y=y_coords,
            ax=ax,
            cmap="YlOrRd",
            fill=True,
            levels=100,
            alpha=0.7,
        )
        pitch.scatter(
            x=x_coords,
            y=y_coords,
            ax=ax,
            s=50,
            color="white",
            edgecolors="black",
            zorder=3,
        )
        st.pyplot(fig)

        # Ajouter une légende à la heatmap
        st.markdown("""
        <div class='card'>
            <h3>Légende de la Heatmap</h3>
            <p>Les zones en <strong>rouge foncé</strong> indiquent une forte concentration d'actions du type sélectionné.</p>
            <p>Les zones en <strong>orange</strong> indiquent une concentration moyenne d'actions.</p>
            <p>Les zones en <strong>jaune clair</strong> indiquent une faible concentration d'actions.</p>
            <p>Cette visualisation vous aide à comprendre où l'équipe est la plus active sur le terrain.</p>
        </div>
        """, unsafe_allow_html=True)

    # Onglet 2: Schéma Tactique
    with tab2:
        st.markdown("<h2 class='sub-header'>Schéma Tactique</h2>", unsafe_allow_html=True)

        # Sélection de la formation
        formation = st.selectbox(
            "Sélectionner une formation",
            options=["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "5-3-2"],
            index=0,
        )

        # Créer un terrain de football
        pitch = Pitch(pitch_type="statsbomb", line_zorder=2, pitch_color="#22312b", line_color="#efefef")
        fig, ax = pitch.draw(figsize=(12, 8))
        
  
        def place_players(ax, formation, team_name, matches):
            for _, match in matches.iterrows():
                match_id = match["match_id"]
                lineup = sb.lineups(match_id=match_id)
                team_lineup = lineup.get(team_name, pd.DataFrame())

                # Vérification de la structure de "team_lineup"
                print(team_lineup.columns)  # Pour vérifier les colonnes disponibles
                
                # On s'assure que "location" est présent et est sous forme de liste ou de dictionnaire
                if "location" not in team_lineup.columns:
                    print(f"Pas de données de location pour le match {match_id}")
                    continue
                
                # Si la colonne "location" est présente, nous traitons les positions des joueurs
                if formation == "4-3-3":
                    # Gardien
                    goalkeeper = team_lineup[team_lineup["jersey_number"] == 1].iloc[0]
                    goalkeeper_x, goalkeeper_y = goalkeeper["location"]
                    ax.plot(goalkeeper_x, goalkeeper_y, 'ro', markersize=12)
                    ax.text(goalkeeper_x, goalkeeper_y - 5, "GK", fontsize=10, ha='center')

                    # Défenseurs
                    defenders = team_lineup[(team_lineup["position"] == "Defender") & (team_lineup["jersey_number"] != 1)]
                    for _, defender in defenders.iterrows():
                        defender_x, defender_y = defender["location"]
                        ax.plot(defender_x, defender_y, 'bo', markersize=12)
                        ax.text(defender_x, defender_y - 5, f"DEF{defender['jersey_number']}", fontsize=10, ha='center')

                    # Milieux
                    midfielders = team_lineup[(team_lineup["position"] == "Midfielder") & (team_lineup["jersey_number"] != 1)]
                    for _, midfielder in midfielders.iterrows():
                        midfielder_x, midfielder_y = midfielder["location"]
                        ax.plot(midfielder_x, midfielder_y, 'go', markersize=12)
                        ax.text(midfielder_x, midfielder_y - 5, f"MID{midfielder['jersey_number']}", fontsize=10, ha='center')

                    # Attaquants
                    forwards = team_lineup[(team_lineup["position"] == "Forward") & (team_lineup["jersey_number"] != 1)]
                    for _, forward in forwards.iterrows():
                        forward_x, forward_y = forward["location"]
                        ax.plot(forward_x, forward_y, 'yo', markersize=12)
                        ax.text(forward_x, forward_y - 5, f"FW{forward['jersey_number']}", fontsize=10, ha='center')

                # Ajoutez d'autres formations ici si nécessaire

            return fig


        fig = place_players(ax, formation, selected_team, team_matches)
        st.pyplot(fig)

        # Ajouter une légende au schéma tactique
        st.markdown("""
        <div class='card'>
            <h3>Légende du Schéma Tactique</h3>
            <p>Gardien (GK): Red point</p>
            <p>Défenseurs (DEF): Blue points</p>
            <p>Milieux (MID): Green points</p>
            <p>Attaquants (FW): Yellow points</p>
            <p>Cette visualisation montre la position des joueurs sur le terrain selon la formation sélectionnée.</p>
        </div>
        """, unsafe_allow_html=True)

    # Onglet 3: Flèches de Mouvement

    with tab3:
        st.markdown("<h2 class='sub-header'>Flèches de Mouvement (Flow Chart)</h2>", unsafe_allow_html=True)

        # Sélection du type de mouvement
        movement_type = st.selectbox(
            "Sélectionner un type de mouvement",
            options=["Passes", "Progressions avec le ballon", "Transitions défense-attaque"],
            index=0,
        )

        # Créer un terrain de football
        pitch = Pitch(pitch_type="statsbomb", line_zorder=2, pitch_color="#22312b", line_color="#efefef")
        fig, ax = pitch.draw(figsize=(12, 8))

        # Extraire les positions des actions
        def extract_movement_data(team_name, matches, movement_type, period):
            start_x = []
            start_y = []
            end_x = []
            end_y = []

            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                team_events = events[events["team"] == team_name]

                if period == "Match complet":
                    filtered_events = team_events
                elif period == "1ère mi-temps":
                    filtered_events = team_events[team_events["minute"] <= 45]
                elif period == "2ème mi-temps":
                    filtered_events = team_events[team_events["minute"] > 45]

                if movement_type == "Passes":
                    filtered_events = filtered_events[filtered_events["type"] == "Pass"]
                elif movement_type == "Progressions avec le ballon":
                    filtered_events = filtered_events[filtered_events["type"] == "Carry"]
                elif movement_type == "Transitions défense-attaque":
                    filtered_events = filtered_events[
                        (filtered_events["type"] == "Pass") | (filtered_events["type"] == "Carry")
                    ]

                for _, event in filtered_events.iterrows():
                    if "location" in event and isinstance(event["location"], list):
                        start_x.append(event["location"][0])
                        start_y.append(event["location"][1])
                        if "end_location" in event and isinstance(event["end_location"], list):
                            end_x.append(event["end_location"][0])
                            end_y.append(event["end_location"][1])

            return start_x, start_y, end_x, end_y

        start_x, start_y, end_x, end_y = extract_movement_data(selected_team, team_matches, movement_type, period)

        # Vérifier que les listes de départ et de fin ont la même taille
        if len(start_x) == len(end_x) and len(start_y) == len(end_y):
            # Dessiner les flèches de mouvement
            pitch.arrows(
                xstart=start_x,   # Correction ici
                ystart=start_y,   # Correction ici
                xend=end_x,       # Correction ici
                yend=end_y,       # Correction ici
                color="blue",
                alpha=0.6,
                width=1,
                ax=ax,
            )
            st.pyplot(fig)
        else:
            st.error("Les listes de départ et d'arrivée des flèches ne sont pas de même taille. Vérifiez les données.")

        # Ajouter une légende aux flèches de mouvement
        st.markdown("""
        <div class='card'>
            <h3>Légende des Flèches de Mouvement</h3>
            <p>Flèches bleues: Direction des passes ou des progressions avec le ballon.</p>
            <p>Cette visualisation vous aide à comprendre les circuits de jeu préférentiels de l'équipe.</p>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")
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
    load_players,
    load_events,
)

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Joueurs",
    page_icon="👤",
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
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-header'>👤 Analyse de Joueurs</h1>", unsafe_allow_html=True)

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

    # Chargement des joueurs de l'équipe sélectionnée
    players = load_players(selected_team, competition_id, season_id)
    if players.empty:
        st.warning(f"Aucun joueur trouvé pour l'équipe {selected_team}. Veuillez sélectionner une autre équipe.")
        st.stop()

    # Sélection des joueurs pour la comparaison
    player_options = players["player_name"].tolist() if "player_name" in players.columns else []
    selected_player1 = st.sidebar.selectbox(
        "Sélectionner un joueur",
        options=player_options,
        index=0 if player_options else None,
    )
    selected_player2 = st.sidebar.selectbox(
        "Sélectionner un joueur pour comparaison",
        options=["Aucun"] + player_options,
        index=0,
    )

    # Chargement des matchs
    matches = load_matches(competition_id, season_id)
    team_matches = matches[(matches["home_team"] == selected_team) | (matches["away_team"] == selected_team)]

    # Onglets pour les différentes analyses
    tab1, tab2,tab3, tab4 = st.tabs(["Profil","Comparaison de Joueurs", "Suivi des Performances","Analyse "])

    # Onglet 1: Profil du Joueur
    with tab1:
        st.markdown("<h2 class='sub-header'>Profil du Joueur</h2>", unsafe_allow_html=True)

        # Informations de base sur le joueur
        col1, col2 = st.columns([1, 2])
        with col1:
            # Image du joueur (fictive)
            st.image("https://via.placeholder.com/300x400?text=Photo+du+Joueur", caption=selected_player1)
            # Informations de base
            st.markdown(f"""
            <div class='card'>
                <h3>Informations</h3>
                <p><strong>Équipe:</strong> {selected_team}</p>
                <p><strong>Position:</strong> {'Attaquant' if np.random.random() < 0.3 else ('Milieu' if np.random.random() < 0.5 else 'Défenseur')}</p>
                <p><strong>Âge:</strong> {np.random.randint(18, 35)} ans</p>
                <p><strong>Taille:</strong> {np.random.randint(170, 195)} cm</p>
                <p><strong>Pied préféré:</strong> {'Droit' if np.random.random() < 0.7 else 'Gauche'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Statistiques clés
            st.markdown("<h3>Statistiques clés</h3>", unsafe_allow_html=True)

            def calculate_player_stats(player_name, matches):
                goals = 0
                assists = 0
                passes_completed = 0
                shots = 0
                duels_won = 0
                minutes_played = 0

                for _, match in matches.iterrows():
                    match_id = match["match_id"]
                    events = load_events(match_id)
                    player_events = events[events["player"] == player_name]

                    goals += player_events[
                        (player_events["type"] == "Shot") & 
                        (player_events["shot_outcome"] == "Goal")
                    ].shape[0]
                    assists += player_events[player_events["type"] == "Assist"].shape[0]
                    passes_completed += player_events[
                        (player_events["type"] == "Pass") & (player_events["pass_outcome"] == "Complete")
                    ].shape[0]
                    shots += player_events[player_events["type"] == "Shot"].shape[0]
                    duels_won += player_events[
                        (player_events["type"] == "Duel") & (player_events["duel_outcome"] == "Won")
                    ].shape[0]
                    minutes_played += player_events["duration"].sum()

                return {
                    "goals": goals,
                    "assists": assists,
                    "passes_completed": passes_completed,
                    "shots": shots,
                    "duels_won": duels_won,
                    "minutes_played": minutes_played,
                }

            player_stats = calculate_player_stats(selected_player1, team_matches)

            # Afficher les métriques principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{player_stats.get('goals', 0)}</div>
                    <div class='metric-label'>Buts</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{player_stats.get('assists', 0)}</div>
                    <div class='metric-label'>Passes décisives</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{len(team_matches)}</div>
                    <div class='metric-label'>Matchs joués</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{player_stats.get('minutes_played', 0)}</div>
                    <div class='metric-label'>Minutes jouées</div>
                </div>
                """, unsafe_allow_html=True)

            # Statistiques par 90 minutes
            if player_stats["minutes_played"] > 0:
                st.markdown("<h4>Statistiques par 90 minutes</h4>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    goals_per_90 = round(player_stats.get("goals", 0) * 90 / player_stats["minutes_played"], 2)
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{goals_per_90}</div>
                        <div class='metric-label'>Buts / 90 min</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    assists_per_90 = round(player_stats.get("assists", 0) * 90 / player_stats["minutes_played"], 2)
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{assists_per_90}</div>
                        <div class='metric-label'>Passes déc. / 90 min</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    shots_per_90 = round(player_stats.get("shots", 0) * 90 / player_stats["minutes_played"], 2)
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{shots_per_90}</div>
                        <div class='metric-label'>Tirs / 90 min</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    key_passes_per_90 = round(player_stats.get("passes_completed", 0) * 90 / player_stats["minutes_played"], 2)
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{key_passes_per_90}</div>
                        <div class='metric-label'>Passes clés / 90 min</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Onglet 2: Comparaison de Joueurs
    with tab2:
        st.markdown("<h2 class='sub-header'>Comparaison de Joueurs</h2>", unsafe_allow_html=True)

        # Graphique radar pour comparer les joueurs
        st.subheader("Graphique Radar: Comparaison des performances")
        categories = [
            "Buts",
            "Passes décisives",
            "Passes progressives",
            "Tirs",
            "Duels gagnés",
            "Interceptions",
        ]

        # Extraire les statistiques réelles pour chaque joueur
        def get_player_statistics(player_name, matches):
            goals = 0
            assists = 0
            progressive_passes = 0
            shots = 0
            duels_won = 0
            interceptions = 0

            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                player_events = events[events["player"] == player_name]

                # Calculer les statistiques
                goals += player_events[
                    (player_events["type"] == "Shot") & 
                    (player_events["shot_outcome"] == "Goal")
                ].shape[0]

                assists += player_events[player_events["type"] == "Assist"].shape[0]
                progressive_passes += player_events[
                    (player_events["type"] == "Pass") & (player_events["pass_outcome"] == "Complete")
                ].shape[0]
                shots += player_events[player_events["type"] == "Shot"].shape[0]
                duels_won += player_events[
                    (player_events["type"] == "Duel") & (player_events["duel_outcome"] == "Won")
                ].shape[0]
                interceptions += player_events[player_events["type"] == "Interception"].shape[0]

            return [goals, assists, progressive_passes, shots, duels_won, interceptions]

        player1_values = get_player_statistics(selected_player1, team_matches)
        if selected_player2 != "Aucun":
            player2_values = get_player_statistics(selected_player2, team_matches)
            comparison_name = selected_player2
        else:
            # Utiliser la moyenne du poste (données fictives pour l'exemple)
            player2_values = [np.mean(player1_values)] * len(categories)
            comparison_name = "Moyenne du poste"

        # Normaliser les valeurs pour le graphique radar
        max_values = [max(player1_values[i], player2_values[i]) for i in range(len(categories))]
        if any(max_val == 0 for max_val in max_values):
            st.warning("Certaines catégories ont des valeurs nulles. Elles seront ignorées dans le graphique radar.")
            max_values = [max_val if max_val != 0 else 1 for max_val in max_values]

        player1_values_norm = [player1_values[i] / max_values[i] for i in range(len(categories))]
        player2_values_norm = [player2_values[i] / max_values[i] for i in range(len(categories))]

        # Créer le graphique radar
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=player1_values_norm,
                theta=categories,
                fill="toself",
                name=selected_player1,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=player2_values_norm,
                theta=categories,
                fill="toself",
                name=comparison_name,
            )
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                )
            ),
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Boîte à moustaches pour analyser les variations de performance
        st.subheader("Boîte à moustaches: Analyse des variations de performance")
        stat_type = st.selectbox(
            "Sélectionner une statistique",
            options=["Buts", "Passes décisives", "Passes progressives", "Tirs", "Duels gagnés", "Interceptions"],
            index=0,
        )

        # Extraire les données réelles pour la boîte à moustaches
        def extract_boxplot_data(player_name, matches, stat_type):
            data = []
            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                player_events = events[events["player"] == player_name]

                if stat_type == "Buts":
                    data.append( player_events[
                    (player_events["type"] == "Shot") & 
                    (player_events["shot_outcome"] == "Goal")
                ].shape[0])
                    
                elif stat_type == "Passes décisives":
                    data.append(player_events[player_events["type"] == "Assist"].shape[0])
                elif stat_type == "Passes progressives":
                    data.append(
                        player_events[
                            (player_events["type"] == "Pass") & (player_events["pass_outcome"] == "Complete")
                        ].shape[0]
                    )
                elif stat_type == "Tirs":
                    data.append(player_events[player_events["type"] == "Shot"].shape[0])
                elif stat_type == "Duels gagnés":
                    data.append(
                        player_events[
                            (player_events["type"] == "Duel") & (player_events["duel_outcome"] == "Won")
                        ].shape[0]
                    )
                elif stat_type == "Interceptions":
                    data.append(player_events[player_events["type"] == "Interception"].shape[0])

            return data

        player1_data = extract_boxplot_data(selected_player1, team_matches, stat_type)
        if selected_player2 != "Aucun":
            player2_data = extract_boxplot_data(selected_player2, team_matches, stat_type)
        else:
            player2_data = [np.mean(player1_data)] * len(player1_data)

        # Créer le dataframe pour la boîte à moustaches
        boxplot_data = pd.DataFrame(
            {
                "Joueur": [selected_player1] * len(player1_data) + [comparison_name] * len(player2_data),
                stat_type: player1_data + player2_data,
            }
        )

        fig = px.box(
            boxplot_data,
            x="Joueur",
            y=stat_type,
            color="Joueur",
            title=f"Distribution de {stat_type} par match",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Onglet 2: Suivi des Performances
    with tab3:
        st.markdown("<h2 class='sub-header'>Suivi des Performances dans le Temps</h2>", unsafe_allow_html=True)

        # Graphique en courbes pour suivre la progression
        st.subheader(f"Progression de {selected_player1} sur plusieurs matchs")
        stat_to_track = st.selectbox(
            "Sélectionner une statistique à suivre",
            options=["Buts", "Passes décisives", "Tirs", "Duels gagnés", "Interceptions"],
            index=0,
        )

        # Extraire les données réelles pour la progression
        def extract_progression_data(player_name, matches, stat_type):
            data = []
            match_dates = []
            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                player_events = events[events["player"] == player_name]

                if stat_type == "Buts":
                    data.append(player_events[
                    (player_events["type"] == "Shot") & 
                    (player_events["shot_outcome"] == "Goal")
                ].shape[0])
                elif stat_type == "Passes décisives":
                    data.append(player_events[player_events["type"] == "Assist"].shape[0])
                elif stat_type == "Tirs":
                    data.append(player_events[player_events["type"] == "Shot"].shape[0])
                elif stat_type == "Duels gagnés":
                    data.append(
                        player_events[
                            (player_events["type"] == "Duel") & (player_events["duel_outcome"] == "Won")
                        ].shape[0]
                    )
                elif stat_type == "Interceptions":
                    data.append(player_events[player_events["type"] == "Interception"].shape[0])

                match_dates.append(match["match_date"])

            return match_dates, data

        match_dates, stat_values = extract_progression_data(selected_player1, team_matches, stat_to_track)

        # Créer le dataframe pour le graphique en courbes
        progression_data = pd.DataFrame(
            {"Date": match_dates, "Match": [f"Match {i+1}" for i in range(len(match_dates))], stat_to_track: stat_values}
        )
        progression_data["Date"] = pd.to_datetime(progression_data["Date"])
        progression_data = progression_data.sort_values("Date")

        # Créer le graphique en courbes
        fig = px.line(
            progression_data,
            x="Date",
            y=stat_to_track,
            markers=True,
            title=f"Évolution de {stat_to_track} pour {selected_player1}",
        )

        # Ajouter des annotations pour les événements importants
        important_matches = progression_data[progression_data[stat_to_track] > 0]
        for _, match in important_matches.iterrows():
            fig.add_annotation(
                x=match["Date"],
                y=match[stat_to_track],
                text=f"{int(match[stat_to_track])} {stat_to_track.lower()}",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-30,
            )

        st.plotly_chart(fig, use_container_width=True)
     # Onglet 4: Analyse Contextuelle
    
    with tab4:
        st.markdown("<h2 class='sub-header'>Analyse Contextuelle</h2>", unsafe_allow_html=True)

        # Heatmap des zones d'action
        pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
        fig, ax = pitch.draw(figsize=(12, 8))

        # Extraire les positions des actions
        def extract_heatmap_data(player_name, matches):
            x_coords = []
            y_coords = []

            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                player_events = events[events["player"] == player_name]

                for _, event in player_events.iterrows():
                    if "location" in event and isinstance(event["location"], list):
                        x_coords.append(event["location"][0])
                        y_coords.append(event["location"][1])

            return x_coords, y_coords

        x_coords, y_coords = extract_heatmap_data(selected_player1, team_matches)
        pitch.kdeplot(x_coords, y_coords, ax=ax, cmap="YlOrRd", shade=True, levels=100)
        st.pyplot(fig)

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")


##################################


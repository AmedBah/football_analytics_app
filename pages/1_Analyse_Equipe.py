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
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='statsbombpy')

import logging
logging.basicConfig(level=logging.DEBUG)

# Ajouter le répertoire parent au chemin pour importer les fonctions utilitaires
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import (
    load_competitions,
    load_matches,
    load_teams,
    load_events,
    load_filtered_events,
)

# Configuration de la page
st.set_page_config(
    page_title="Analyse d'Équipe",
    page_icon="📊",
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
st.markdown("<h1 class='main-header'>📊 Analyse d'Équipe</h1>", unsafe_allow_html=True)

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

    # Sélection des équipes pour la comparaison
    selected_team1 = st.sidebar.selectbox(
        "Sélectionner la première équipe", options=teams, index=0
    )
    selected_team2 = st.sidebar.selectbox(
        "Sélectionner la deuxième équipe (pour comparaison)",
        options=teams,
        index=min(1, len(teams) - 1),
    )

    # Chargement des matchs
    matches = load_matches(competition_id, season_id)
    if matches.empty:
        st.error("Aucun match disponible pour cette compétition.")
        st.stop()

    # Filtrer les matchs pour les équipes sélectionnées
    team1_matches = matches[
        (matches["home_team"] == selected_team1) | (matches["away_team"] == selected_team1)
    ]
    team2_matches = matches[
        (matches["home_team"] == selected_team2) | (matches["away_team"] == selected_team2)
    ]

    # Onglets pour les différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Classement & Performance",
            "Comparaison d'Équipes",
            "Heatmaps & Zones d'Action",
            "Corrélations Statistiques",
        ]
    )

    # Onglet 1: Classement et Performance Globale
    with tab1:
        st.markdown("<h2 class='sub-header'>Classement et Performance Globale</h2>", unsafe_allow_html=True)

        # Créer un dataframe pour le classement
        def create_standings(matches):
            teams_data = {}
            for _, match in matches.iterrows():
                home_team = match["home_team"]
                away_team = match["away_team"]
                home_score = match["home_score"]
                away_score = match["away_score"]

                # Initialiser les équipes si elles n'existent pas encore
                if home_team not in teams_data:
                    teams_data[home_team] = {
                        "matches": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                        "points": 0,
                    }
                if away_team not in teams_data:
                    teams_data[away_team] = {
                        "matches": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                        "points": 0,
                    }

                # Mettre à jour les statistiques
                teams_data[home_team]["matches"] += 1
                teams_data[away_team]["matches"] += 1
                teams_data[home_team]["goals_for"] += home_score
                teams_data[home_team]["goals_against"] += away_score
                teams_data[away_team]["goals_for"] += away_score
                teams_data[away_team]["goals_against"] += home_score

                if home_score > away_score:  # Victoire à domicile
                    teams_data[home_team]["wins"] += 1
                    teams_data[home_team]["points"] += 3
                    teams_data[away_team]["losses"] += 1
                elif home_score < away_score:  # Victoire à l'extérieur
                    teams_data[away_team]["wins"] += 1
                    teams_data[away_team]["points"] += 3
                    teams_data[home_team]["losses"] += 1
                else:  # Match nul
                    teams_data[home_team]["draws"] += 1
                    teams_data[home_team]["points"] += 1
                    teams_data[away_team]["draws"] += 1
                    teams_data[away_team]["points"] += 1

            # Créer le dataframe
            standings = pd.DataFrame.from_dict(teams_data, orient="index")
            standings["team"] = standings.index
            standings["goal_difference"] = (
                standings["goals_for"] - standings["goals_against"]
            )
            standings = standings.sort_values(
                by=["points", "goal_difference", "goals_for"], ascending=False
            ).reset_index(drop=True)
            standings.index = standings.index + 1  # Commencer l'index à 1
            return standings

        standings = create_standings(matches)

        # Afficher le classement
        st.subheader("Classement de la compétition")
        st.dataframe(
            standings[
                [
                    "team",
                    "matches",
                    "wins",
                    "draws",
                    "losses",
                    "goals_for",
                    "goals_against",
                    "goal_difference",
                    "points",
                ]
            ]
        )

        # Statistiques de l'équipe sélectionnée
        st.subheader(f"Statistiques de {selected_team1}")
        team_stats = standings[standings["team"] == selected_team1].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Points", team_stats["points"])
        with col2:
            st.metric("Victoires", team_stats["wins"])
        with col3:
            st.metric("Nuls", team_stats["draws"])
        with col4:
            st.metric("Défaites", team_stats["losses"])

    # Onglet 2: Comparaison entre Équipes
    # Onglet 2: Comparaison entre Équipes
    with tab2:
        st.markdown("<h2 class='sub-header'>Comparaison entre Équipes</h2>", unsafe_allow_html=True)

        # Graphique radar pour comparer les équipes
        st.subheader("Graphique Radar: Comparaison des performances")

        # Catégories pour le graphique radar
        categories = [
            "Buts marqués",
            "Possession moyenne (%)",
            "Passes réussies",
            "Tirs cadrés",
            "Duels gagnés",
            "Interceptions",
        ]

        # Extraire les statistiques réelles pour chaque équipe
        def get_team_statistics(team_name, matches):
            goals = 0
            possession = []
            passes_completed = 0
            shots_on_target = 0
            duels_won = 0
            interceptions = 0

            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                team_events = events[events["team"] == team_name]

                # Calculer les statistiques
                goals += team_events[(team_events["type"] == "Shot") & (team_events["shot_outcome"] == "Goal")
                ].shape[0]

                possession.append(events["possession_team"].value_counts().get(team_name, 0))
                passes_completed += team_events[team_events["type"] == "Pass"].shape[0]
                shots_on_target += team_events[
                    (team_events["type"] == "Shot") & (team_events["shot_outcome"] == "Goal")
                ].shape[0]
                duels_won += team_events[
                    (team_events["type"] == "Duel") & (team_events["duel_outcome"] == "Won")
                ].shape[0]
                interceptions += team_events[team_events["type"] == "Interception"].shape[0]

            avg_possession = np.mean(possession) if possession else 0
            return [
                goals,
                avg_possession,
                passes_completed,
                shots_on_target,
                duels_won,
                interceptions,
            ]

        # Obtenir les valeurs pour les deux équipes
        team1_values = get_team_statistics(selected_team1, team1_matches)
        team2_values = get_team_statistics(selected_team2, team2_matches)

        # Normaliser les valeurs pour le graphique radar
        max_values = [max(team1_values[i], team2_values[i]) for i in range(len(categories))]
        if any(max_val == 0 for max_val in max_values):
            st.warning("Certaines catégories ont des valeurs nulles. Elles seront ignorées dans le graphique radar.")
            max_values = [max_val if max_val != 0 else 1 for max_val in max_values]

        team1_values_norm = [team1_values[i] / max_values[i] for i in range(len(categories))]
        team2_values_norm = [team2_values[i] / max_values[i] for i in range(len(categories))]

        # Créer le graphique radar
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=team1_values_norm,
                theta=categories,
                fill="toself",
                name=selected_team1,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=team2_values_norm,
                theta=categories,
                fill="toself",
                name=selected_team2,
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

        # Boîte à moustaches pour comparer les statistiques
        st.subheader("Boîte à moustaches: Analyse de la distribution des statistiques")
        # Sélectionner une statistique pour la boîte à moustaches
        stat_type = st.selectbox(
            "Sélectionner une statistique",
            options=["Buts", "Tirs", "Passes", "Possession"],
            index=0,
        )

        # Extraire les données réelles pour la boîte à moustaches
        def extract_boxplot_data(team_name, matches, stat_type):
            data = []
            for _, match in matches.iterrows():
                match_id = match["match_id"]
                events = load_events(match_id)
                team_events = events[events["team"] == team_name]

                if stat_type == "Buts":
                    data.append(team_events[
                        (team_events["type"] == "Shot") & (team_events["shot_outcome"] == "Goal")
                    ].shape[0])

                elif stat_type == "Tirs":
                    data.append(team_events[team_events["type"] == "Shot"].shape[0])
                elif stat_type == "Passes":
                    data.append(team_events[team_events["type"] == "Pass"].shape[0])
                elif stat_type == "Possession":
                    possession_percentage = (
                        events["possession_team"].value_counts().get(team_name, 0)
                    )
                    data.append(possession_percentage)
            return data

        # Extraire les données pour les deux équipes
        team1_data = extract_boxplot_data(selected_team1, team1_matches, stat_type)
        team2_data = extract_boxplot_data(selected_team2, team2_matches, stat_type)

        # Vérifier si les données sont valides
        if not team1_data and not team2_data:
            st.warning(f"Aucune donnée disponible pour {stat_type}.")
        else:
            # Créer le dataframe pour la boîte à moustaches
            boxplot_data = pd.DataFrame(
                {
                    "Équipe": [selected_team1] * len(team1_data) + [selected_team2] * len(team2_data),
                    stat_type: team1_data + team2_data,
                }
            )

            # Créer le graphique de boîte à moustaches
            fig = px.box(
                boxplot_data,
                x="Équipe",
                y=stat_type,
                color="Équipe",
                title=f"Distribution de {stat_type} par match",
            )
            st.plotly_chart(fig, use_container_width=True)
    # Onglet 3: Heatmaps et Zones d'Action
    with tab3:
        st.markdown("<h2 class='sub-header'>Heatmaps et Zones d'Action</h2>", unsafe_allow_html=True)
        st.info(
            "Cette section utilise les données d'événements de StatsBomb pour générer des heatmaps montrant les zones d'action de l'équipe."
        )

        # Sélection du match pour la heatmap
        team1_match_options = team1_matches[
            ["match_id", "home_team", "away_team", "match_date"]
        ]
        team1_match_options["display_name"] = (
            team1_match_options["match_date"].astype(str)
            + ": "
            + team1_match_options["home_team"]
            + " vs "
            + team1_match_options["away_team"]
        )
        selected_match_display = st.selectbox(
            "Sélectionner un match pour visualiser les zones d'action",
            options=team1_match_options["display_name"].tolist(),
            index=0,
        )
        selected_match_id = team1_match_options[
            team1_match_options["display_name"] == selected_match_display
        ]["match_id"].values[0]

        # Type d'événement pour la heatmap
        event_type = st.selectbox(
            "Sélectionner un type d'événement",
            options=["Passes", "Tirs", "Récupérations", "Pertes de balle"],
            index=0,
        )

        # Charger les événements filtrés
        events = load_filtered_events(selected_match_id, team_name=selected_team1)

        # Filtre spécifique sur le type d'événement
        if event_type == "Passes":
            filtered_events = events[events["type"] == "Pass"]
        elif event_type == "Tirs":
            filtered_events = events[events["type"] == "Shot"]
        elif event_type == "Récupérations":
            filtered_events = events[events["type"] == "Ball Recovery"]
        elif event_type == "Pertes de balle":
            filtered_events = events[events["type"] == "Miscontrol"]

        # Créer une heatmap avec mpl_soccer
        pitch = Pitch(pitch_type="statsbomb", line_zorder=2, pitch_color="#22312b", line_color="#efefef")
        fig, ax = pitch.draw(figsize=(12, 8))

        # Extraire les coordonnées des événements
        x_coords = filtered_events["location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None).dropna()
        y_coords = filtered_events["location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None).dropna()

        # Dessiner la heatmap
        if not x_coords.empty and not y_coords.empty:
            pitch.kdeplot(
                x=x_coords,
                y=y_coords,
                ax=ax,
                cmap="hot",
                fill=True,
                levels=100,
                alpha=0.7,
            )
            pitch.scatter(x=x_coords, y=y_coords, ax=ax, s=50, color="white", edgecolors="black", zorder=3)

        st.pyplot(fig)

    # Onglet 4: Corrélations Statistiques
    with tab4:
        st.markdown("<h2 class='sub-header'>Corrélations Statistiques</h2>", unsafe_allow_html=True)
        st.info("Cette section analyse les corrélations entre différentes statistiques pour identifier les facteurs clés de performance.")

        # Sélection des variables pour le diagramme de dispersion
        col1, col2 = st.columns(2)
        with col1:
            x_variable = st.selectbox(
                "Variable X",
                options=["Possession (%)", "Passes réussies", "Tirs", "Centres", "Duels gagnés"],
                index=0,
            )
        with col2:
            y_variable = st.selectbox(
                "Variable Y",
                options=["Buts marqués", "Tirs cadrés", "Occasions créées", "xG (Expected Goals)", "Points"],
                index=0,
            )

        # Extraire les données réelles pour toutes les équipes
        def extract_correlation_data(matches, x_var, y_var):
            data = []
            for team in teams:
                team_matches = matches[
                    (matches["home_team"] == team) | (matches["away_team"] == team)
                ]
                x_value = 0
                y_value = 0

                for _, match in team_matches.iterrows():
                    match_id = match["match_id"]
                    events = load_events(match_id)
                    team_events = events[events["team"] == team]

                    if x_var == "Possession (%)":
                        x_value += events["possession_team"].value_counts().get(team, 0)
                    elif x_var == "Passes réussies":
                        x_value += team_events[team_events["type"] == "Pass"].shape[0]
                    elif x_var == "Tirs":
                        x_value += team_events[team_events["type"] == "Shot"].shape[0]
                    elif x_var == "Centres":
                        x_value += team_events[team_events["type"] == "Cross"].shape[0]
                    elif x_var == "Duels gagnés":
                        x_value += team_events[
                            (team_events["type"] == "Duel")
                            & (team_events["duel_outcome"] == "Won")
                        ].shape[0]

                    if y_var == "Buts marqués":
                        y_value += team_events[
                            (team_events["type"] == "Shot") & 
                            (team_events["shot_outcome"] == "Goal")
                        ].shape[0]

                    elif y_var == "Tirs cadrés":
                        y_value += team_events[
                            (team_events["type"] == "Shot")
                            & (team_events["shot_outcome"] == "Goal")
                        ].shape[0]
                    elif y_var == "Occasions créées":
                        y_value += team_events[team_events["type"] == "Shot"].shape[0]
                    elif y_var == "xG (Expected Goals)":
                        y_value += team_events["shot_statsbomb_xg"].sum()
                    elif y_var == "Points":
                        points = 0
                        if match["home_team"] == team:
                            points += 3 if match["home_score"] > match["away_score"] else 1 if match["home_score"] == match["away_score"] else 0
                        else:
                            points += 3 if match["away_score"] > match["home_score"] else 1 if match["away_score"] == match["home_score"] else 0
                        y_value += points

                data.append({"Équipe": team, x_var: x_value, y_var: y_value})

            return pd.DataFrame(data)

        correlation_data = extract_correlation_data(matches, x_variable, y_variable)

        # Créer le diagramme de dispersion
        fig = px.scatter(
            correlation_data,
            x=x_variable,
            y=y_variable,
            text="Équipe",
            title=f"Relation entre {x_variable} et {y_variable}",
            trendline="ols",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Calcul et affichage de la corrélation
        x_data = correlation_data[x_variable]
        y_data = correlation_data[y_variable]
        if np.std(x_data) == 0 or np.std(y_data) == 0:
            st.warning("La corrélation ne peut pas être calculée en raison de données insuffisantes ou constantes.")
            correlation_value = 0
        else:
            correlation_value = np.corrcoef(x_data, y_data)[0, 1]

        st.markdown(
            f"""
            <div class='card'>
                <h3>Analyse de la Corrélation</h3>
                <p>Coefficient de corrélation: <strong>{correlation_value:.2f}</strong></p>
                <p>Interprétation:</p>
                <ul>
                    <li>Une valeur proche de 1 indique une forte corrélation positive</li>
                    <li>Une valeur proche de -1 indique une forte corrélation négative</li>
                    <li>Une valeur proche de 0 indique une faible corrélation</li>
                </ul>
                <p>Cette analyse vous permet d'identifier les facteurs statistiques qui ont le plus d'impact sur les performances de votre équipe.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")
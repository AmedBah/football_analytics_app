import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from statsbombpy import sb
import sys
import os

# Ajouter le répertoire parent au chemin pour importer les fonctions utilitaires
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_competitions, load_matches, load_teams, load_events

# Configuration de la page
st.set_page_config(
    page_title="Analyse d'Équipe",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Titre de la page
st.markdown("<h1 class='main-header'>📊 Analyse d'Équipe</h1>", unsafe_allow_html=True)

# Barre latérale pour les filtres
st.sidebar.header("Filtres")

# Chargement des compétitions
try:
    competitions = load_competitions()
    
    # Sélection de la compétition
    competition_options = competitions[['competition_id', 'competition_name', 'season_id', 'season_name']].drop_duplicates()
    competition_options['display_name'] = competition_options['competition_name'] + ' - ' + competition_options['season_name']
    
    selected_competition = st.sidebar.selectbox(
        "Sélectionner une compétition",
        options=competition_options['display_name'].tolist(),
        index=0
    )
    
    # Récupérer les IDs de la compétition et de la saison sélectionnées
    selected_comp_data = competition_options[competition_options['display_name'] == selected_competition]
    competition_id = selected_comp_data['competition_id'].values[0]
    season_id = selected_comp_data['season_id'].values[0]
    
    # Chargement des équipes
    teams = load_teams(competition_id, season_id)
    
    # Sélection des équipes pour la comparaison
    selected_team1 = st.sidebar.selectbox(
        "Sélectionner la première équipe",
        options=teams,
        index=0
    )
    
    selected_team2 = st.sidebar.selectbox(
        "Sélectionner la deuxième équipe (pour comparaison)",
        options=teams,
        index=min(1, len(teams)-1)
    )
    
    # Chargement des matchs
    matches = load_matches(competition_id, season_id)
    
    # Filtrer les matchs pour les équipes sélectionnées
    team1_matches = matches[(matches['home_team'] == selected_team1) | (matches['away_team'] == selected_team1)]
    team2_matches = matches[(matches['home_team'] == selected_team2) | (matches['away_team'] == selected_team2)]
    
    # Onglets pour les différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Classement & Performance", 
        "Comparaison d'Équipes", 
        "Heatmaps & Zones d'Action", 
        "Corrélations Statistiques"
    ])
    
    # Onglet 1: Classement et Performance Globale
    with tab1:
        st.markdown("<h2 class='sub-header'>Classement et Performance Globale</h2>", unsafe_allow_html=True)
        
        # Créer un dataframe pour le classement
        def create_standings(matches):
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
        
        standings = create_standings(matches)
        
        # Afficher le classement
        st.subheader("Classement de la compétition")
        st.dataframe(standings[['team', 'matches', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference', 'points']])
        
        # Statistiques de l'équipe sélectionnée
        st.subheader(f"Statistiques de {selected_team1}")
        
        team_stats = standings[standings['team'] == selected_team1].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Points", team_stats['points'])
        with col2:
            st.metric("Victoires", team_stats['wins'])
        with col3:
            st.metric("Nuls", team_stats['draws'])
        with col4:
            st.metric("Défaites", team_stats['losses'])
        
        # Graphique d'évolution des points
        st.subheader("Évolution des points au fil des matchs")
        
        # Simuler l'évolution des points (données fictives pour l'exemple)
        match_numbers = list(range(1, team_stats['matches'] + 1))
        points_evolution = np.cumsum(np.random.choice([0, 1, 3], size=team_stats['matches'], p=[0.2, 0.3, 0.5]))
        
        fig = px.line(
            x=match_numbers, 
            y=points_evolution,
            labels={"x": "Match", "y": "Points cumulés"},
            title=f"Évolution des points de {selected_team1}"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Onglet 2: Comparaison entre Équipes
    with tab2:
        st.markdown("<h2 class='sub-header'>Comparaison entre Équipes</h2>", unsafe_allow_html=True)
        
        # Graphique radar pour comparer les équipes
        st.subheader("Graphique Radar: Comparaison des performances")
        
        # Créer des données pour le graphique radar (données fictives pour l'exemple)
        categories = ['Buts marqués', 'Possession', 'Passes réussies', 'Tirs cadrés', 'Duels gagnés', 'Interceptions']
        
        team1_values = [
            standings[standings['team'] == selected_team1]['goals_for'].values[0],
            np.random.randint(40, 70),  # Possession
            np.random.randint(300, 600),  # Passes réussies
            np.random.randint(30, 100),  # Tirs cadrés
            np.random.randint(100, 200),  # Duels gagnés
            np.random.randint(50, 150)   # Interceptions
        ]
        
        team2_values = [
            standings[standings['team'] == selected_team2]['goals_for'].values[0],
            np.random.randint(40, 70),  # Possession
            np.random.randint(300, 600),  # Passes réussies
            np.random.randint(30, 100),  # Tirs cadrés
            np.random.randint(100, 200),  # Duels gagnés
            np.random.randint(50, 150)   # Interceptions
        ]
        
        # Normaliser les valeurs pour le graphique radar
        max_values = [max(team1_values[i], team2_values[i]) for i in range(len(categories))]
        team1_values_norm = [team1_values[i]/max_values[i] for i in range(len(categories))]
        team2_values_norm = [team2_values[i]/max_values[i] for i in range(len(categories))]
        
        # Créer le graphique radar
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=team1_values_norm,
            theta=categories,
            fill='toself',
            name=selected_team1
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=team2_values_norm,
            theta=categories,
            fill='toself',
            name=selected_team2
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Boîte à moustaches pour comparer les statistiques
        st.subheader("Boîte à moustaches: Analyse de la distribution des statistiques")
        
        # Créer des données pour la boîte à moustaches (données fictives pour l'exemple)
        stat_type = st.selectbox(
            "Sélectionner une statistique",
            options=["Buts", "Tirs", "Passes", "Possession"],
            index=0
        )
        
        # Générer des données fictives pour les boîtes à moustaches
        team1_data = np.random.normal(3, 1, 20) if stat_type == "Buts" else (
            np.random.normal(15, 5, 20) if stat_type == "Tirs" else (
                np.random.normal(500, 100, 20) if stat_type == "Passes" else
                np.random.normal(55, 10, 20)
            )
        )
        
        team2_data = np.random.normal(2.5, 1.2, 20) if stat_type == "Buts" else (
            np.random.normal(12, 4, 20) if stat_type == "Tirs" else (
                np.random.normal(450, 120, 20) if stat_type == "Passes" else
                np.random.normal(50, 12, 20)
            )
        )
        
        # Créer le dataframe pour la boîte à moustaches
        boxplot_data = pd.DataFrame({
            'Équipe': [selected_team1] * len(team1_data) + [selected_team2] * len(team2_data),
            stat_type: np.concatenate([team1_data, team2_data])
        })
        
        fig = px.box(
            boxplot_data, 
            x='Équipe', 
            y=stat_type,
            color='Équipe',
            title=f"Distribution de {stat_type} par match"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Onglet 3: Heatmaps et Zones d'Action
    with tab3:
        st.markdown("<h2 class='sub-header'>Heatmaps et Zones d'Action</h2>", unsafe_allow_html=True)
        
        st.info("Cette section utilise les données d'événements de StatsBomb pour générer des heatmaps montrant les zones d'action de l'équipe.")
        
        # Sélection du match pour la heatmap
        team1_match_options = team1_matches[['match_id', 'home_team', 'away_team', 'match_date']]
        team1_match_options['display_name'] = team1_match_options['match_date'].astype(str) + ': ' + team1_match_options['home_team'] + ' vs ' + team1_match_options['away_team']
        
        selected_match_display = st.selectbox(
            "Sélectionner un match pour visualiser les zones d'action",
            options=team1_match_options['display_name'].tolist(),
            index=0
        )
        
        selected_match_id = team1_match_options[team1_match_options['display_name'] == selected_match_display]['match_id'].values[0]
        
        # Type d'événement pour la heatmap
        event_type = st.selectbox(
            "Sélectionner un type d'événement",
            options=["Passes", "Tirs", "Récupérations", "Pertes de balle"],
            index=0
        )
        
        # Créer une heatmap fictive (à remplacer par des données réelles)
        st.subheader(f"Heatmap des {event_type} pour {selected_team1}")
        
        # Créer un terrain de football
        pitch_length = 120
        pitch_width = 80
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Dessiner le terrain
        # Rectangle principal
        ax.plot([0, 0, pitch_length, pitch_length, 0], [0, pitch_width, pitch_width, 0, 0], color='black')
        
        # Ligne médiane
        ax.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color='black')
        
        # Cercle central
        central_circle = plt.Circle((pitch_length/2, pitch_width/2), 9.15, fill=False, color='black')
        ax.add_artist(central_circle)
        
        # Surfaces de réparation
        # Gauche
        ax.plot([0, 16.5, 16.5, 0], [pitch_width/2 - 20.15, pitch_width/2 - 20.15, pitch_width/2 + 20.15, pitch_width/2 + 20.15], color='black')
        # Droite
        ax.plot([pitch_length, pitch_length - 16.5, pitch_length - 16.5, pitch_length], [pitch_width/2 - 20.15, pitch_width/2 - 20.15, pitch_width/2 + 20.15, pitch_width/2 + 20.15], color='black')
        
        # Surfaces de but
        # Gauche
        ax.plot([0, 5.5, 5.5, 0], [pitch_width/2 - 9.16, pitch_width/2 - 9.16, pitch_width/2 + 9.16, pitch_width/2 + 9.16], color='black')
        # Droite
        ax.plot([pitch_length, pitch_length - 5.5, pitch_length - 5.5, pitch_length], [pitch_width/2 - 9.16, pitch_width/2 - 9.16, pitch_width/2 + 9.16, pitch_width/2 + 9.16], color='black')
        
        # Points de penalty
        ax.plot(11, pitch_width/2, marker='o', markersize=2, color='black')
        ax.plot(pitch_length - 11, pitch_width/2, marker='o', markersize=2, color='black')
        
        # Générer des données fictives pour la heatmap
        x = np.random.normal(pitch_length/2, pitch_length/4, 500)
        y = np.random.normal(pitch_width/2, pitch_width/4, 500)
        
        # Créer la heatmap
        heatmap = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', alpha=0.7)
        plt.colorbar(heatmap, ax=ax, label='Densité')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Heatmap des {event_type} - {selected_team1}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher la heatmap
        st.pyplot(fig)
        
        # Explication de la heatmap
        st.markdown("""
        <div class='card'>
            <h3>Interprétation de la Heatmap</h3>
            <p>Cette heatmap montre les zones du terrain où l'équipe a été la plus active pour le type d'événement sélectionné. 
            Les zones en rouge indiquent une forte concentration d'actions, tandis que les zones en jaune indiquent une concentration plus faible.</p>
            <p>Utilisez cette visualisation pour identifier les zones préférentielles d'action de l'équipe et adapter votre stratégie en conséquence.</p>
        </div>
        """, unsafe_allow_html=True)
    
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
                index=0
            )
        
        with col2:
            y_variable = st.selectbox(
                "Variable Y",
                options=["Buts marqués", "Tirs cadrés", "Occasions créées", "xG (Expected Goals)", "Points"],
                index=0
            )
        
        # Créer des données fictives pour le diagramme de dispersion
        np.random.seed(42)  # Pour la reproductibilité
        
        # Générer des données avec une corrélation
        n_teams = 20
        
        if x_variable == "Possession (%)":
            x_data = np.random.normal(50, 10, n_teams)
            x_data = np.clip(x_data, 30, 70)  # Limiter entre 30% et 70%
        elif x_variable == "Passes réussies":
            x_data = np.random.normal(450, 100, n_teams)
        elif x_variable == "Tirs":
            x_data = np.random.normal(12, 3, n_teams)
        elif x_variable == "Centres":
            x_data = np.random.normal(20, 5, n_teams)
        else:  # Duels gagnés
            x_data = np.random.normal(50, 10, n_teams)
        
        # Ajouter une corrélation avec la variable Y
        correlation = 0.7  # Corrélation positive
        noise = np.random.normal(0, 1, n_teams)
        
        if y_variable == "Buts marqués":
            y_data = 1.5 + 0.05 * x_data + noise
            y_data = np.round(np.clip(y_data, 0, 5))
        elif y_variable == "Tirs cadrés":
            y_data = 3 + 0.1 * x_data + noise * 2
            y_data = np.round(np.clip(y_data, 0, 10))
        elif y_variable == "Occasions créées":
            y_data = 2 + 0.08 * x_data + noise * 3
            y_data = np.round(np.clip(y_data, 0, 15))
        elif y_variable == "xG (Expected Goals)":
            y_data = 1 + 0.03 * x_data + noise * 0.5
            y_data = np.round(y_data * 10) / 10  # Arrondir à 1 décimale
        else:  # Points
            y_data = 0.5 + 0.06 * x_data + noise * 2
            y_data = np.round(np.clip(y_data, 0, 3))
        
        # Créer un dataframe pour le diagramme de dispersion
        scatter_data = pd.DataFrame({
            'Équipe': [f"Équipe {i+1}" for i in range(n_teams)],
            x_variable: x_data,
            y_variable: y_data
        })
        
        # Marquer les équipes sélectionnées
        team_colors = ['#1E88E5' if team == selected_team1 else 
                       '#FFC107' if team == selected_team2 else 
                       '#CCCCCC' for team in scatter_data['Équipe']]
        
        # Créer le diagramme de dispersion
        fig = px.scatter(
            scatter_data,
            x=x_variable,
            y=y_variable,
            text='Équipe',
            title=f"Relation entre {x_variable} et {y_variable}",
            trendline="ols"  # Ajouter une ligne de tendance
        )
        
        # Mettre à jour les couleurs des points
        fig.update_traces(marker=dict(color=team_colors, size=12), selector=dict(mode='markers+text'))
        
        # Afficher le diagramme
        st.plotly_chart(fig, use_container_width=True)
        
        # Calcul et affichage de la corrélation
        correlation_value = np.corrcoef(x_data, y_data)[0, 1]
        
        st.markdown(f"""
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
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

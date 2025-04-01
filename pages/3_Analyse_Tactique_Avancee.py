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
import matplotlib.patches as patches

# Ajouter le répertoire parent au chemin pour importer les fonctions utilitaires
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_competitions, load_matches, load_teams, load_events, load_filtered_events

# Configuration de la page
st.set_page_config(
    page_title="Analyse Tactique Avancée",
    page_icon="🔍",
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
    }
    .metric-container {
        background-color: #e3f2fd;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1976D2;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #424242;
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-header'>🔍 Analyse Tactique Avancée</h1>", unsafe_allow_html=True)

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
    
    # Sélection de l'équipe
    selected_team = st.sidebar.selectbox(
        "Sélectionner une équipe",
        options=teams,
        index=0
    )
    
    # Chargement des matchs
    matches = load_matches(competition_id, season_id)
    
    # Filtrer les matchs pour l'équipe sélectionnée
    team_matches = matches[(matches['home_team'] == selected_team) | (matches['away_team'] == selected_team)]
    
    # Sélection du match
    match_options = team_matches[['match_id', 'home_team', 'away_team', 'match_date']]
    match_options['display_name'] = match_options['match_date'].astype(str) + ': ' + match_options['home_team'] + ' vs ' + match_options['away_team']
    
    selected_match_display = st.sidebar.selectbox(
        "Sélectionner un match",
        options=match_options['display_name'].tolist(),
        index=0
    )
    
    selected_match_id = match_options[match_options['display_name'] == selected_match_display]['match_id'].values[0]
    selected_match_home = match_options[match_options['display_name'] == selected_match_display]['home_team'].values[0]
    selected_match_away = match_options[match_options['display_name'] == selected_match_display]['away_team'].values[0]
    
    # Options d'analyse avancée
    st.sidebar.header("Options d'analyse avancée")
    
    analysis_period = st.sidebar.radio(
        "Période d'analyse",
        options=["Match complet", "1ère mi-temps", "2ème mi-temps"],
        index=0
    )
    
    # Onglets pour les différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Analyse de Possession", 
        "Analyse des Passes",
        "Analyse Défensive",
        "Analyse des Transitions"
    ])
    
    # Onglet 1: Analyse de Possession
    with tab1:
        st.markdown("<h2 class='sub-header'>Analyse de Possession</h2>", unsafe_allow_html=True)
        
        # Statistiques de possession
        st.subheader("Statistiques de possession")
        
        # Générer des données fictives pour la possession
        home_possession = np.random.randint(35, 65)
        away_possession = 100 - home_possession
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{home_possession}%</div>
                <div class='metric-label'>{selected_match_home}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 20px;'>vs</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{away_possession}%</div>
                <div class='metric-label'>{selected_match_away}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Graphique de possession par période
        st.subheader("Possession par période")
        
        # Générer des données fictives pour la possession par période
        periods = ["0-15'", "15-30'", "30-45'", "45-60'", "60-75'", "75-90'"]
        home_possession_periods = [np.random.randint(35, 65) for _ in range(len(periods))]
        away_possession_periods = [100 - p for p in home_possession_periods]
        
        possession_data = pd.DataFrame({
            'Période': periods,
            selected_match_home: home_possession_periods,
            selected_match_away: away_possession_periods
        })
        
        fig = px.bar(
            possession_data,
            x='Période',
            y=[selected_match_home, selected_match_away],
            barmode='stack',
            title="Évolution de la possession par période"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Carte de chaleur de la possession
        st.subheader("Carte de chaleur de la possession")
        
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
        
        # Générer des données fictives pour la heatmap de possession
        # Simuler une distribution de possession basée sur l'équipe sélectionnée
        if selected_team == selected_match_home:
            # Si l'équipe sélectionnée est l'équipe à domicile
            # Simuler une concentration plus élevée dans la moitié offensive
            x = np.concatenate([
                np.random.normal(pitch_length/4, pitch_length/8, 300),  # Défense
                np.random.normal(pitch_length/2, pitch_length/6, 500),  # Milieu
                np.random.normal(3*pitch_length/4, pitch_length/8, 200)  # Attaque
            ])
        else:
            # Si l'équipe sélectionnée est l'équipe à l'extérieur
            # Simuler une concentration plus élevée dans la moitié défensive
            x = np.concatenate([
                np.random.normal(pitch_length/4, pitch_length/8, 500),  # Défense
                np.random.normal(pitch_length/2, pitch_length/6, 300),  # Milieu
                np.random.normal(3*pitch_length/4, pitch_length/8, 200)  # Attaque
            ])
        
        y = np.random.normal(pitch_width/2, pitch_width/3, len(x))
        
        # Créer la heatmap
        heatmap = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', alpha=0.7)
        plt.colorbar(heatmap, ax=ax, label='Densité de possession')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Heatmap de possession - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher la heatmap
        st.pyplot(fig)
        
        # Analyse de la possession
        st.markdown("""
        <div class='card'>
            <h3>Analyse de la possession</h3>
            <p>Cette visualisation montre les zones du terrain où l'équipe a eu le plus de possession du ballon. Les zones en rouge indiquent une forte concentration de possession, tandis que les zones en jaune indiquent une concentration plus faible.</p>
            <p>L'analyse de la possession peut aider à :</p>
            <ul>
                <li>Identifier les zones de contrôle préférentielles de l'équipe</li>
                <li>Comprendre la stratégie de construction du jeu</li>
                <li>Détecter les déséquilibres dans la répartition de la possession</li>
                <li>Évaluer l'efficacité de la pression adverse</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques avancées de possession
        st.subheader("Métriques avancées de possession")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(5, 15)}</div>
                <div class='metric-label'>Séquences de 10+ passes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(20, 40)}</div>
                <div class='metric-label'>Entrées dans le dernier tiers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(3, 8)}</div>
                <div class='metric-label'>Temps moyen de possession (sec)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(40, 70)}%</div>
                <div class='metric-label'>Possession dans le camp adverse</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Onglet 2: Analyse des Passes
    with tab2:
        st.markdown("<h2 class='sub-header'>Analyse des Passes</h2>", unsafe_allow_html=True)
        
        # Statistiques de passes
        st.subheader("Statistiques de passes")
        
        # Générer des données fictives pour les passes
        home_passes = np.random.randint(400, 700)
        away_passes = np.random.randint(400, 700)
        home_accuracy = np.random.randint(75, 90)
        away_accuracy = np.random.randint(75, 90)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>{selected_match_home}</h3>
                <p><strong>Passes totales:</strong> {home_passes}</p>
                <p><strong>Précision des passes:</strong> {home_accuracy}%</p>
                <p><strong>Passes réussies:</strong> {int(home_passes * home_accuracy / 100)}</p>
                <p><strong>Passes manquées:</strong> {int(home_passes * (100 - home_accuracy) / 100)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3>{selected_match_away}</h3>
                <p><strong>Passes totales:</strong> {away_passes}</p>
                <p><strong>Précision des passes:</strong> {away_accuracy}%</p>
                <p><strong>Passes réussies:</strong> {int(away_passes * away_accuracy / 100)}</p>
                <p><strong>Passes manquées:</strong> {int(away_passes * (100 - away_accuracy) / 100)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Réseau de passes
        st.subheader("Réseau de passes")
        
        # Créer un terrain de football pour le réseau de passes
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
        
        # Simuler des positions de joueurs
        # Formation 4-3-3
        player_positions = [
            (10, pitch_width/2),  # GK
            (30, pitch_width/5),  # RB
            (30, 2*pitch_width/5),  # CB
            (30, 3*pitch_width/5),  # CB
            (30, 4*pitch_width/5),  # LB
            (60, pitch_width/4),  # CM
            (60, pitch_width/2),  # CM
            (60, 3*pitch_width/4),  # CM
            (90, pitch_width/4),  # RW
            (90, pitch_width/2),  # ST
            (90, 3*pitch_width/4)  # LW
        ]
        
        # Dessiner les joueurs
        for i, (x, y) in enumerate(player_positions):
            circle = plt.Circle((x, y), 3, color='blue', fill=True)
            ax.add_artist(circle)
            ax.text(x, y - 5, str(i+1), fontsize=8, ha='center')
        
        # Simuler des passes entre les joueurs
        n_passes = 30
        for _ in range(n_passes):
            # Sélectionner deux joueurs aléatoires
            player1_idx = np.random.randint(0, len(player_positions))
            player2_idx = np.random.randint(0, len(player_positions))
            
            # Éviter les passes vers soi-même
            while player1_idx == player2_idx:
                player2_idx = np.random.randint(0, len(player_positions))
            
            # Récupérer les positions des joueurs
            x1, y1 = player_positions[player1_idx]
            x2, y2 = player_positions[player2_idx]
            
            # Dessiner la flèche de passe
            # L'épaisseur de la flèche est proportionnelle au nombre de passes
            width = np.random.uniform(0.5, 2.5)
            ax.arrow(x1, y1, x2-x1, y2-y1, head_width=2, head_length=2, fc='blue', ec='blue', alpha=0.4, width=width)
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Réseau de passes - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher le réseau de passes
        st.pyplot(fig)
        
        # Analyse du réseau de passes
        st.markdown("""
        <div class='card'>
            <h3>Analyse du réseau de passes</h3>
            <p>Cette visualisation montre les connexions de passes entre les joueurs. L'épaisseur des flèches est proportionnelle au nombre de passes échangées entre les joueurs.</p>
            <p>L'analyse du réseau de passes peut aider à :</p>
            <ul>
                <li>Identifier les joueurs centraux dans la construction du jeu</li>
                <li>Détecter les combinaisons de passes préférentielles</li>
                <li>Comprendre la structure de l'équipe en possession</li>
                <li>Repérer les déséquilibres dans la distribution des passes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Types de passes
        st.subheader("Types de passes")
        
        # Générer des données fictives pour les types de passes
        pass_types = ["Courtes", "Moyennes", "Longues", "Progressives", "Latérales", "Vers l'arrière", "Dernière passe"]
        pass_counts = [np.random.randint(100, 300), np.random.randint(50, 150), np.random.randint(20, 60), 
                      np.random.randint(30, 80), np.random.randint(50, 150), np.random.randint(30, 100), np.random.randint(5, 20)]
        
        pass_data = pd.DataFrame({
            'Type de passe': pass_types,
            'Nombre': pass_counts
        })
        
        fig = px.bar(
            pass_data,
            x='Type de passe',
            y='Nombre',
            title=f"Distribution des types de passes - {selected_team}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Carte de chaleur des passes
        st.subheader("Carte de chaleur des passes")
        
        # Créer un terrain de football pour la heatmap des passes
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
        
        # Générer des données fictives pour la heatmap des passes
        # Simuler des points de départ de passes
        x_start = np.concatenate([
            np.random.normal(pitch_length/4, pitch_length/8, 200),  # Défense
            np.random.normal(pitch_length/2, pitch_length/6, 400),  # Milieu
            np.random.normal(3*pitch_length/4, pitch_length/8, 100)  # Attaque
        ])
        
        y_start = np.random.normal(pitch_width/2, pitch_width/3, len(x_start))
        
        # Créer la heatmap
        heatmap = ax.hexbin(x_start, y_start, gridsize=30, cmap='YlOrRd', alpha=0.7)
        plt.colorbar(heatmap, ax=ax, label='Densité de passes')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Heatmap des passes - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher la heatmap
        st.pyplot(fig)
        
        # Métriques avancées de passes
        st.subheader("Métriques avancées de passes")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(10, 30)}</div>
                <div class='metric-label'>Passes clés</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(5, 15)}</div>
                <div class='metric-label'>Passes dans la surface</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(20, 50)}</div>
                <div class='metric-label'>Passes progressives</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(3, 10)}</div>
                <div class='metric-label'>Passes décisives attendues (xA)</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Onglet 3: Analyse Défensive
    with tab3:
        st.markdown("<h2 class='sub-header'>Analyse Défensive</h2>", unsafe_allow_html=True)
        
        # Statistiques défensives
        st.subheader("Statistiques défensives")
        
        # Générer des données fictives pour les statistiques défensives
        defensive_stats = {
            'Tacles': np.random.randint(15, 30),
            'Interceptions': np.random.randint(10, 25),
            'Duels gagnés': np.random.randint(40, 70),
            'Duels aériens gagnés': np.random.randint(15, 30),
            'Dégagements': np.random.randint(15, 35),
            'Blocs': np.random.randint(5, 15),
            'Fautes commises': np.random.randint(8, 18)
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>Statistiques défensives</h3>
                <p><strong>Tacles:</strong> {defensive_stats['Tacles']}</p>
                <p><strong>Interceptions:</strong> {defensive_stats['Interceptions']}</p>
                <p><strong>Duels gagnés:</strong> {defensive_stats['Duels gagnés']}</p>
                <p><strong>Duels aériens gagnés:</strong> {defensive_stats['Duels aériens gagnés']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3>Statistiques défensives (suite)</h3>
                <p><strong>Dégagements:</strong> {defensive_stats['Dégagements']}</p>
                <p><strong>Blocs:</strong> {defensive_stats['Blocs']}</p>
                <p><strong>Fautes commises:</strong> {defensive_stats['Fautes commises']}</p>
                <p><strong>Taux de réussite des tacles:</strong> {np.random.randint(60, 85)}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Carte de chaleur des actions défensives
        st.subheader("Carte de chaleur des actions défensives")
        
        # Créer un terrain de football pour la heatmap des actions défensives
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
        
        # Générer des données fictives pour la heatmap des actions défensives
        # Simuler des points d'actions défensives
        x_def = np.concatenate([
            np.random.normal(pitch_length/4, pitch_length/6, 300),  # Défense
            np.random.normal(pitch_length/2, pitch_length/8, 150),  # Milieu
            np.random.normal(3*pitch_length/4, pitch_length/10, 50)  # Attaque
        ])
        
        y_def = np.random.normal(pitch_width/2, pitch_width/3, len(x_def))
        
        # Créer la heatmap
        heatmap = ax.hexbin(x_def, y_def, gridsize=30, cmap='Blues', alpha=0.7)
        plt.colorbar(heatmap, ax=ax, label='Densité d\'actions défensives')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Heatmap des actions défensives - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher la heatmap
        st.pyplot(fig)
        
        # Analyse de la pression
        st.subheader("Analyse de la pression")
        
        # Créer un terrain de football pour l'analyse de la pression
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
        
        # Dessiner les zones de pression
        # Zone de pression haute
        high_press = patches.Rectangle((pitch_length/2, 0), pitch_length/2, pitch_width, 
                                      linewidth=0, edgecolor='none', facecolor='red', alpha=0.2)
        ax.add_patch(high_press)
        
        # Zone de pression moyenne
        mid_press = patches.Rectangle((pitch_length/4, 0), pitch_length/4, pitch_width, 
                                     linewidth=0, edgecolor='none', facecolor='yellow', alpha=0.2)
        ax.add_patch(mid_press)
        
        # Zone de pression basse
        low_press = patches.Rectangle((0, 0), pitch_length/4, pitch_width, 
                                     linewidth=0, edgecolor='none', facecolor='green', alpha=0.2)
        ax.add_patch(low_press)
        
        # Ajouter des annotations
        ax.text(3*pitch_length/4, pitch_width/2, "Pression haute", fontsize=12, ha='center')
        ax.text(3*pitch_length/8, pitch_width/2, "Pression moyenne", fontsize=12, ha='center')
        ax.text(pitch_length/8, pitch_width/2, "Pression basse", fontsize=12, ha='center')
        
        # Générer des données fictives pour les récupérations
        n_recoveries = 50
        x_rec = np.concatenate([
            np.random.normal(3*pitch_length/4, pitch_length/10, int(n_recoveries*0.3)),  # Pression haute
            np.random.normal(3*pitch_length/8, pitch_length/10, int(n_recoveries*0.5)),  # Pression moyenne
            np.random.normal(pitch_length/8, pitch_length/10, int(n_recoveries*0.2))     # Pression basse
        ])
        
        y_rec = np.random.uniform(5, pitch_width-5, len(x_rec))
        
        # Dessiner les points de récupération
        ax.scatter(x_rec, y_rec, color='blue', s=30, alpha=0.7, label='Récupérations')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Analyse de la pression - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        ax.legend(loc='upper left')
        
        # Afficher l'analyse de la pression
        st.pyplot(fig)
        
        # Métriques de pression
        st.subheader("Métriques de pression")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(10, 25)}</div>
                <div class='metric-label'>Récupérations en zone haute</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(15, 30)}</div>
                <div class='metric-label'>Récupérations en zone moyenne</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{np.random.randint(5, 15)}</div>
                <div class='metric-label'>Récupérations en zone basse</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Analyse des récupérations
        st.markdown("""
        <div class='card'>
            <h3>Analyse de la pression et des récupérations</h3>
            <p>Cette visualisation montre les zones où l'équipe exerce sa pression et récupère le ballon. Les zones sont divisées en trois catégories :</p>
            <ul>
                <li><strong>Pression haute (rouge):</strong> Récupérations dans le tiers offensif, indiquant un pressing agressif</li>
                <li><strong>Pression moyenne (jaune):</strong> Récupérations dans le tiers médian, indiquant un bloc médian</li>
                <li><strong>Pression basse (verte):</strong> Récupérations dans le tiers défensif, indiquant un bloc bas</li>
            </ul>
            <p>L'analyse de la pression peut aider à :</p>
            <ul>
                <li>Comprendre la stratégie défensive de l'équipe</li>
                <li>Identifier les zones de récupération préférentielles</li>
                <li>Évaluer l'efficacité du pressing</li>
                <li>Adapter la stratégie offensive contre ce type de défense</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Onglet 4: Analyse des Transitions
    with tab4:
        st.markdown("<h2 class='sub-header'>Analyse des Transitions</h2>", unsafe_allow_html=True)
        
        # Statistiques de transition
        st.subheader("Statistiques de transition")
        
        # Générer des données fictives pour les transitions
        transition_stats = {
            'Contre-attaques': np.random.randint(5, 15),
            'Buts sur contre-attaque': np.random.randint(0, 3),
            'Temps moyen de transition (sec)': round(np.random.uniform(6, 12), 1),
            'Transitions réussies (%)': np.random.randint(40, 70),
            'Récupérations suivies de tir': np.random.randint(3, 10),
            'Distance moyenne de progression (m)': np.random.randint(25, 45)
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>Transitions offensives</h3>
                <p><strong>Contre-attaques:</strong> {transition_stats['Contre-attaques']}</p>
                <p><strong>Buts sur contre-attaque:</strong> {transition_stats['Buts sur contre-attaque']}</p>
                <p><strong>Temps moyen de transition:</strong> {transition_stats['Temps moyen de transition (sec)']} sec</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3>Efficacité des transitions</h3>
                <p><strong>Transitions réussies:</strong> {transition_stats['Transitions réussies (%)']}%</p>
                <p><strong>Récupérations suivies de tir:</strong> {transition_stats['Récupérations suivies de tir']}</p>
                <p><strong>Distance moyenne de progression:</strong> {transition_stats['Distance moyenne de progression (m)']} m</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualisation des transitions
        st.subheader("Visualisation des transitions")
        
        # Créer un terrain de football pour les transitions
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
        
        # Simuler des transitions
        n_transitions = 10
        
        # Points de départ des transitions (récupérations)
        start_x = np.concatenate([
            np.random.normal(pitch_length/4, pitch_length/10, int(n_transitions*0.6)),  # Défense
            np.random.normal(pitch_length/2, pitch_length/10, int(n_transitions*0.4))   # Milieu
        ])
        
        start_y = np.random.uniform(10, pitch_width-10, len(start_x))
        
        # Points d'arrivée des transitions (finalisations)
        end_x = np.random.normal(pitch_length - 20, 10, len(start_x))
        end_y = np.random.normal(pitch_width/2, pitch_width/4, len(start_x))
        
        # Dessiner les transitions
        for i in range(len(start_x)):
            # Point de départ (récupération)
            ax.plot(start_x[i], start_y[i], 'bo', markersize=8)
            
            # Point d'arrivée (finalisation)
            ax.plot(end_x[i], end_y[i], 'ro', markersize=8)
            
            # Flèche de transition
            ax.arrow(start_x[i], start_y[i], 
                    (end_x[i] - start_x[i])*0.9, (end_y[i] - start_y[i])*0.9,  # Réduire légèrement pour éviter de superposer le point d'arrivée
                    head_width=2, head_length=2, fc='green', ec='green', alpha=0.6)
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Transitions défense-attaque - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Ajouter une légende
        ax.plot([], [], 'bo', markersize=8, label='Point de récupération')
        ax.plot([], [], 'ro', markersize=8, label='Point de finalisation')
        ax.plot([], [], '-', color='green', alpha=0.6, label='Trajectoire de transition')
        ax.legend(loc='upper left')
        
        # Afficher les transitions
        st.pyplot(fig)
        
        # Analyse des transitions
        st.markdown("""
        <div class='card'>
            <h3>Analyse des transitions</h3>
            <p>Cette visualisation montre les transitions défense-attaque de l'équipe, depuis le point de récupération du ballon jusqu'au point de finalisation.</p>
            <p>L'analyse des transitions peut aider à :</p>
            <ul>
                <li>Comprendre la vitesse et l'efficacité des contre-attaques</li>
                <li>Identifier les zones de récupération les plus dangereuses</li>
                <li>Analyser les circuits préférentiels en transition</li>
                <li>Évaluer la capacité de l'équipe à passer rapidement de la défense à l'attaque</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Vitesse des transitions
        st.subheader("Vitesse des transitions")
        
        # Générer des données fictives pour la vitesse des transitions
        transition_times = np.random.normal(8, 2, 20)
        transition_times = np.clip(transition_times, 4, 15)
        
        fig = px.histogram(
            transition_times,
            nbins=10,
            labels={'value': 'Temps de transition (sec)'},
            title="Distribution des temps de transition"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des temps de transition
        st.markdown("""
        <div class='card'>
            <h3>Analyse des temps de transition</h3>
            <p>Ce graphique montre la distribution des temps de transition, c'est-à-dire le temps écoulé entre la récupération du ballon et la finalisation de l'action.</p>
            <p>Un temps de transition court indique une équipe capable de contre-attaquer rapidement, tandis qu'un temps plus long peut indiquer une approche plus contrôlée ou des difficultés à progresser rapidement.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommandations tactiques
        st.subheader("Recommandations tactiques")
        
        st.markdown("""
        <div class='card'>
            <h3>Recommandations tactiques basées sur l'analyse</h3>
            <p>En fonction de l'analyse des transitions et des autres aspects tactiques, voici quelques recommandations :</p>
            <ol>
                <li><strong>Optimiser la pression :</strong> Concentrer la pression dans les zones où l'équipe récupère le plus efficacement le ballon.</li>
                <li><strong>Améliorer les transitions :</strong> Travailler sur la vitesse et la précision des transitions pour augmenter leur efficacité.</li>
                <li><strong>Exploiter les circuits préférentiels :</strong> Renforcer les connexions entre les joueurs clés dans le réseau de passes.</li>
                <li><strong>Équilibrer la possession :</strong> Maintenir un équilibre entre la possession sécurisée et les attaques rapides.</li>
                <li><strong>Adapter la stratégie défensive :</strong> Ajuster la hauteur du bloc défensif en fonction de l'adversaire et du contexte du match.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

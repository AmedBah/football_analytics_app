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
    page_title="Analyse Tactique",
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
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-header'>🔍 Analyse Tactique</h1>", unsafe_allow_html=True)

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
    
    # Onglets pour les différentes analyses
    tab1, tab2, tab3 = st.tabs([
        "Carte de Chaleur", 
        "Schéma Tactique", 
        "Flèches de Mouvement"
    ])
    
    # Onglet 1: Carte de Chaleur
    with tab1:
        st.markdown("<h2 class='sub-header'>Carte de Chaleur (Heatmap)</h2>", unsafe_allow_html=True)
        
        # Sélection du type d'événement
        event_type = st.selectbox(
            "Sélectionner un type d'événement",
            options=["Tous les événements", "Passes", "Tirs", "Récupérations", "Pertes de balle", "Duels"],
            index=0
        )
        
        # Sélection de la période
        period = st.radio(
            "Sélectionner une période",
            options=["Match complet", "1ère mi-temps", "2ème mi-temps"],
            horizontal=True
        )
        
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
        if event_type == "Passes":
            # Simuler des passes avec une concentration au milieu du terrain
            x = np.random.normal(pitch_length/2, pitch_length/4, 500)
            y = np.random.normal(pitch_width/2, pitch_width/4, 500)
        elif event_type == "Tirs":
            # Simuler des tirs avec une concentration près du but adverse
            x = np.random.normal(pitch_length - 20, 15, 50)
            y = np.random.normal(pitch_width/2, pitch_width/4, 50)
        elif event_type == "Récupérations":
            # Simuler des récupérations avec une concentration au milieu défensif
            x = np.random.normal(pitch_length/3, pitch_length/6, 200)
            y = np.random.normal(pitch_width/2, pitch_width/3, 200)
        elif event_type == "Pertes de balle":
            # Simuler des pertes de balle avec une concentration au milieu offensif
            x = np.random.normal(2*pitch_length/3, pitch_length/6, 150)
            y = np.random.normal(pitch_width/2, pitch_width/3, 150)
        elif event_type == "Duels":
            # Simuler des duels avec une distribution plus uniforme
            x = np.random.uniform(0, pitch_length, 300)
            y = np.random.uniform(0, pitch_width, 300)
        else:  # Tous les événements
            # Simuler tous les événements avec une distribution plus uniforme
            x = np.random.normal(pitch_length/2, pitch_length/3, 1000)
            y = np.random.normal(pitch_width/2, pitch_width/3, 1000)
        
        # Créer la heatmap
        heatmap = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', alpha=0.7)
        plt.colorbar(heatmap, ax=ax, label='Densité')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Heatmap des {event_type} - {selected_team} ({period})")
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
    
    # Onglet 2: Schéma Tactique
    with tab2:
        st.markdown("<h2 class='sub-header'>Schéma Tactique</h2>", unsafe_allow_html=True)
        
        # Sélection de la formation
        formation = st.selectbox(
            "Sélectionner une formation",
            options=["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "5-3-2"],
            index=0
        )
        
        # Créer un terrain de football pour le schéma tactique
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
        
        # Placer les joueurs selon la formation
        if formation == "4-3-3":
            # Gardien
            ax.plot(5, pitch_width/2, 'ro', markersize=12)
            ax.text(5, pitch_width/2 - 5, "GK", fontsize=10, ha='center')
            
            # Défenseurs
            defenders_y = [pitch_width/5, 2*pitch_width/5, 3*pitch_width/5, 4*pitch_width/5]
            for i, y in enumerate(defenders_y):
                ax.plot(20, y, 'bo', markersize=12)
                ax.text(20, y - 5, f"DEF{i+1}", fontsize=10, ha='center')
            
            # Milieux
            midfielders_y = [pitch_width/4, pitch_width/2, 3*pitch_width/4]
            for i, y in enumerate(midfielders_y):
                ax.plot(50, y, 'go', markersize=12)
                ax.text(50, y - 5, f"MID{i+1}", fontsize=10, ha='center')
            
            # Attaquants
            attackers_y = [pitch_width/4, pitch_width/2, 3*pitch_width/4]
            for i, y in enumerate(attackers_y):
                ax.plot(80, y, 'yo', markersize=12)
                ax.text(80, y - 5, f"ATT{i+1}", fontsize=10, ha='center')
        
        elif formation == "4-4-2":
            # Gardien
            ax.plot(5, pitch_width/2, 'ro', markersize=12)
            ax.text(5, pitch_width/2 - 5, "GK", fontsize=10, ha='center')
            
            # Défenseurs
            defenders_y = [pitch_width/5, 2*pitch_width/5, 3*pitch_width/5, 4*pitch_width/5]
            for i, y in enumerate(defenders_y):
                ax.plot(20, y, 'bo', markersize=12)
                ax.text(20, y - 5, f"DEF{i+1}", fontsize=10, ha='center')
            
            # Milieux
            midfielders_y = [pitch_width/5, 2*pitch_width/5, 3*pitch_width/5, 4*pitch_width/5]
            for i, y in enumerate(midfielders_y):
                ax.plot(50, y, 'go', markersize=12)
                ax.text(50, y - 5, f"MID{i+1}", fontsize=10, ha='center')
            
            # Attaquants
            attackers_y = [pitch_width/3, 2*pitch_width/3]
            for i, y in enumerate(attackers_y):
                ax.plot(80, y, 'yo', markersize=12)
                ax.text(80, y - 5, f"ATT{i+1}", fontsize=10, ha='center')
        
        elif formation == "3-5-2":
            # Gardien
            ax.plot(5, pitch_width/2, 'ro', markersize=12)
            ax.text(5, pitch_width/2 - 5, "GK", fontsize=10, ha='center')
            
            # Défenseurs
            defenders_y = [pitch_width/4, pitch_width/2, 3*pitch_width/4]
            for i, y in enumerate(defenders_y):
                ax.plot(20, y, 'bo', markersize=12)
                ax.text(20, y - 5, f"DEF{i+1}", fontsize=10, ha='center')
            
            # Milieux
            midfielders_y = [pitch_width/6, 2*pitch_width/6, 3*pitch_width/6, 4*pitch_width/6, 5*pitch_width/6]
            for i, y in enumerate(midfielders_y):
                ax.plot(50, y, 'go', markersize=12)
                ax.text(50, y - 5, f"MID{i+1}", fontsize=10, ha='center')
            
            # Attaquants
            attackers_y = [pitch_width/3, 2*pitch_width/3]
            for i, y in enumerate(attackers_y):
                ax.plot(80, y, 'yo', markersize=12)
                ax.text(80, y - 5, f"ATT{i+1}", fontsize=10, ha='center')
        
        elif formation == "4-2-3-1":
            # Gardien
            ax.plot(5, pitch_width/2, 'ro', markersize=12)
            ax.text(5, pitch_width/2 - 5, "GK", fontsize=10, ha='center')
            
            # Défenseurs
            defenders_y = [pitch_width/5, 2*pitch_width/5, 3*pitch_width/5, 4*pitch_width/5]
            for i, y in enumerate(defenders_y):
                ax.plot(20, y, 'bo', markersize=12)
                ax.text(20, y - 5, f"DEF{i+1}", fontsize=10, ha='center')
            
            # Milieux défensifs
            def_midfielders_y = [pitch_width/3, 2*pitch_width/3]
            for i, y in enumerate(def_midfielders_y):
                ax.plot(40, y, 'go', markersize=12)
                ax.text(40, y - 5, f"DMF{i+1}", fontsize=10, ha='center')
            
            # Milieux offensifs
            off_midfielders_y = [pitch_width/4, pitch_width/2, 3*pitch_width/4]
            for i, y in enumerate(off_midfielders_y):
                ax.plot(60, y, 'co', markersize=12)
                ax.text(60, y - 5, f"AMF{i+1}", fontsize=10, ha='center')
            
            # Attaquant
            ax.plot(80, pitch_width/2, 'yo', markersize=12)
            ax.text(80, pitch_width/2 - 5, "ST", fontsize=10, ha='center')
        
        else:  # 5-3-2
            # Gardien
            ax.plot(5, pitch_width/2, 'ro', markersize=12)
            ax.text(5, pitch_width/2 - 5, "GK", fontsize=10, ha='center')
            
            # Défenseurs
            defenders_y = [pitch_width/6, 2*pitch_width/6, 3*pitch_width/6, 4*pitch_width/6, 5*pitch_width/6]
            for i, y in enumerate(defenders_y):
                ax.plot(20, y, 'bo', markersize=12)
                ax.text(20, y - 5, f"DEF{i+1}", fontsize=10, ha='center')
            
            # Milieux
            midfielders_y = [pitch_width/4, pitch_width/2, 3*pitch_width/4]
            for i, y in enumerate(midfielders_y):
                ax.plot(50, y, 'go', markersize=12)
                ax.text(50, y - 5, f"MID{i+1}", fontsize=10, ha='center')
            
            # Attaquants
            attackers_y = [pitch_width/3, 2*pitch_width/3]
            for i, y in enumerate(attackers_y):
                ax.plot(80, y, 'yo', markersize=12)
                ax.text(80, y - 5, f"ATT{i+1}", fontsize=10, ha='center')
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Schéma Tactique {formation} - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher le schéma tactique
        st.pyplot(fig)
        
        # Explication du schéma tactique
        st.markdown("""
        <div class='card'>
            <h3>Interprétation du Schéma Tactique</h3>
            <p>Ce schéma tactique montre l'organisation et les positions des joueurs sur le terrain selon la formation sélectionnée.</p>
            <p>Utilisez cette visualisation pour comprendre la structure de l'équipe et identifier les zones de force et de faiblesse potentielles.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Onglet 3: Flèches de Mouvement
    with tab3:
        st.markdown("<h2 class='sub-header'>Flèches de Mouvement (Flow Chart)</h2>", unsafe_allow_html=True)
        
        # Sélection du type de mouvement
        movement_type = st.selectbox(
            "Sélectionner un type de mouvement",
            options=["Passes", "Progressions avec le ballon", "Transitions défense-attaque"],
            index=0
        )
        
        # Créer un terrain de football pour les flèches de mouvement
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
        
        # Générer des flèches de mouvement fictives
        np.random.seed(42)  # Pour la reproductibilité
        
        if movement_type == "Passes":
            # Simuler des passes entre les joueurs
            n_passes = 30
            
            # Points de départ des passes
            start_x = np.random.uniform(10, 100, n_passes)
            start_y = np.random.uniform(10, pitch_width - 10, n_passes)
            
            # Points d'arrivée des passes
            # Ajouter une tendance vers l'avant
            dx = np.random.normal(15, 10, n_passes)
            dy = np.random.normal(0, 15, n_passes)
            
            end_x = np.clip(start_x + dx, 0, pitch_length)
            end_y = np.clip(start_y + dy, 0, pitch_width)
            
            # Dessiner les flèches
            for i in range(n_passes):
                ax.arrow(start_x[i], start_y[i], end_x[i] - start_x[i], end_y[i] - start_y[i],
                        head_width=2, head_length=2, fc='blue', ec='blue', alpha=0.6)
            
            # Ajouter des points pour représenter les joueurs
            ax.scatter(start_x, start_y, color='red', s=30)
            ax.scatter(end_x, end_y, color='green', s=30)
        
        elif movement_type == "Progressions avec le ballon":
            # Simuler des progressions avec le ballon
            n_progressions = 15
            
            # Points de départ des progressions
            start_x = np.random.uniform(10, 80, n_progressions)
            start_y = np.random.uniform(10, pitch_width - 10, n_progressions)
            
            # Points d'arrivée des progressions
            # Ajouter une tendance vers l'avant avec des mouvements plus longs
            dx = np.random.normal(25, 10, n_progressions)
            dy = np.random.normal(0, 10, n_progressions)
            
            end_x = np.clip(start_x + dx, 0, pitch_length)
            end_y = np.clip(start_y + dy, 0, pitch_width)
            
            # Dessiner les flèches
            for i in range(n_progressions):
                ax.arrow(start_x[i], start_y[i], end_x[i] - start_x[i], end_y[i] - start_y[i],
                        head_width=2, head_length=2, fc='green', ec='green', alpha=0.6, width=1)
            
            # Ajouter des points pour représenter les joueurs
            ax.scatter(start_x, start_y, color='blue', s=30)
            ax.scatter(end_x, end_y, color='blue', s=30)
        
        else:  # Transitions défense-attaque
            # Simuler des transitions défense-attaque
            n_transitions = 10
            
            # Points de départ des transitions (zone défensive)
            start_x = np.random.uniform(10, 40, n_transitions)
            start_y = np.random.uniform(10, pitch_width - 10, n_transitions)
            
            # Points intermédiaires (milieu de terrain)
            mid_x = np.random.uniform(40, 70, n_transitions)
            mid_y = np.random.uniform(10, pitch_width - 10, n_transitions)
            
            # Points d'arrivée des transitions (zone offensive)
            end_x = np.random.uniform(70, 100, n_transitions)
            end_y = np.random.uniform(10, pitch_width - 10, n_transitions)
            
            # Dessiner les flèches courbes
            for i in range(n_transitions):
                # Première partie de la transition
                ax.arrow(start_x[i], start_y[i], mid_x[i] - start_x[i], mid_y[i] - start_y[i],
                        head_width=0, head_length=0, fc='red', ec='red', alpha=0.4, width=0.5)
                
                # Deuxième partie de la transition
                ax.arrow(mid_x[i], mid_y[i], end_x[i] - mid_x[i], end_y[i] - mid_y[i],
                        head_width=2, head_length=2, fc='red', ec='red', alpha=0.6, width=0.5)
            
            # Ajouter des points pour représenter les joueurs
            ax.scatter(start_x, start_y, color='blue', s=30)
            ax.scatter(mid_x, mid_y, color='purple', s=30)
            ax.scatter(end_x, end_y, color='red', s=30)
        
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        ax.set_title(f"Flèches de Mouvement: {movement_type} - {selected_team}")
        ax.set_xlabel("Longueur du terrain (m)")
        ax.set_ylabel("Largeur du terrain (m)")
        ax.set_aspect('equal')
        
        # Afficher les flèches de mouvement
        st.pyplot(fig)
        
        # Explication des flèches de mouvement
        st.markdown("""
        <div class='card'>
            <h3>Interprétation des Flèches de Mouvement</h3>
            <p>Ce graphique montre les circuits préférentiels de l'équipe pour le type de mouvement sélectionné.</p>
            <p>Pour les passes, les flèches indiquent la direction et la fréquence des passes entre les différentes zones du terrain.</p>
            <p>Pour les progressions avec le ballon, les flèches montrent les trajectoires préférentielles des joueurs lorsqu'ils avancent avec le ballon.</p>
            <p>Pour les transitions défense-attaque, les flèches illustrent comment l'équipe passe de la phase défensive à la phase offensive.</p>
            <p>Utilisez cette visualisation pour identifier les circuits de jeu préférentiels et les failles potentielles dans l'organisation adverse.</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

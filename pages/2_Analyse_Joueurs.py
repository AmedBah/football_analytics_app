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
from utils.data_loader import load_competitions, load_matches, load_teams, load_players, load_events

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Joueurs",
    page_icon="👤",
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
st.markdown("<h1 class='main-header'>👤 Analyse de Joueurs</h1>", unsafe_allow_html=True)

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
    
    # Chargement des joueurs de l'équipe sélectionnée
    players = load_players(selected_team, competition_id, season_id)
    
    if not players.empty:
        # Sélection du joueur
        player_options = players['player_name'].tolist() if 'player_name' in players.columns else []
        
        selected_player1 = st.sidebar.selectbox(
            "Sélectionner un joueur",
            options=player_options,
            index=0 if player_options else None
        )
        
        selected_player2 = st.sidebar.selectbox(
            "Sélectionner un joueur pour comparaison",
            options=['Aucun'] + player_options,
            index=0
        )
        
        # Onglets pour les différentes analyses
        tab1, tab2 = st.tabs([
            "Comparaison de Joueurs", 
            "Suivi des Performances"
        ])
        
        # Onglet 1: Comparaison de Joueurs
        with tab1:
            st.markdown("<h2 class='sub-header'>Comparaison de Joueurs</h2>", unsafe_allow_html=True)
            
            # Graphique radar pour comparer les joueurs
            st.subheader("Graphique Radar: Comparaison des performances")
            
            # Créer des données pour le graphique radar (données fictives pour l'exemple)
            categories = ['Buts', 'Passes décisives', 'Passes progressives', 'Tirs', 'Duels gagnés', 'Interceptions']
            
            # Données fictives pour le joueur 1
            player1_values = [
                np.random.randint(0, 15),  # Buts
                np.random.randint(0, 10),  # Passes décisives
                np.random.randint(20, 100),  # Passes progressives
                np.random.randint(10, 50),  # Tirs
                np.random.randint(50, 150),  # Duels gagnés
                np.random.randint(10, 50)   # Interceptions
            ]
            
            # Données fictives pour le joueur 2 ou la moyenne du poste
            if selected_player2 != 'Aucun':
                player2_values = [
                    np.random.randint(0, 15),  # Buts
                    np.random.randint(0, 10),  # Passes décisives
                    np.random.randint(20, 100),  # Passes progressives
                    np.random.randint(10, 50),  # Tirs
                    np.random.randint(50, 150),  # Duels gagnés
                    np.random.randint(10, 50)   # Interceptions
                ]
                comparison_name = selected_player2
            else:
                # Utiliser la moyenne du poste
                player2_values = [
                    np.random.randint(0, 10),  # Buts (moyenne)
                    np.random.randint(0, 8),  # Passes décisives (moyenne)
                    np.random.randint(15, 80),  # Passes progressives (moyenne)
                    np.random.randint(8, 40),  # Tirs (moyenne)
                    np.random.randint(40, 120),  # Duels gagnés (moyenne)
                    np.random.randint(8, 40)   # Interceptions (moyenne)
                ]
                comparison_name = "Moyenne du poste"
            
            # Normaliser les valeurs pour le graphique radar
            max_values = [max(player1_values[i], player2_values[i]) for i in range(len(categories))]
            player1_values_norm = [player1_values[i]/max_values[i] if max_values[i] > 0 else 0 for i in range(len(categories))]
            player2_values_norm = [player2_values[i]/max_values[i] if max_values[i] > 0 else 0 for i in range(len(categories))]
            
            # Créer le graphique radar
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=player1_values_norm,
                theta=categories,
                fill='toself',
                name=selected_player1
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=player2_values_norm,
                theta=categories,
                fill='toself',
                name=comparison_name
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
            
            # Boîte à moustaches pour analyser les variations de performance
            st.subheader("Boîte à moustaches: Analyse des variations de performance")
            
            # Sélection de la statistique à analyser
            stat_type = st.selectbox(
                "Sélectionner une statistique",
                options=["Buts", "Passes décisives", "Passes progressives", "Tirs", "Duels gagnés", "Interceptions"],
                index=0
            )
            
            # Générer des données fictives pour les boîtes à moustaches
            player1_data = np.random.normal(
                player1_values[categories.index(stat_type)]/10, 
                player1_values[categories.index(stat_type)]/20, 
                20
            )
            
            player2_data = np.random.normal(
                player2_values[categories.index(stat_type)]/10, 
                player2_values[categories.index(stat_type)]/20, 
                20
            )
            
            # Créer le dataframe pour la boîte à moustaches
            boxplot_data = pd.DataFrame({
                'Joueur': [selected_player1] * len(player1_data) + [comparison_name] * len(player2_data),
                stat_type: np.concatenate([player1_data, player2_data])
            })
            
            fig = px.box(
                boxplot_data, 
                x='Joueur', 
                y=stat_type,
                color='Joueur',
                title=f"Distribution de {stat_type} par match"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Diagramme de dispersion pour analyser les relations entre statistiques
            st.subheader("Diagramme de dispersion: Relation entre statistiques")
            
            # Sélection des variables pour le diagramme de dispersion
            col1, col2 = st.columns(2)
            
            with col1:
                x_variable = st.selectbox(
                    "Variable X",
                    options=["Passes progressives", "Tirs", "Duels gagnés", "Minutes jouées", "Distance parcourue"],
                    index=0
                )
            
            with col2:
                y_variable = st.selectbox(
                    "Variable Y",
                    options=["Buts", "Passes décisives", "Occasions créées", "xG (Expected Goals)", "xA (Expected Assists)"],
                    index=0
                )
            
            # Créer des données fictives pour le diagramme de dispersion
            np.random.seed(42)  # Pour la reproductibilité
            
            # Générer des données pour plusieurs joueurs
            n_players = 20
            
            if x_variable == "Passes progressives":
                x_data = np.random.normal(50, 20, n_players)
            elif x_variable == "Tirs":
                x_data = np.random.normal(3, 1, n_players)
            elif x_variable == "Duels gagnés":
                x_data = np.random.normal(10, 3, n_players)
            elif x_variable == "Minutes jouées":
                x_data = np.random.normal(70, 20, n_players)
            else:  # Distance parcourue
                x_data = np.random.normal(9, 2, n_players)
            
            # Ajouter une corrélation avec la variable Y
            correlation = 0.7  # Corrélation positive
            noise = np.random.normal(0, 1, n_players)
            
            if y_variable == "Buts":
                y_data = 0.2 + 0.01 * x_data + noise * 0.3
                y_data = np.round(np.clip(y_data, 0, 2), 1)
            elif y_variable == "Passes décisives":
                y_data = 0.1 + 0.008 * x_data + noise * 0.2
                y_data = np.round(np.clip(y_data, 0, 1.5), 1)
            elif y_variable == "Occasions créées":
                y_data = 0.5 + 0.02 * x_data + noise * 0.5
                y_data = np.round(np.clip(y_data, 0, 3), 1)
            elif y_variable == "xG (Expected Goals)":
                y_data = 0.1 + 0.005 * x_data + noise * 0.2
                y_data = np.round(np.clip(y_data, 0, 1), 2)
            else:  # xA (Expected Assists)
                y_data = 0.05 + 0.004 * x_data + noise * 0.15
                y_data = np.round(np.clip(y_data, 0, 0.8), 2)
            
            # Créer un dataframe pour le diagramme de dispersion
            scatter_data = pd.DataFrame({
                'Joueur': [f"Joueur {i+1}" for i in range(n_players)],
                x_variable: x_data,
                y_variable: y_data
            })
            
            # Marquer les joueurs sélectionnés
            player_colors = ['#1E88E5' if player == selected_player1 else 
                           '#FFC107' if player == selected_player2 else 
                           '#CCCCCC' for player in scatter_data['Joueur']]
            
            # Créer le diagramme de dispersion
            fig = px.scatter(
                scatter_data,
                x=x_variable,
                y=y_variable,
                text='Joueur',
                title=f"Relation entre {x_variable} et {y_variable}",
                trendline="ols"  # Ajouter une ligne de tendance
            )
            
            # Mettre à jour les couleurs des points
            fig.update_traces(marker=dict(color=player_colors, size=12), selector=dict(mode='markers+text'))
            
            # Afficher le diagramme
            st.plotly_chart(fig, use_container_width=True)
        
        # Onglet 2: Suivi des Performances
        with tab2:
            st.markdown("<h2 class='sub-header'>Suivi des Performances dans le Temps</h2>", unsafe_allow_html=True)
            
            # Graphique en courbes pour suivre la progression
            st.subheader(f"Progression de {selected_player1} sur plusieurs matchs")
            
            # Sélection de la statistique à suivre
            stat_to_track = st.selectbox(
                "Sélectionner une statistique à suivre",
                options=["Buts", "Passes décisives", "Note globale", "Distance parcourue", "Passes réussies"],
                index=0
            )
            
            # Générer des données fictives pour la progression
            n_matches = 15
            match_dates = pd.date_range(start='2023-08-01', periods=n_matches, freq='W')
            
            if stat_to_track == "Buts":
                stat_values = np.random.choice([0, 0, 0, 0, 1, 1, 2], size=n_matches)
            elif stat_to_track == "Passes décisives":
                stat_values = np.random.choice([0, 0, 0, 1, 1], size=n_matches)
            elif stat_to_track == "Note globale":
                stat_values = np.random.normal(7, 1, n_matches)
                stat_values = np.round(np.clip(stat_values, 4, 10), 1)
            elif stat_to_track == "Distance parcourue":
                stat_values = np.random.normal(9, 1, n_matches)
                stat_values = np.round(stat_values, 1)
            else:  # Passes réussies
                stat_values = np.random.normal(40, 10, n_matches)
                stat_values = np.round(stat_values)
            
            # Créer le dataframe pour le graphique en courbes
            progression_data = pd.DataFrame({
                'Date': match_dates,
                'Match': [f"Match {i+1}" for i in range(n_matches)],
                stat_to_track: stat_values
            })
            
            # Créer le graphique en courbes
            fig = px.line(
                progression_data,
                x='Date',
                y=stat_to_track,
                markers=True,
                title=f"Évolution de {stat_to_track} pour {selected_player1}"
            )
            
            # Ajouter des annotations pour les événements importants
            if stat_to_track == "Buts" or stat_to_track == "Passes décisives":
                # Trouver les matchs avec des valeurs élevées
                important_matches = progression_data[progression_data[stat_to_track] > 0]
                
                for _, match in important_matches.iterrows():
                    fig.add_annotation(
                        x=match['Date'],
                        y=match[stat_to_track],
                        text=f"{int(match[stat_to_track])} {stat_to_track.lower()}",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-30
                    )
            
            # Afficher le graphique
            st.plotly_chart(fig, use_container_width=True)
            
            # Chronologie annotée
            st.subheader("Chronologie annotée des événements clés")
            
            # Créer une chronologie fictive
            timeline_data = [
                {"date": "2023-08-15", "event": "Début de saison", "description": "Premier match de la saison"},
                {"date": "2023-09-10", "event": "Premier but", "description": "Premier but de la saison contre l'équipe X"},
                {"date": "2023-10-05", "event": "Blessure légère", "description": "Blessure musculaire mineure, absent pour 1 match"},
                {"date": "2023-11-20", "event": "Changement tactique", "description": "Changement de position suite à une nouvelle stratégie de l'entraîneur"},
                {"date": "2023-12-15", "event": "Performance exceptionnelle", "description": "Homme du match avec 2 buts et 1 passe décisive"},
                {"date": "2024-02-10", "event": "Retour de blessure", "description": "Retour après 3 semaines d'absence"},
                {"date": "2024-03-05", "event": "Milestone", "description": "10ème but de la saison, toutes compétitions confondues"}
            ]
            
            # Créer un dataframe pour la chronologie
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df['date'] = pd.to_datetime(timeline_df['date'])
            timeline_df = timeline_df.sort_values('date')
            
            # Afficher la chronologie
            for i, event in timeline_df.iterrows():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{event['date'].strftime('%d %b %Y')}**")
                    st.markdown(f"*{event['event']}*")
                with col2:
                    st.markdown(f"{event['description']}")
                st.markdown("---")
            
            # Analyse des performances
            st.subheader("Analyse des performances")
            
            # Créer des métriques fictives pour le joueur
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Buts par 90 min", "0.45", "+0.12")
            with col2:
                st.metric("Passes décisives par 90 min", "0.32", "+0.08")
            with col3:
                st.metric("xG par 90 min", "0.38", "-0.07")
            with col4:
                st.metric("Duels gagnés (%)", "62%", "+5%")
            
            # Ajouter un commentaire d'analyse
            st.markdown("""
            <div class='card'>
                <h3>Analyse de la progression</h3>
                <p>Le joueur montre une amélioration constante dans ses performances offensives, avec une augmentation notable 
                des buts par 90 minutes et des passes décisives. Cependant, sa valeur xG a légèrement diminué, ce qui pourrait 
                indiquer une meilleure efficacité de conversion plutôt qu'une augmentation des occasions créées.</p>
                <p>Son pourcentage de duels gagnés a également augmenté, ce qui montre une amélioration dans son jeu physique 
                et sa capacité à conserver le ballon sous pression.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"Aucun joueur trouvé pour l'équipe {selected_team}. Veuillez sélectionner une autre équipe.")

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

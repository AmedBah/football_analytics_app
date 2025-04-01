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
from utils.data_loader import (
    load_competitions, load_matches, load_teams, load_players, 
    load_events, load_filtered_events, calculate_player_stats
)

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Joueurs Avancée",
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
    .positive-trend {
        color: #4CAF50;
    }
    .negative-trend {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-header'>👤 Analyse de Joueurs Avancée</h1>", unsafe_allow_html=True)

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
        
        # Options d'analyse avancée
        st.sidebar.header("Options d'analyse avancée")
        
        analysis_period = st.sidebar.radio(
            "Période d'analyse",
            options=["Saison complète", "5 derniers matchs", "10 derniers matchs"],
            index=0
        )
        
        normalize_stats = st.sidebar.checkbox("Normaliser par 90 minutes", value=True)
        
        show_percentiles = st.sidebar.checkbox("Afficher les percentiles", value=True)
        
        # Onglets pour les différentes analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "Profil du Joueur", 
            "Comparaison Avancée",
            "Évolution Temporelle",
            "Analyse Contextuelle"
        ])
        
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
                
                # Calculer ou simuler les statistiques du joueur
                player_stats = calculate_player_stats(selected_player1, selected_team, competition_id, season_id)
                
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
                        <div class='metric-value'>{player_stats.get('matches_played', 0)}</div>
                        <div class='metric-label'>Matchs joués</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    minutes = player_stats.get('minutes_played', 0)
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{minutes}</div>
                        <div class='metric-label'>Minutes jouées</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Statistiques par 90 minutes
                if normalize_stats and minutes > 0:
                    st.markdown("<h4>Statistiques par 90 minutes</h4>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        goals_per_90 = round(player_stats.get('goals', 0) * 90 / minutes, 2)
                        st.markdown(f"""
                        <div class='metric-container'>
                            <div class='metric-value'>{goals_per_90}</div>
                            <div class='metric-label'>Buts / 90 min</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        assists_per_90 = round(player_stats.get('assists', 0) * 90 / minutes, 2)
                        st.markdown(f"""
                        <div class='metric-container'>
                            <div class='metric-value'>{assists_per_90}</div>
                            <div class='metric-label'>Passes déc. / 90 min</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        shots_per_90 = round(player_stats.get('shots', 0) * 90 / minutes, 2)
                        st.markdown(f"""
                        <div class='metric-container'>
                            <div class='metric-value'>{shots_per_90}</div>
                            <div class='metric-label'>Tirs / 90 min</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        key_passes_per_90 = round(player_stats.get('key_passes', 0) * 90 / minutes, 2)
                        st.markdown(f"""
                        <div class='metric-container'>
                            <div class='metric-value'>{key_passes_per_90}</div>
                            <div class='metric-label'>Passes clés / 90 min</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Graphique radar des compétences
                st.markdown("<h4>Profil de compétences</h4>", unsafe_allow_html=True)
                
                # Créer des données pour le graphique radar
                categories = ['Finition', 'Passes', 'Dribbles', 'Défense', 'Physique', 'Vitesse']
                
                # Générer des valeurs aléatoires pour l'exemple
                values = np.random.randint(60, 95, len(categories))
                
                # Créer le graphique radar
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=selected_player1,
                    line=dict(color='#1E88E5')
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des forces et faiblesses
                st.markdown("<h4>Forces et faiblesses</h4>", unsafe_allow_html=True)
                
                # Identifier les forces et faiblesses basées sur les valeurs du radar
                strengths = [categories[i] for i in range(len(categories)) if values[i] >= 85]
                weaknesses = [categories[i] for i in range(len(categories)) if values[i] <= 70]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h5>Forces</h5>", unsafe_allow_html=True)
                    if strengths:
                        for strength in strengths:
                            st.markdown(f"✅ **{strength}**")
                    else:
                        st.markdown("Aucune force particulière identifiée.")
                
                with col2:
                    st.markdown("<h5>Points à améliorer</h5>", unsafe_allow_html=True)
                    if weaknesses:
                        for weakness in weaknesses:
                            st.markdown(f"⚠️ **{weakness}**")
                    else:
                        st.markdown("Aucune faiblesse particulière identifiée.")
        
        # Onglet 2: Comparaison Avancée
        with tab2:
            st.markdown("<h2 class='sub-header'>Comparaison Avancée</h2>", unsafe_allow_html=True)
            
            # Sélection du type de comparaison
            comparison_type = st.radio(
                "Type de comparaison",
                options=["Avec un autre joueur", "Avec la moyenne du poste", "Avec les meilleurs du poste"],
                horizontal=True
            )
            
            # Sélection des métriques à comparer
            metrics_options = [
                "Buts", "Passes décisives", "Tirs", "Tirs cadrés", 
                "Passes", "Passes réussies (%)", "Passes clés", 
                "Dribbles réussis", "Duels gagnés", "Interceptions", 
                "Tacles", "Fautes", "Distance parcourue"
            ]
            
            selected_metrics = st.multiselect(
                "Sélectionner les métriques à comparer",
                options=metrics_options,
                default=metrics_options[:6]
            )
            
            if selected_metrics:
                # Graphique radar pour comparer les joueurs
                st.subheader("Graphique Radar: Comparaison des performances")
                
                # Créer des données pour le graphique radar
                player1_values = []
                player2_values = []
                
                for metric in selected_metrics:
                    # Simuler des valeurs pour le joueur 1
                    if metric == "Buts":
                        player1_values.append(player_stats.get('goals', np.random.randint(0, 15)))
                    elif metric == "Passes décisives":
                        player1_values.append(player_stats.get('assists', np.random.randint(0, 10)))
                    elif metric == "Tirs":
                        player1_values.append(player_stats.get('shots', np.random.randint(10, 50)))
                    elif metric == "Passes réussies (%)":
                        player1_values.append(player_stats.get('pass_accuracy', np.random.randint(70, 95)))
                    else:
                        player1_values.append(np.random.randint(10, 100))
                    
                    # Simuler des valeurs pour le joueur 2 ou la moyenne
                    if comparison_type == "Avec un autre joueur" and selected_player2 != 'Aucun':
                        player2_values.append(np.random.randint(10, 100))
                        comparison_name = selected_player2
                    elif comparison_type == "Avec les meilleurs du poste":
                        player2_values.append(np.random.randint(70, 100))
                        comparison_name = "Top 10% du poste"
                    else:
                        player2_values.append(np.random.randint(40, 80))
                        comparison_name = "Moyenne du poste"
                
                # Normaliser les valeurs pour le graphique radar
                max_values = [max(player1_values[i], player2_values[i]) for i in range(len(selected_metrics))]
                player1_values_norm = [player1_values[i]/max_values[i] if max_values[i] > 0 else 0 for i in range(len(selected_metrics))]
                player2_values_norm = [player2_values[i]/max_values[i] if max_values[i] > 0 else 0 for i in range(len(selected_metrics))]
                
                # Créer le graphique radar
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=player1_values_norm,
                    theta=selected_metrics,
                    fill='toself',
                    name=selected_player1,
                    line=dict(color='#1E88E5')
                ))
                
                fig.add_trace(go.Scatterpolar(
                    r=player2_values_norm,
                    theta=selected_metrics,
                    fill='toself',
                    name=comparison_name,
                    line=dict(color='#FFC107')
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
                
                # Tableau de comparaison détaillé
                st.subheader("Tableau de comparaison détaillé")
                
                comparison_data = {
                    'Métrique': selected_metrics,
                    selected_player1: player1_values,
                    comparison_name: player2_values
                }
                
                if show_percentiles:
                    # Calculer les percentiles fictifs
                    percentiles = [np.random.randint(1, 100) for _ in range(len(selected_metrics))]
                    comparison_data['Percentile'] = percentiles
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Afficher le tableau
                st.dataframe(comparison_df, use_container_width=True)
                
                # Graphique à barres pour comparer les valeurs absolues
                st.subheader("Comparaison des valeurs absolues")
                
                # Préparer les données pour le graphique à barres
                bar_data = pd.DataFrame({
                    'Métrique': selected_metrics * 2,
                    'Joueur': [selected_player1] * len(selected_metrics) + [comparison_name] * len(selected_metrics),
                    'Valeur': player1_values + player2_values
                })
                
                # Créer le graphique à barres
                fig = px.bar(
                    bar_data,
                    x='Métrique',
                    y='Valeur',
                    color='Joueur',
                    barmode='group',
                    title=f"Comparaison entre {selected_player1} et {comparison_name}"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des différences
                st.subheader("Analyse des différences")
                
                # Calculer les différences en pourcentage
                differences = []
                for i in range(len(selected_metrics)):
                    if player2_values[i] > 0:
                        diff_pct = round((player1_values[i] - player2_values[i]) / player2_values[i] * 100, 1)
                        differences.append((selected_metrics[i], diff_pct))
                
                # Trier les différences
                differences.sort(key=lambda x: x[1], reverse=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h5>Points forts par rapport à la référence</h5>", unsafe_allow_html=True)
                    strengths = [d for d in differences if d[1] > 10]
                    if strengths:
                        for metric, diff in strengths:
                            st.markdown(f"✅ **{metric}**: +{diff}%")
                    else:
                        st.markdown("Aucun avantage significatif identifié.")
                
                with col2:
                    st.markdown("<h5>Points à améliorer par rapport à la référence</h5>", unsafe_allow_html=True)
                    weaknesses = [d for d in differences if d[1] < -10]
                    if weaknesses:
                        for metric, diff in weaknesses:
                            st.markdown(f"⚠️ **{metric}**: {diff}%")
                    else:
                        st.markdown("Aucune faiblesse significative identifiée.")
            else:
                st.warning("Veuillez sélectionner au moins une métrique pour la comparaison.")
        
        # Onglet 3: Évolution Temporelle
        with tab3:
            st.markdown("<h2 class='sub-header'>Évolution Temporelle</h2>", unsafe_allow_html=True)
            
            # Sélection de la métrique à suivre
            metric_to_track = st.selectbox(
                "Sélectionner une métrique à suivre",
                options=["Buts", "Passes décisives", "Note globale", "Distance parcourue", "Passes réussies", "xG", "xA"],
                index=0
            )
            
            # Générer des données fictives pour la progression
            n_matches = 15
            match_dates = pd.date_range(start='2023-08-01', periods=n_matches, freq='W')
            
            if metric_to_track == "Buts":
                stat_values = np.random.choice([0, 0, 0, 0, 1, 1, 2], size=n_matches)
            elif metric_to_track == "Passes décisives":
                stat_values = np.random.choice([0, 0, 0, 1, 1], size=n_matches)
            elif metric_to_track == "Note globale":
                stat_values = np.random.normal(7, 1, n_matches)
                stat_values = np.round(np.clip(stat_values, 4, 10), 1)
            elif metric_to_track == "Distance parcourue":
                stat_values = np.random.normal(9, 1, n_matches)
                stat_values = np.round(stat_values, 1)
            elif metric_to_track == "xG":
                stat_values = np.random.normal(0.3, 0.2, n_matches)
                stat_values = np.round(np.clip(stat_values, 0, 1), 2)
            elif metric_to_track == "xA":
                stat_values = np.random.normal(0.2, 0.15, n_matches)
                stat_values = np.round(np.clip(stat_values, 0, 0.8), 2)
            else:  # Passes réussies
                stat_values = np.random.normal(40, 10, n_matches)
                stat_values = np.round(stat_values)
            
            # Créer le dataframe pour le graphique en courbes
            progression_data = pd.DataFrame({
                'Date': match_dates,
                'Match': [f"Match {i+1}" for i in range(n_matches)],
                metric_to_track: stat_values
            })
            
            # Ajouter une colonne pour la moyenne mobile
            progression_data['Moyenne mobile (3 matchs)'] = progression_data[metric_to_track].rolling(window=3, min_periods=1).mean()
            
            # Créer le graphique en courbes
            fig = px.line(
                progression_data,
                x='Date',
                y=[metric_to_track, 'Moyenne mobile (3 matchs)'],
                markers=True,
                title=f"Évolution de {metric_to_track} pour {selected_player1}"
            )
            
            # Ajouter des annotations pour les événements importants
            if metric_to_track == "Buts" or metric_to_track == "Passes décisives":
                # Trouver les matchs avec des valeurs élevées
                important_matches = progression_data[progression_data[metric_to_track] > 0]
                
                for _, match in important_matches.iterrows():
                    fig.add_annotation(
                        x=match['Date'],
                        y=match[metric_to_track],
                        text=f"{match[metric_to_track]} {metric_to_track.lower()}",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-30
                    )
            
            # Afficher le graphique
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse de tendance
            st.subheader("Analyse de tendance")
            
            # Calculer la tendance
            first_half = stat_values[:len(stat_values)//2].mean()
            second_half = stat_values[len(stat_values)//2:].mean()
            trend_pct = round((second_half - first_half) / first_half * 100 if first_half > 0 else 0, 1)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{round(stat_values.mean(), 2)}</div>
                    <div class='metric-label'>Moyenne sur la période</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value'>{round(second_half, 2)}</div>
                    <div class='metric-label'>Moyenne récente</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                trend_class = "positive-trend" if trend_pct > 0 else "negative-trend"
                trend_sign = "+" if trend_pct > 0 else ""
                st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-value {trend_class}'>{trend_sign}{trend_pct}%</div>
                    <div class='metric-label'>Tendance</div>
                </div>
                """, unsafe_allow_html=True)
            
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
        
        # Onglet 4: Analyse Contextuelle
        with tab4:
            st.markdown("<h2 class='sub-header'>Analyse Contextuelle</h2>", unsafe_allow_html=True)
            
            # Sélection du contexte d'analyse
            context_type = st.radio(
                "Contexte d'analyse",
                options=["Domicile vs Extérieur", "Niveau d'adversaire", "Phase de jeu", "Position sur le terrain"],
                horizontal=True
            )
            
            if context_type == "Domicile vs Extérieur":
                # Créer des données fictives pour la comparaison domicile/extérieur
                metrics = ["Buts", "Passes décisives", "Tirs", "Passes réussies (%)", "Duels gagnés (%)", "Distance (km)"]
                
                home_values = [
                    np.random.randint(0, 10),  # Buts
                    np.random.randint(0, 8),   # Passes décisives
                    np.random.randint(10, 40), # Tirs
                    np.random.randint(70, 90), # Passes réussies (%)
                    np.random.randint(50, 70), # Duels gagnés (%)
                    round(np.random.uniform(8, 12), 1)  # Distance (km)
                ]
                
                away_values = [
                    np.random.randint(0, 10),  # Buts
                    np.random.randint(0, 8),   # Passes décisives
                    np.random.randint(10, 40), # Tirs
                    np.random.randint(70, 90), # Passes réussies (%)
                    np.random.randint(50, 70), # Duels gagnés (%)
                    round(np.random.uniform(8, 12), 1)  # Distance (km)
                ]
                
                # Créer le dataframe pour la comparaison
                context_data = pd.DataFrame({
                    'Métrique': metrics,
                    'Domicile': home_values,
                    'Extérieur': away_values
                })
                
                # Afficher le tableau
                st.dataframe(context_data, use_container_width=True)
                
                # Créer le graphique à barres
                fig = px.bar(
                    context_data,
                    x='Métrique',
                    y=['Domicile', 'Extérieur'],
                    barmode='group',
                    title=f"Performances de {selected_player1} à domicile vs à l'extérieur"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des différences
                home_better = sum([1 for i in range(len(metrics)) if home_values[i] > away_values[i]])
                away_better = sum([1 for i in range(len(metrics)) if away_values[i] > home_values[i]])
                
                if home_better > away_better:
                    st.info(f"**{selected_player1}** semble être plus performant à domicile, avec de meilleures statistiques dans {home_better} catégories sur {len(metrics)}.")
                elif away_better > home_better:
                    st.info(f"**{selected_player1}** semble être plus performant à l'extérieur, avec de meilleures statistiques dans {away_better} catégories sur {len(metrics)}.")
                else:
                    st.info(f"**{selected_player1}** montre des performances équilibrées à domicile et à l'extérieur.")
            
            elif context_type == "Niveau d'adversaire":
                # Créer des données fictives pour la comparaison selon le niveau d'adversaire
                metrics = ["Buts", "Passes décisives", "Tirs", "Passes réussies (%)", "Duels gagnés (%)", "Distance (km)"]
                
                top_values = [
                    np.random.randint(0, 5),   # Buts
                    np.random.randint(0, 5),   # Passes décisives
                    np.random.randint(5, 20),  # Tirs
                    np.random.randint(70, 85), # Passes réussies (%)
                    np.random.randint(45, 65), # Duels gagnés (%)
                    round(np.random.uniform(9, 12), 1)  # Distance (km)
                ]
                
                mid_values = [
                    np.random.randint(0, 8),   # Buts
                    np.random.randint(0, 6),   # Passes décisives
                    np.random.randint(10, 30), # Tirs
                    np.random.randint(75, 90), # Passes réussies (%)
                    np.random.randint(50, 70), # Duels gagnés (%)
                    round(np.random.uniform(8, 11), 1)  # Distance (km)
                ]
                
                bottom_values = [
                    np.random.randint(0, 10),  # Buts
                    np.random.randint(0, 8),   # Passes décisives
                    np.random.randint(15, 40), # Tirs
                    np.random.randint(80, 95), # Passes réussies (%)
                    np.random.randint(55, 75), # Duels gagnés (%)
                    round(np.random.uniform(7, 10), 1)  # Distance (km)
                ]
                
                # Créer le dataframe pour la comparaison
                context_data = pd.DataFrame({
                    'Métrique': metrics,
                    'Top 6': top_values,
                    'Milieu de tableau': mid_values,
                    'Bas de tableau': bottom_values
                })
                
                # Afficher le tableau
                st.dataframe(context_data, use_container_width=True)
                
                # Créer le graphique à barres
                fig = px.bar(
                    context_data,
                    x='Métrique',
                    y=['Top 6', 'Milieu de tableau', 'Bas de tableau'],
                    barmode='group',
                    title=f"Performances de {selected_player1} selon le niveau d'adversaire"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des performances
                st.markdown("""
                <div class='card'>
                    <h3>Analyse des performances selon le niveau d'adversaire</h3>
                    <p>Cette analyse montre comment les performances du joueur varient en fonction du niveau de l'adversaire.</p>
                    <p>Les différences observées peuvent indiquer :</p>
                    <ul>
                        <li>La capacité du joueur à s'élever au niveau de la compétition</li>
                        <li>Les types d'adversaires contre lesquels le joueur est le plus efficace</li>
                        <li>Les ajustements tactiques potentiels selon l'adversaire</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            elif context_type == "Phase de jeu":
                # Créer des données fictives pour la répartition des actions par phase de jeu
                phases = ["Organisation offensive", "Transition offensive", "Organisation défensive", "Transition défensive", "Coups de pied arrêtés"]
                
                # Générer des valeurs aléatoires pour chaque phase
                values = np.random.randint(10, 100, len(phases))
                total = sum(values)
                percentages = [round(v / total * 100, 1) for v in values]
                
                # Créer le dataframe pour la répartition
                phase_data = pd.DataFrame({
                    'Phase de jeu': phases,
                    'Actions': values,
                    'Pourcentage': percentages
                })
                
                # Afficher le tableau
                st.dataframe(phase_data, use_container_width=True)
                
                # Créer le graphique en secteurs
                fig = px.pie(
                    phase_data,
                    values='Pourcentage',
                    names='Phase de jeu',
                    title=f"Répartition des actions de {selected_player1} par phase de jeu"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse de l'efficacité par phase
                st.subheader("Efficacité par phase de jeu")
                
                # Générer des données fictives pour l'efficacité
                efficiency_data = pd.DataFrame({
                    'Phase de jeu': phases,
                    'Efficacité (%)': [np.random.randint(50, 90) for _ in range(len(phases))]
                })
                
                # Créer le graphique à barres pour l'efficacité
                fig = px.bar(
                    efficiency_data,
                    x='Phase de jeu',
                    y='Efficacité (%)',
                    title=f"Efficacité de {selected_player1} par phase de jeu"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommandations tactiques
                st.markdown("""
                <div class='card'>
                    <h3>Recommandations tactiques</h3>
                    <p>Basées sur l'analyse des phases de jeu, voici quelques recommandations tactiques :</p>
                    <ul>
                        <li>Maximiser l'implication du joueur dans les phases où il est le plus efficace</li>
                        <li>Travailler sur l'amélioration des phases où l'efficacité est plus faible</li>
                        <li>Adapter le rôle du joueur en fonction des forces identifiées par phase</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            else:  # Position sur le terrain
                st.subheader("Zones d'influence sur le terrain")
                
                # Créer un terrain de football pour la heatmap
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
                # Simuler différentes distributions selon la position du joueur
                position = np.random.choice(["Attaquant", "Milieu", "Défenseur"])
                
                if position == "Attaquant":
                    # Concentration dans la moitié offensive
                    x = np.random.normal(3*pitch_length/4, pitch_length/6, 500)
                    y = np.random.normal(pitch_width/2, pitch_width/4, 500)
                elif position == "Milieu":
                    # Concentration au milieu du terrain
                    x = np.random.normal(pitch_length/2, pitch_length/4, 500)
                    y = np.random.normal(pitch_width/2, pitch_width/3, 500)
                else:  # Défenseur
                    # Concentration dans la moitié défensive
                    x = np.random.normal(pitch_length/4, pitch_length/6, 500)
                    y = np.random.normal(pitch_width/2, pitch_width/4, 500)
                
                # Créer la heatmap
                heatmap = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', alpha=0.7)
                plt.colorbar(heatmap, ax=ax, label='Densité')
                
                ax.set_xlim(-5, pitch_length + 5)
                ax.set_ylim(-5, pitch_width + 5)
                ax.set_title(f"Zones d'influence de {selected_player1}")
                ax.set_xlabel("Longueur du terrain (m)")
                ax.set_ylabel("Largeur du terrain (m)")
                ax.set_aspect('equal')
                
                # Afficher la heatmap
                st.pyplot(fig)
                
                # Analyse des zones d'influence
                st.markdown("""
                <div class='card'>
                    <h3>Analyse des zones d'influence</h3>
                    <p>Cette heatmap montre les zones du terrain où le joueur est le plus actif. Les zones en rouge indiquent une forte concentration d'actions, tandis que les zones en jaune indiquent une concentration plus faible.</p>
                    <p>L'analyse des zones d'influence peut aider à :</p>
                    <ul>
                        <li>Comprendre le rôle réel du joueur sur le terrain</li>
                        <li>Identifier les zones où le joueur est le plus efficace</li>
                        <li>Adapter le système tactique pour maximiser l'impact du joueur</li>
                        <li>Détecter les déséquilibres potentiels dans la couverture du terrain</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Statistiques par zone
                st.subheader("Statistiques par zone du terrain")
                
                # Créer des données fictives pour les statistiques par zone
                zones = ["Tiers défensif", "Milieu de terrain", "Tiers offensif"]
                
                # Générer des statistiques aléatoires pour chaque zone
                zone_stats = pd.DataFrame({
                    'Zone': zones,
                    'Actions': [np.random.randint(10, 100) for _ in range(len(zones))],
                    'Réussite (%)': [np.random.randint(50, 90) for _ in range(len(zones))],
                    'Duels gagnés (%)': [np.random.randint(40, 80) for _ in range(len(zones))],
                    'Passes clés': [np.random.randint(0, 20) for _ in range(len(zones))]
                })
                
                # Afficher le tableau
                st.dataframe(zone_stats, use_container_width=True)
    else:
        st.warning(f"Aucun joueur trouvé pour l'équipe {selected_team}. Veuillez sélectionner une autre équipe.")

except Exception as e:
    st.error(f"Une erreur s'est produite: {e}")
    st.info("Assurez-vous d'avoir accès aux données StatsBomb et que les API sont correctement configurées.")

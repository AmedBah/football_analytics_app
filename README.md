# Application d'Analyse Footballistique avec Streamlit

Cette application interactive permet aux entraîneurs d'analyser et d'optimiser les performances de leur équipe et de leurs joueurs grâce à la data science appliquée au football.

## Fonctionnalités

### 1. Analyse d'Équipe
- **Classement et performance globale** : Statistiques de classement et indicateurs clés
- **Comparaison entre équipes** : Graphiques radar, boîtes à moustaches
- **Heatmaps** : Visualisation des zones d'actions de l'équipe
- **Corrélations statistiques** : Diagrammes de dispersion pour analyser les relations entre différentes métriques

### 2. Analyse de Joueurs
- **Profil du joueur** : Statistiques clés et profil de compétences
- **Comparaison intra-club et inter-club** : Graphiques radar, boîtes à moustaches
- **Suivi des performances dans le temps** : Graphiques en courbes, chronologie annotée
- **Analyse contextuelle** : Performance selon le contexte (domicile/extérieur, niveau d'adversaire, etc.)

### 3. Analyse Tactique
- **Analyse de possession** : Statistiques et heatmaps de possession
- **Analyse des passes** : Réseau de passes, types de passes, carte de chaleur
- **Analyse défensive** : Statistiques défensives, carte de chaleur, analyse de la pression
- **Analyse des transitions** : Visualisation des transitions défense-attaque

## Données

L'application utilise les données de StatsBomb pour fournir des analyses détaillées. Les données sont accessibles via la bibliothèque `statsbombpy`.

## Installation

1. Cloner ce dépôt
2. Installer les dépendances :
```bash
pip install streamlit matplotlib seaborn plotly pandas numpy statsbombpy
```
3. Lancer l'application :
```bash
streamlit run app.py
```

## Structure du Projet

- `app.py` : Point d'entrée de l'application
- `pages/` : Contient les différentes pages de l'application
  - `1_Analyse_Equipe.py` : Analyse d'équipe
  - `2_Analyse_Joueurs.py` : Analyse de joueurs
  - `2_Analyse_Joueurs_Avancee.py` : Analyse avancée de joueurs
  - `3_Analyse_Tactique.py` : Analyse tactique
  - `3_Analyse_Tactique_Avancee.py` : Analyse tactique avancée
- `utils/` : Contient les modules utilitaires
  - `data_loader.py` : Module de chargement des données

## Utilisation

1. Sélectionnez une compétition dans la barre latérale
2. Choisissez une équipe à analyser
3. Naviguez entre les différentes pages d'analyse à l'aide de la barre de navigation
4. Utilisez les filtres dans la barre latérale pour affiner votre analyse

## Remarques

- L'application utilise les données ouvertes de StatsBomb, qui peuvent être limitées. Pour une analyse plus complète, envisagez d'utiliser un abonnement complet à StatsBomb ou d'autres sources de données comme Wyscout ou Fbref.
- Certaines visualisations utilisent des données simulées lorsque les données réelles ne sont pas disponibles.

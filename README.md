# Lausanne Time Machine — HUM-460

Analyse spatiale des lieux de divertissement à Lausanne au XIXe siècle  
Groupe Mercator — EPFL Master

## Structure du projet
raw_data/ → Sources brutes (cadastre 1888, almanach 1832)
processed_data/ → Données filtrées et géocodées
filtrage_cadastre.py → Extraction des lieux de divertissement
geocodage.py → Géocodage initial via Nominatim
geocodage_v2.py → Géocodage des adresses historiques


## Fichiers lourds (non versionnés)
Les rasters géoréférencés (carte Payot 1900) dispo moodle

## Dépendances Python
```bash
pip install pandas geopandas geopy openpyxl
```
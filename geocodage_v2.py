# CORRECTIONS DES ADRESSES MANQUANTES 

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

df = pd.read_csv("processed_data/lieux_divertissement_geocodes.csv", encoding="utf-8-sig")

geolocator = Nominatim(user_agent="lausanne_time_machine_v2")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=5)

# Corrections manuelles des noms de rues historiques → noms actuels
CORRECTIONS = {
    "Rue du Pont":              "Rue Centrale, Lausanne, Switzerland",
    "Rue du Grand Pont":        "Rue Centrale, Lausanne, Switzerland",
    "Rue du Petit St-Jean":     "Rue Saint-Jean, Lausanne, Switzerland",
    "Rue du Grand St-Jean":     "Rue Saint-Jean, Lausanne, Switzerland",
    "Rue Cité Devant":          "Rue Cité-Devant, Lausanne, Switzerland",
    "Rue Cité Derrière":        "Rue Cité-Derrière, Lausanne, Switzerland",
    "Rue de la Louve":          "Rue de la Louve, Lausanne, Switzerland",
    "Ruelle du Grand Pont":     "Rue Centrale, Lausanne, Switzerland",
    "Place de Pépinet":         "Place Pépinet, Lausanne, Switzerland",
    "Route du Tunnel":          "Rue du Tunnel, Lausanne, Switzerland",
    "Rue des Deux Marchés":     "Rue des Deux-Marchés, Lausanne, Switzerland",
    "Rue Chaucrau":             "Rue Chaucrau, Lausanne, Switzerland",
    "Rue de la Cheneau de Bourg": "Rue de la Cheneau-de-Bourg, Lausanne, Switzerland",
    "Derrière Bourg":           "Rue Derrière-Bourg, Lausanne, Switzerland",
    "Escaliers des Petites Roches": "Lausanne, Switzerland",
    "Abbaye de l'Arc":          "Rue de l'Arc, Lausanne, Switzerland",
    "Sous Montbenon":           "Avenue de Montbenon, Lausanne, Switzerland",
    "Sur Montbenon":            "Avenue de Montbenon, Lausanne, Switzerland",
    "A Ouchy":                  "Ouchy, Lausanne, Switzerland",
    "A Beau Rivage":            "Ouchy, Lausanne, Switzerland",
    "En Chauderon":             "Chauderon, Lausanne, Switzerland",
    "Au Bugnon":                "Rue du Bugnon, Lausanne, Switzerland",
    "A la Ponthaise":           "Rue de la Ponthaise, Lausanne, Switzerland",
    "Le Maupas":                "Rue du Maupas, Lausanne, Switzerland",
    "A Beaulieu":               "Avenue de Beaulieu, Lausanne, Switzerland",
    "A la Sallaz":              "La Sallaz, Lausanne, Switzerland",
    "A Cour":                   "Cour, Lausanne, Switzerland",
}

non_trouves = df[df["lat"].isna()].copy()
print(f"Tentative sur {len(non_trouves)} adresses non trouvées...\n")

for idx, row in non_trouves.iterrows():
    nom_local = str(row["Noms locaux"]).strip()
    
    # Chercher une correction manuelle
    adresse_corrigee = None
    for ancien, nouveau in CORRECTIONS.items():
        if ancien.lower() in nom_local.lower():
            adresse_corrigee = nouveau
            break
    
    # Si pas de correction, retenter avec juste "Lausanne, Switzerland"
    if not adresse_corrigee:
        adresse_corrigee = f"{nom_local}, Lausanne, Switzerland"
    
    try:
        location = geocode(adresse_corrigee)
        if location:
            df.at[idx, "lat"] = location.latitude
            df.at[idx, "lon"] = location.longitude
            print(f"✅ '{nom_local}' → {adresse_corrigee}")
        else:
            print(f"❌ Toujours non trouvé : '{nom_local}'")
    except Exception as e:
        print(f"⚠️ Erreur : {nom_local} — {e}")

# Sauvegarder
df.to_csv("processed_data/lieux_divertissement_geocodes.csv", index=False, encoding="utf-8-sig")

trouves = df["lat"].notna().sum()
print(f"\n✅ Total géocodé : {trouves}/{len(df)}")

# Regénérer le GeoJSON
df_geo = df.dropna(subset=["lat", "lon"]).copy()
gdf = gpd.GeoDataFrame(
    df_geo,
    geometry=[Point(lon, lat) for lat, lon in zip(df_geo["lat"], df_geo["lon"])],
    crs="EPSG:4326"
)
gdf.to_file("processed_data/lieux_divertissement_1888.geojson", driver="GeoJSON")
print("✅ GeoJSON mis à jour")
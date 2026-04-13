import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Charger le CSV
df = pd.read_csv("processed_data/lieux_divertissement_cadastre_1888.csv", encoding="utf-8-sig")

# Initialiser Nominatim avec un délai de 1 seconde entre chaque requête
geolocator = Nominatim(user_agent="lausanne_time_machine_hum460")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=5)

lats, lons = [], []

for i, row in df.iterrows():
    adresse = str(row["adresse_complete"])
    try:
        location = geocode(adresse)
        if location:
            lats.append(location.latitude)
            lons.append(location.longitude)
            print(f"✅ {adresse} → {location.latitude:.4f}, {location.longitude:.4f}")
        else:
            lats.append(None)
            lons.append(None)
            print(f"❌ Non trouvé : {adresse}")
    except Exception as e:
        lats.append(None)
        lons.append(None)
        print(f"⚠️ Erreur : {adresse} — {e}")

df["lat"] = lats
df["lon"] = lons

# Sauvegarder CSV avec coordonnées
df.to_csv("processed_data/lieux_divertissement_geocodes.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ CSV exporté : {df['lat'].notna().sum()}/{len(df)} adresses géocodées")

# Exporter en GeoJSON directement lisible par QGIS
df_geo = df.dropna(subset=["lat", "lon"]).copy()
gdf = gpd.GeoDataFrame(
    df_geo,
    geometry=[Point(lon, lat) for lat, lon in zip(df_geo["lat"], df_geo["lon"])],
    crs="EPSG:4326"
)
gdf.to_file("processed_data/lieux_divertissement_1888.geojson", driver="GeoJSON")
print(f"✅ GeoJSON exporté → ouvrable directement dans QGIS")
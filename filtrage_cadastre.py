import pandas as pd
import re
from collections import Counter

# ─────────────────────────────────────────────
# 1. Chargement — header=0 : la ligne 0 EST l'en-tête
# ─────────────────────────────────────────────
FICHIER = "raw_data/cadastre_renove_1888.xlsx"

df = pd.read_excel(FICHIER, sheet_name="Feuil1", header=0)

print("Colonnes :", df.columns.tolist())
print(f"Lignes chargées : {len(df)}\n")

# ─────────────────────────────────────────────
# 2. Nettoyage de la colonne 'use'
# ─────────────────────────────────────────────
# La colonne s'appelle bien 'use' d'après l'aperçu
df["use"] = df["use"].fillna("").astype(str).str.strip()

# Décomposer les usages multiples séparés par virgule
# Ex: "Maison d'habitation, café, magasin" → 3 usages atomiques
all_uses_split = []
for cell in df["use"]:
    if cell:
        parts = [p.strip().lower() for p in cell.split(",") if p.strip()]
        all_uses_split.extend(parts)

# ─────────────────────────────────────────────
# 3. Inventaire complet de tous les usages distincts
# ─────────────────────────────────────────────
use_counter = Counter(all_uses_split)
use_df = pd.DataFrame(use_counter.most_common(), columns=["usage_atomique", "occurrences"])

print(f"{len(use_df)} usages distincts trouvés :\n")
print(use_df.to_string(index=False))

use_df.to_csv(
    "processed_data/tous_les_usages_cadastre_1888.csv",
    index=False,
    encoding="utf-8-sig"
)
print("\n✅ Exporté : processed_data/tous_les_usages_cadastre_1888.csv")

# ─────────────────────────────────────────────
# 4. Filtrage des usages liés au divertissement
# ─────────────────────────────────────────────
MOTS_CLES_DIVERTISSEMENT = [
    "café", "brasserie", "hôtel", "théâtre", "casino",
    "restaurant", "pinte", "cabaret", "concert", "salle",
    "guinguette", "estaminet", "débit de boissons", "auberge",
    "bal", "jeu", "spectacle"
]

pattern = "|".join(re.escape(m) for m in MOTS_CLES_DIVERTISSEMENT)

masque = df["use"].str.lower().str.contains(pattern, na=False)
df_divert = df[masque].copy()

# Filtrage d'exclusion
EXCLUSIONS = ["tribunal", "école", "chapelle", "bûcher", "scierie",
              "gymnastique", "épuration", "fenil", "machines", "pétrole"]
pattern_excl = "|".join(EXCLUSIONS)
df_divert = df_divert[~df_divert["use"].str.lower().str.contains(pattern_excl, na=False)]

print(f"\n{len(df_divert)} entrées liées au divertissement :\n")
print(df_divert[["folio", "nr", "Noms locaux", "use", "owner"]].to_string(index=False))

df_divert["ville"] = "Lausanne"
df_divert["pays"] = "Switzerland"
df_divert["adresse_complete"] = df_divert["Noms locaux"].str.strip() + ", Lausanne, Switzerland"

# Categorisation des lieux pour map QGIS differentes couleurs
def simplifier_type(use):
    use_lower = str(use).lower()
    if any(m in use_lower for m in ["hôtel", "hotel", "auberge"]):
        return "Hôtel"
    elif any(m in use_lower for m in ["brasserie"]):
        return "Brasserie"
    elif any(m in use_lower for m in ["pinte"]):
        return "Pinte"
    elif any(m in use_lower for m in ["café", "cafe"]):
        return "Café"
    else:
        return "Autre"

df_divert["type_simplifie"] = df_divert["use"].apply(simplifier_type)

df_divert.to_csv(
    "processed_data/lieux_divertissement_cadastre_1888.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n✅ Exporté : processed_data/lieux_divertissement_cadastre_1888.csv")
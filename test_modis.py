import ee
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

PROJECT_ID = os.getenv("EE_PROJECT_ID", "potent-airfoil-493212-f0")

def test_modis_retrieval():
    print(f"--- Debut du test MODIS ---")
    print(f"Project ID: {PROJECT_ID}")

    try:
        # 1. Initialisation
        print("Initialisation de Earth Engine...")
        ee.Initialize(project=PROJECT_ID)
        print("Succès : Earth Engine est initialisé.")

        # 2. Définition d'une zone (Marrakech)
        marrakech_geom = ee.Geometry.Point([-7.9811, 31.6295]).buffer(5000).bounds()
        
        # 3. Récupération d'une collection MODIS (LST Day)
        print("Récupération des données MODIS (MOD11A2)...")
        collection = (ee.ImageCollection("MODIS/061/MOD11A2")
                      .filterDate("2023-01-01", "2023-02-01")
                      .filterBounds(marrakech_geom))

        count = collection.size().getInfo()
        print(f"Nombre d'images trouvées : {count}")

        if count > 0:
            # Récupérer la moyenne pour la première image
            img = collection.first()
            date = ee.Date(img.get("system:time_start")).format("YYYY-MM-dd").getInfo()
            
            stats = img.select("LST_Day_1km").multiply(0.02).add(-273.15).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=marrakech_geom,
                scale=1000
            ).getInfo()

            print(f"Date de l'image : {date}")
            print(f"Température moyenne : {stats.get('LST_Day_1km')} °C")
            print("--- Test réussi ! ---")
        else:
            print("--- Test termine : Aucune donnée trouvée pour cette période. ---")

    except Exception as e:
        print("\n--- ERREUR DETECTEE ---")
        print(str(e))
        print("------------------------\n")
        print("CONSEIL : Si l'erreur est 'Not authenticated', lancez 'earthengine authenticate' dans votre terminal.")

if __name__ == "__main__":
    test_modis_retrieval()

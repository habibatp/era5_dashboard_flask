import os
import shutil
from pathlib import Path

def clean_temp_downloads():
    temp_dir = Path("temp_downloads")
    if temp_dir.exists():
        print(f"Nettoyage de {temp_dir}...")
        for item in temp_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                print(f"Supprimé: {item.name}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {item.name}: {e}")
    else:
        print("Dossier temp_downloads introuvable.")

def clean_cache():
    cache_dir = Path("cache_data")
    if cache_dir.exists():
        print(f"Nettoyage de {cache_dir}...")
        for item in cache_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                print(f"Supprimé: {item.name}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {item.name}: {e}")
    else:
        print("Dossier cache_data introuvable.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if "temp" in sys.argv:
            clean_temp_downloads()
        if "cache" in sys.argv:
            clean_cache()
    else:
        clean_temp_downloads()

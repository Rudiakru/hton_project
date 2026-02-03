import os
from dotenv import load_dotenv
from pathlib import Path

# Basis-Verzeichnis des Projekts
BASE_DIR = Path(__file__).resolve().parent.parent

# .env laden
load_dotenv(BASE_DIR / '.env')

class Config:
    GRID_API_KEY = os.getenv('GRID_API_KEY')
    # Die korrekte Basis-URL für den Open Access (OP) Endpunkt
    GRID_BASE_URL = "https://api-op.grid.gg/live-data-feed/series-state/graphql"
    # Fallback/Alternative URLs (für Recherche/andere Pakete)
    GRID_CENTRAL_DATA_URL = "https://api-op.grid.gg/central-data/graphql"
    
    DATA_RAW_DIR = BASE_DIR / 'data' / 'raw'

    @classmethod
    def ensure_data_dirs(cls):
        # Sicherstellen, dass das Datenverzeichnis existiert
        cls.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls, require_api_key: bool = True):
        """Validiert die Konfiguration.

        Wichtig: Diese Validierung ist absichtlich NICHT mehr import-time.
        Tests/CI sollen das Modul importieren können, ohne dass zwingend
        ein echter API-Key vorhanden ist.
        """
        cls.ensure_data_dirs()

        if require_api_key and not cls.GRID_API_KEY:
            raise ValueError('GRID_API_KEY ist nicht in der .env Datei gesetzt.')

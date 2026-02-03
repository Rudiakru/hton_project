from typing import Dict
from .config import Config

class GridAuth:
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Generiert die Header für die GRID-API Kommunikation."""
        Config.validate(require_api_key=True)
        return {
            "x-api-key": Config.GRID_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

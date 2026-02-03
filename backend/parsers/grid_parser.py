import json
import os

def load_grid_data(filepath):
    """
    Lädt die GRID-Daten mit robustem Error-Handling.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Datei {filepath} nicht gefunden.")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basis-Validierung der GRID-Struktur
            if "data" not in data or "seriesState" not in data["data"]:
                raise ValueError("Ungültiges GRID JSON Format: 'data.seriesState' fehlt.")
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Fehler beim Parsen der JSON-Datei: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Unerwarteter Fehler beim Laden der Daten: {e}")

def extract_player_positions(game_data):
    """
    Extrahiert Spielerpositionen aus einem Game-Snapshot.
    """
    teams_data = []
    teams = game_data.get("teams", [])
    
    for t_idx, team in enumerate(teams):
        players = []
        for p in team.get("players", []):
            pos = p.get("position")
            is_alive = p.get("alive", True)
            
            # Nur Spieler mit gültigen Koordinaten extrahieren
            if pos and pos.get("x") is not None and pos.get("y") is not None:
                players.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "x": float(pos["x"]),
                    "y": float(pos["y"]),
                    "alive": bool(is_alive)
                })
        teams_data.append(players)
    
    return teams_data

def extract_events(game_data):
    """
    Extrahiert Events (Kills, Deaths, Objectives).
    """
    return game_data.get("events", [])

if __name__ == "__main__":
    # Test-Aufruf
    try:
        data = load_grid_data("data/raw/real_data.json")
        game = data["data"]["seriesState"]["games"][0]
        pos = extract_player_positions(game)
        print(f"Erfolgreich {len(pos[0]) + len(pos[1])} Spielerpositionen extrahiert.")
    except Exception as e:
        print(f"Fehler: {e}")

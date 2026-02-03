import asyncio
import sys
import logging
from typing import List
from core.client import GridClient
from core.schemas import SeriesData, Player

# Logging Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ValidationAgent")

async def validate_series_data(data: SeriesData):
    """Führt die geforderten Validierungen durch."""
    logger.info("--- Starte Daten-Validierung ---")
    
    if not data.frames:
        logger.warning("Keine Frames in den Daten gefunden!")
        return

    total_frames = len(data.frames)
    frames_with_10_players = 0
    frames_with_valid_coords = 0
    event_types = set()

    for frame in data.frames:
        # Check 1: 10 Spieler vorhanden?
        players: List[Player] = frame.players
        if len(players) == 10:
            frames_with_10_players += 1
        else:
            logger.warning(f"Frame bei {frame.matchTime}s hat {len(players)} Spieler statt 10.")

        # Check 2: Valide Koordinaten für lebende Spieler?
        valid_players = 0
        for p in players:
            if p.isAlive:
                if p.position and p.position.x is not None and p.position.y is not None:
                    valid_players += 1
                else:
                    logger.debug(f"Spieler {p.playerId} ist am Leben, hat aber keine Koordinaten.")
        
        if valid_players == len([p for p in players if p.isAlive]):
            frames_with_valid_coords += 1

    # Check 3: Datenfrequenz
    if total_frames > 1:
        match_duration = data.frames[-1].matchTime - data.frames[0].matchTime
        if match_duration > 0:
            fps = total_frames / match_duration
            logger.info(f"Datenfrequenz: {fps:.2f} Frames pro Sekunde (Über {match_duration:.2f}s)")
        else:
            logger.info("Match-Dauer konnte nicht berechnet werden (nur 1 Zeitstempel).")

    # Event Zusammenfassung
    for event in data.events:
        event_types.add(event.type)

    logger.info(f"Gesamtanzahl Frames: {total_frames}")
    logger.info(f"Frames mit 10 Spielern: {frames_with_10_players} ({frames_with_10_players/total_frames*100:.1f}%)")
    logger.info(f"Frames mit validen Koordinaten (lebende Spieler): {frames_with_valid_coords} ({frames_with_valid_coords/total_frames*100:.1f}%)")
    logger.info(f"Gefundene Event-Typen: {', '.join(event_types) if event_types else 'Keine'}")
    logger.info("--- Validierung abgeschlossen ---")

async def main():
    if len(sys.argv) < 2:
        logger.error("Bitte eine Series-ID angeben: python ingest_and_validate.py <series_id>")
        return

    series_id = sys.argv[1]
    client = GridClient()
    
    try:
        data = await client.fetch_match_data(series_id)
        if data:
            await validate_series_data(data)
        else:
            logger.error("Abruf der Daten fehlgeschlagen.")
    except Exception as e:
        logger.exception(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    asyncio.run(main())


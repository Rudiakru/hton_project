import asyncio
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from .auth import GridAuth
from .config import Config
from .schemas import GameFrame, GameEvent, SeriesData

logger = logging.getLogger(__name__)

class GridClient:
    def __init__(self, base_url: str = Config.GRID_BASE_URL):
        self.base_url = base_url
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.max_retries = 5
        
    async def fetch_match_data(self, series_id: str) -> Optional[SeriesData]:
        """
        Ruft sowohl den Series State (Frames) als auch die Events ab.
        """
        logger.info(f"Starte Datenabruf für Series {series_id}...")
        
        state_data = await self._fetch_with_retry(f"{self.base_url}/{series_id}/state")
        events_data = await self._fetch_with_retry(f"{self.base_url}/{series_id}/events")
        
        if not state_data:
            logger.error(f"Konnte State-Daten für {series_id} nicht abrufen.")
            return None

        # Wir bauen das SeriesData Objekt zusammen
        # Hinweis: Die Struktur der GRID Antwort kann variieren, wir versuchen sie robust zu mappen
        try:
            # Beispielhafte Extraktion der Frames aus dem State
            # GRID API State enthält oft 'gameState' mit 'players' etc.
            # Hier müssen wir eventuell das Mapping anpassen je nach exakter GRID-Response
            
            frames = []
            if 'gameState' in state_data:
                # Da state oft nur den AKTUELLEN Stand liefert, behandeln wir ihn hier als einen Frame
                # In einer echten Pipeline würde man den Stream pollen oder Webhooks nutzen.
                frames.append(GameFrame(
                    timestamp=state_data['gameState'].get('timestamp', datetime.now().isoformat()),
                    matchTime=state_data['gameState'].get('matchTime', 0.0),
                    players=state_data['gameState'].get('players', [])
                ))
            
            events = []
            if events_data and 'events' in events_data:
                for ev in events_data['events']:
                    events.append(GameEvent(
                        type=ev.get('type', 'unknown'),
                        timestamp=ev.get('occurredAt', ''),
                        payload=ev.get('payload', {})
                    ))

            series_data = SeriesData(
                seriesId=series_id,
                frames=frames,
                events=events
            )
            
            # Speichern als Roh-JSONL
            await self._save_to_jsonl(series_id, series_data)
            
            return series_data
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen der GRID Daten für {series_id}: {e}")
            return None

    async def _fetch_with_retry(self, url: str) -> Optional[Dict[str, Any]]:
        headers = GridAuth.get_headers()
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 429:
                        wait_time = (2 ** attempt) + 1 # Exponential Backoff
                        logger.warning(f"Rate Limit (429). Warte {wait_time}s (Versuch {attempt+1}/{self.max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Fehler {e.response.status_code} für {url}")
                if e.response.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue
                break
            except Exception as e:
                logger.error(f"Netzwerkfehler bei {url}: {e}")
                await asyncio.sleep(2 ** attempt)
                continue
        
        return None

    async def _save_to_jsonl(self, series_id: str, data: SeriesData):
        Config.ensure_data_dirs()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Config.DATA_RAW_DIR / f"{series_id}_{timestamp}.jsonl"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Wir speichern das gesamte Modell als eine Zeile (JSONL Style für ein Objekt)
                # In einer echten Pipeline pro Frame eine Zeile.
                f.write(data.json() + "\n")
            logger.info(f"Rohdaten gespeichert unter: {filename}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der JSONL Datei: {e}")

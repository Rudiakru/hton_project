import asyncio
import httpx
import os
from dotenv import load_dotenv

async def test_ids():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    ids = ['100', '101', '50', '150', '28']
    
    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }
    
    print("--- Teste 'Public' GRID IDs ---")
    async with httpx.AsyncClient(timeout=5.0) as client:
        for sid in ids:
            url = f'https://api-op.grid.gg/live-data-feed/v1/series/{sid}/state'
            try:
                response = await client.get(url, headers=headers)
                print(f'ID {sid:3} | Status: {response.status_code}')
                if response.status_code == 200:
                    print(f'      -> ERFOLG! {sid} ist erreichbar.')
            except Exception as e:
                print(f'ID {sid:3} | Fehler: {e}')

if __name__ == "__main__":
    asyncio.run(test_ids())


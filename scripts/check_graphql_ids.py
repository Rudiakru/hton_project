import httpx
import os
from dotenv import load_dotenv

def check_series_exists(series_id):
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    url = 'https://api-op.grid.gg/central-data/graphql'
    
    query = """
    query GetSeries($id: ID!) {
      series(id: $id) {
        id
      }
    }
    """
    variables = {"id": series_id}
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}

    try:
        response = httpx.post(url, json={'query': query, 'variables': variables}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                return False, data['errors']
            return True, data.get('data', {}).get('series')
        return False, response.text
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    for test_id in ["1", "2", "28", "100"]:
        success, result = check_series_exists(test_id)
        print(f"ID {test_id}: Success={success}, Result={result}")

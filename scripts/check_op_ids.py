import httpx
import os
from dotenv import load_dotenv
load_dotenv()

def check_op_id(series_id):
    api_key = os.getenv("GRID_API_KEY")
    url = "https://api-op.grid.gg/central-data/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    query = """
    query GetSeries($id: ID!) {
      series(id: $id) {
        id
        title {
          name
        }
      }
    }
    """
    variables = {"id": series_id}
    
    with httpx.Client() as client:
        try:
            r = client.post(url, headers=headers, json={"query": query, "variables": variables})
            print(f"ID {series_id} | Status {r.status_code} | Response: {r.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    for sid in ["1", "2", "28"]:
        check_op_id(sid)


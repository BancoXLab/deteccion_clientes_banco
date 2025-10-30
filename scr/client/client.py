import requests
from typing import Any, Dict

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base = base_url.rstrip("/")

    def predict(self, payload: Dict[str, Any], timeout: int = 10):
        url = f"{self.base}/predict"
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

if __name__ == "__main__":
    c = APIClient()
    sample = {"features": [0,1,2]}
    print(c.predict(sample))
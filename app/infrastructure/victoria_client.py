import httpx
from datetime import datetime
from typing import Dict , Any , List
from app.core.config import settings

class VictoriaMetricsClient:
    def __init__(self) -> None:
        self.base_url = f"{settings.VICTORIA_URL}/api/v1"
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def get_metrics_range(self, query:str, start_time:datetime, end_time:datetime, step:str) -> List[Dict[str, Any]]:
        """ Fetches range date from VictoriaMetrics"""

        endpoint = f"{self.base_url}/query_range"
        params = {"query":query,
        "start":int(start_time.timestamp()),
        "end":int(end_time.timestamp()),
        "step":step}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                request = client.build_request("GET", endpoint,params=params)
                print(f"[VM FETCH]:{request.url}")

                response = await client.send(request)
                response.raise_for_status()

                data = response.json()

                if data.get("status") == "success":
                    return data.get("data", {}).get("result",[])
                return []
            except httpx.HTTPStatusError as e:
                print(f"VM Query Error ({e.response.status_code}):{e.response.text}")
                return []
            except Exception as e:
                print(f"VM Query Error: {str(e)}")
                return []
"""Optional official data connectors. Nothing is treated as live until configured and verified."""
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def get_ogd_mandi_prices(api_key: str, resource_id: str, base_url: str, *, state="", commodity="", limit=25):
    if not api_key or not resource_id:
        return {"available": False, "status": "not_configured", "records": [],
                "message": "Add an authorised data.gov.in API key and the exact resource ID from the official dataset API tab."}
    params = {"api-key": api_key, "format": "json", "resource_id": resource_id,
              "limit": max(1, min(int(limit), 100))}
    if state:
        params["filters[state]"] = state[:80]
    if commodity:
        params["filters[commodity]"] = commodity[:100]
    url = base_url.rstrip("?") + "?" + urlencode(params)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "FARM-BRAIN/1.0"})
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read(2_000_000).decode("utf-8"))
        records = payload.get("records", []) if isinstance(payload, dict) else []
        return {"available": True, "status": "live", "records": records,
                "message": "Data returned by the configured Open Government Data endpoint.",
                "count": len(records), "retrieved_at": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:  # external providers can be temporarily unavailable
        return {"available": False, "status": "provider_unavailable", "records": [],
                "message": f"The configured mandi data endpoint did not return usable data ({type(exc).__name__}). Try again later."}

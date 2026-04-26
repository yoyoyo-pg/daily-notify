import requests

_URL = "https://wttr.in/Nagoya?format=j1&lang=ja"
_LINK = "https://wttr.in/Nagoya"


def get_weather() -> dict:
    resp = requests.get(_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current_condition"][0]
    today = data["weather"][0]
    hourly = today["hourly"]
    precip_prob = max(int(h.get("chanceofrain", 0)) for h in hourly)

    return {
        "desc": current["weatherDesc"][0]["value"],
        "temp": current["temp_C"],
        "temp_max": today["maxtempC"],
        "temp_min": today["mintempC"],
        "precip_prob": precip_prob,
        "url": _LINK,
    }

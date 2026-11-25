import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote


def config_value(name, default=""):
    value = os.getenv(name) or os.getenv(name.upper())
    if value:
        return value.strip().strip('"').strip("'")

    env_file = Path(__file__).with_name(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if key.strip() == name:
                    return val.strip().strip('"').strip("'")
    return default


def get_request(endpoint):
    base = config_value("backend_url", "http://127.0.0.1:3030").rstrip("/")
    url = base + "/" + quote(endpoint.lstrip("/"), safe="/")
    with urlopen(Request(url), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_request(endpoint, payload):
    base = config_value("backend_url", "http://127.0.0.1:3030").rstrip("/")
    url = base + "/" + endpoint.lstrip("/")
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def analyze_review_sentiments(text):
    base = config_value("sentiment_analyzer_url").rstrip("/")
    if not base or "your code engine" in base.lower():
        raise RuntimeError("Configure sentiment_analyzer_url in djangoapp/.env")

    url = base + "/analyze/" + quote(text, safe="")
    with urlopen(Request(url), timeout=30) as response:
        raw = response.read().decode("utf-8")

    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            sentiment = result.get("sentiment", result.get("label", result))
            if isinstance(sentiment, dict):
                sentiment = sentiment.get("document", {}).get(
                    "label", sentiment.get("label", "unknown")
                )
            return str(sentiment).lower()
        return str(result).lower()
    except json.JSONDecodeError:
        return raw.strip().lower()

"""One model setting and predictable local/parent dotenv discovery."""

from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
load_dotenv(ROOT.parent / ".env", override=False)
# Explicit workspace model choice. Course brief requires Luna on the course key; see README.
MODEL_NAME = "gpt-6-astra"
RUNTIME = Path(os.getenv("PIVOT_DATA_DIR", str(ROOT / "runtime")))
RUNTIME.mkdir(parents=True, exist_ok=True)
RUNTIME.chmod(0o700)
API_TIMEOUT = 60
RUN_TIMEOUT = 100
REQUEST_LIMIT = 3
TOKEN_LIMIT = 24000
OUTPUT_LIMIT = 2600
DAILY_AI_CALLS = 40
DAILY_TOKEN_LIMIT = 300000
PRICES = {
    "input_per_million": 10.0,
    "cached_input_per_million": 1.0,
    "output_per_million": 50.0,
}
PRICE_SOURCE = "https://developers.openai.com/api/docs/models/gpt-6-astra"
PRICE_CHECKED = "2026-10-25"


def key_status():
    return bool(os.getenv("PORTKEY_API_KEY") or os.getenv("OPENAI_API_KEY"))

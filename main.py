"""
Dinari sandbox quickstart.

Loads your sandbox API credentials from a .env file, connects to the Dinari
sandbox environment, and makes a couple of read-only calls to confirm the
connection works.

Docs: https://docs.dinari.com/docs/quickstart
"""

import os
import sys

from dotenv import load_dotenv

from dinari_api_sdk import Dinari

# Load DINARI_API_KEY_ID / DINARI_API_SECRET_KEY from .env into the environment.
load_dotenv()

api_key_id = os.environ.get("DINARI_API_KEY_ID")
api_secret_key = os.environ.get("DINARI_API_SECRET_KEY")

if not api_key_id or not api_secret_key:
    sys.exit(
        "Missing credentials. Copy .env.example to .env and fill in "
        "DINARI_API_KEY_ID and DINARI_API_SECRET_KEY (generate them at "
        "partners.dinari.com with the Sandbox environment selected)."
    )

# environment="sandbox" points the client at the Dinari sandbox instead of
# production (production is the default if you omit it).
client = Dinari(
    api_key_id=api_key_id,
    api_secret_key=api_secret_key,
    environment="sandbox",
)


def main() -> None:
    print("Connected to Dinari sandbox.\n")

    # List a few tokenized stocks available through the API.
    result = client.v2.market_data.stocks.list()

    # Depending on the SDK version, .list() returns either a response object
    # with a `.data` attribute or the list of stocks directly. Handle both.
    stocks = result.data if hasattr(result, "data") else list(result)

    print(f"Fetched {len(stocks)} stocks. First few:")
    for stock in stocks[:5]:
        # Attributes vary by stock; print the common ones defensively.
        symbol = getattr(stock, "symbol", "?")
        name = getattr(stock, "name", "")
        print(f"  - {symbol}: {name}")


if __name__ == "__main__":
    main()

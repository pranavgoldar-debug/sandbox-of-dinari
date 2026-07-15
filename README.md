# Dinari Sandbox

A minimal Python sandbox for the [Dinari API](https://docs.dinari.com/docs/quickstart),
configured to run against the **sandbox** environment.

## 1. Get your sandbox API keys

1. Log in at [partners.dinari.com](https://partners.dinari.com).
2. On the home page, **select the Sandbox environment**.
3. Generate an API key and copy the **API Key ID** and **API Secret Key**.

## 2. Set up

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your credentials
cp .env.example .env
# then edit .env and paste your API Key ID and Secret Key
```

Your `.env` is git-ignored, so your credentials never get committed.

## 3. Run

```bash
python main.py
```

You should see a confirmation that the client connected to the sandbox and a
short list of tokenized stocks.

## Web dashboard (localhost)

Prefer a browser over the terminal? Run the local dashboard:

```bash
python app.py
```

Then open **http://localhost:5001** in your browser. It shows your entity,
accounts, cash balances, portfolio, and available stocks — pulled live from the
sandbox each time you refresh. Press `Ctrl+C` in the terminal to stop it.

## What's inside

| File | Purpose |
| --- | --- |
| `app.py` | Local web dashboard at http://localhost:5001 |
| `main.py` | Quickstart: connects to the sandbox and lists stocks (read-only) |
| `create_account.py` | Creates an entity + account, prints their IDs |
| `requirements.txt` | `dinari-api-sdk`, `python-dotenv`, `flask` |
| `.env.example` | Template for your credentials — copy to `.env` |
| `.gitignore` | Keeps `.env` and Python artifacts out of git |

## Create an entity and account

Once `main.py` works, run:

```bash
python create_account.py
```

This creates an **entity** (the account holder) and an **account** under it,
then prints their IDs. Refresh [partners.dinari.com/home](https://partners.dinari.com/home)
(with the Sandbox environment selected) and you'll see them appear.

## Next steps

The client exposes the full API under `client.v2`. A few things to explore
(see the [docs](https://docs.dinari.com/)):

- `client.v2.entities.create(name=...)` — create an entity (account)
- `client.v2.market_data.stocks.list()` — list available stocks
- KYC and wallet management — see the
  [quickstart guide](https://docs.dinari.com/docs/quickstart)

## Going to production

When you're ready, generate **production** keys at partners.dinari.com and
remove `environment="sandbox"` from the client in `main.py` (production is the
default).

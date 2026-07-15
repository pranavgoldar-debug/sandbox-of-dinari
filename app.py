"""
Dinari sandbox — local web dashboard.

Run it:

    python app.py

Then open the link it prints (http://localhost:5001) in your browser.

The page connects to the Dinari sandbox with the credentials in your .env file
and shows your entity, accounts (with wallets & balances), and available stocks.
Each section fails independently, so if one call errors the rest still render.

Docs: https://docs.dinari.com/docs/quickstart
"""

import os

from dotenv import load_dotenv
from flask import Flask, render_template_string

from dinari_api_sdk import Dinari

load_dotenv()

API_KEY_ID = os.environ.get("DINARI_API_KEY_ID")
API_SECRET_KEY = os.environ.get("DINARI_API_SECRET_KEY")

app = Flask(__name__)


def get_client() -> Dinari:
    return Dinari(
        api_key_id=API_KEY_ID,
        api_secret_key=API_SECRET_KEY,
        environment="sandbox",
    )


def as_list(result):
    """SDK responses come back as a plain list, an object with `.data`, or an
    object with `.assets`. Normalize any of them to a plain list."""
    if result is None:
        return []
    if hasattr(result, "data"):
        return list(result.data)
    if hasattr(result, "assets"):
        return list(result.assets)
    return list(result)


def gather():
    """Collect everything the dashboard shows. Every section is wrapped so a
    single failing API call doesn't blank the whole page."""
    data = {"errors": {}, "connected": False}

    if not API_KEY_ID or not API_SECRET_KEY:
        data["errors"]["credentials"] = (
            "Missing credentials. Add DINARI_API_KEY_ID and "
            "DINARI_API_SECRET_KEY to your .env file, then restart."
        )
        return data

    try:
        client = get_client()
    except Exception as exc:  # noqa: BLE001
        data["errors"]["client"] = f"Could not build client: {exc}"
        return data

    # Entity
    entity = None
    try:
        entity = client.v2.entities.retrieve_current()
        data["entity"] = entity
        data["connected"] = True
    except Exception as exc:  # noqa: BLE001
        data["errors"]["entity"] = str(exc)

    # Accounts under the entity
    data["accounts"] = []
    if entity is not None:
        try:
            data["accounts"] = as_list(
                client.v2.entities.accounts.list(entity_id=entity.id)
            )
        except Exception as exc:  # noqa: BLE001
            data["errors"]["accounts"] = str(exc)

    # Balances + portfolio for the first account
    data["cash"] = []
    data["portfolio"] = []
    if data["accounts"]:
        acct_id = data["accounts"][0].id
        data["primary_account_id"] = acct_id
        try:
            data["cash"] = as_list(client.v2.accounts.get_cash_balances(acct_id))
        except Exception as exc:  # noqa: BLE001
            data["errors"]["cash"] = str(exc)
        try:
            data["portfolio"] = as_list(client.v2.accounts.get_portfolio(acct_id))
        except Exception as exc:  # noqa: BLE001
            data["errors"]["portfolio"] = str(exc)

    # Market data — available stocks
    data["stocks"] = []
    try:
        data["stocks"] = as_list(client.v2.market_data.stocks.list())
    except Exception as exc:  # noqa: BLE001
        data["errors"]["stocks"] = str(exc)

    return data


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dinari Sandbox Dashboard</title>
  <style>
    :root { color-scheme: light dark; }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           margin: 0; background: #0d1117; color: #e6edf3; }
    header { background: #0b3d2e; padding: 20px 32px; display: flex;
             align-items: center; gap: 16px; }
    header h1 { margin: 0; font-size: 20px; letter-spacing: 1px; }
    .badge { background: #1f6feb; color: #fff; padding: 3px 10px; border-radius: 999px;
             font-size: 12px; font-weight: 600; }
    .badge.ok { background: #238636; }
    .badge.err { background: #da3633; }
    main { max-width: 1000px; margin: 0 auto; padding: 24px 32px 64px; }
    section { background: #161b22; border: 1px solid #30363d; border-radius: 12px;
              padding: 20px 24px; margin-bottom: 20px; }
    section h2 { margin: 0 0 14px; font-size: 15px; text-transform: uppercase;
                 letter-spacing: 1px; color: #7d8590; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #21262d; }
    th { color: #7d8590; font-weight: 600; font-size: 12px; text-transform: uppercase; }
    code { background: #21262d; padding: 2px 6px; border-radius: 5px; font-size: 13px; }
    .kv { display: grid; grid-template-columns: 160px 1fr; gap: 8px 16px; font-size: 14px; }
    .kv div:nth-child(odd) { color: #7d8590; }
    .err { background: #2d1416; border: 1px solid #da3633; color: #ffb3b0;
           padding: 12px 16px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
    .muted { color: #7d8590; font-size: 13px; }
    .pill { padding: 2px 8px; border-radius: 999px; font-size: 12px; }
    .pill.yes { background: #172f1c; color: #3fb950; }
    .pill.no { background: #2d2117; color: #d29922; }
    a { color: #58a6ff; }
    .refresh { margin-left: auto; font-size: 13px; }
  </style>
</head>
<body>
  <header>
    <h1>DINARI · SANDBOX</h1>
    {% if data.connected %}
      <span class="badge ok">Connected</span>
    {% else %}
      <span class="badge err">Not connected</span>
    {% endif %}
    <a class="refresh" href="/">↻ Refresh</a>
  </header>
  <main>

    {% if data.errors.credentials %}
      <div class="err">{{ data.errors.credentials }}</div>
    {% endif %}
    {% if data.errors.client %}
      <div class="err">{{ data.errors.client }}</div>
    {% endif %}

    <section>
      <h2>Entity</h2>
      {% if data.entity %}
        <div class="kv">
          <div>Name</div><div>{{ data.entity.name }}</div>
          <div>Entity ID</div><div><code>{{ data.entity.id }}</code></div>
          <div>Type</div><div>{{ data.entity.entity_type or "—" }}</div>
          <div>KYC complete</div>
          <div>
            {% if data.entity.is_kyc_complete %}
              <span class="pill yes">Yes</span>
            {% else %}
              <span class="pill no">No</span>
            {% endif %}
          </div>
        </div>
      {% elif data.errors.entity %}
        <div class="err">{{ data.errors.entity }}</div>
      {% else %}
        <p class="muted">No entity data.</p>
      {% endif %}
    </section>

    <section>
      <h2>Accounts</h2>
      {% if data.accounts %}
        <table>
          <tr><th>Account ID</th><th>Active</th><th>Created</th></tr>
          {% for a in data.accounts %}
            <tr>
              <td><code>{{ a.id }}</code></td>
              <td>{% if a.is_active %}<span class="pill yes">Active</span>{% else %}<span class="pill no">Inactive</span>{% endif %}</td>
              <td class="muted">{{ a.created_dt or "—" }}</td>
            </tr>
          {% endfor %}
        </table>
      {% elif data.errors.accounts %}
        <div class="err">{{ data.errors.accounts }}</div>
      {% else %}
        <p class="muted">No accounts found for this entity.</p>
      {% endif %}
    </section>

    <section>
      <h2>Cash balances{% if data.primary_account_id %} · <span class="muted">{{ data.primary_account_id }}</span>{% endif %}</h2>
      {% if data.cash %}
        <table>
          <tr><th>Symbol</th><th>Amount</th><th>Chain</th></tr>
          {% for c in data.cash %}
            <tr><td>{{ c.symbol }}</td><td>{{ c.amount }}</td><td class="muted">{{ c.chain_id }}</td></tr>
          {% endfor %}
        </table>
      {% elif data.errors.cash %}
        <div class="err">{{ data.errors.cash }}</div>
      {% else %}
        <p class="muted">No cash balances yet. (Fund the account with sandbox tokens to see balances.)</p>
      {% endif %}
    </section>

    <section>
      <h2>Portfolio (owned stocks)</h2>
      {% if data.portfolio %}
        <table>
          <tr><th>Symbol</th><th>Amount</th><th>Stock ID</th></tr>
          {% for p in data.portfolio %}
            <tr><td>{{ p.symbol }}</td><td>{{ p.amount }}</td><td class="muted"><code>{{ p.stock_id }}</code></td></tr>
          {% endfor %}
        </table>
      {% elif data.errors.portfolio %}
        <div class="err">{{ data.errors.portfolio }}</div>
      {% else %}
        <p class="muted">No stock holdings yet.</p>
      {% endif %}
    </section>

    <section>
      <h2>Available stocks ({{ data.stocks|length }})</h2>
      {% if data.stocks %}
        <table>
          <tr><th>Symbol</th><th>Name</th><th>Tradable</th></tr>
          {% for s in data.stocks[:25] %}
            <tr>
              <td><strong>{{ s.symbol }}</strong></td>
              <td>{{ s.name }}</td>
              <td>{% if s.is_tradable %}<span class="pill yes">Yes</span>{% else %}<span class="pill no">No</span>{% endif %}</td>
            </tr>
          {% endfor %}
        </table>
        {% if data.stocks|length > 25 %}<p class="muted">Showing first 25 of {{ data.stocks|length }}.</p>{% endif %}
      {% elif data.errors.stocks %}
        <div class="err">{{ data.errors.stocks }}</div>
      {% else %}
        <p class="muted">No stocks returned.</p>
      {% endif %}
    </section>

    <p class="muted">Environment: <strong>sandbox</strong> · Data pulled live from
      the Dinari API each time you refresh.</p>
  </main>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, data=gather())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    print(f"\n  Dinari sandbox dashboard running at:  http://localhost:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=False)

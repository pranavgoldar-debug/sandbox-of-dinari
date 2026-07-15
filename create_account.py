"""
Dinari sandbox: create an entity and an account.

This is Step 2 of the Dinari flow. It:
  1. Creates an "entity" (an account holder — a person or business).
  2. Creates an "account" under that entity (which will hold funds & tokens).
  3. Prints the IDs so you can match them against your dashboard at
     https://partners.dinari.com/home (with the Sandbox environment selected).

Run it with:  python create_account.py

Docs: https://docs.dinari.com/docs/quickstart
"""

import os
import sys

from dotenv import load_dotenv

from dinari_api_sdk import Dinari

load_dotenv()

api_key_id = os.environ.get("DINARI_API_KEY_ID")
api_secret_key = os.environ.get("DINARI_API_SECRET_KEY")

if not api_key_id or not api_secret_key:
    sys.exit(
        "Missing credentials. Make sure your .env file has DINARI_API_KEY_ID "
        "and DINARI_API_SECRET_KEY set."
    )

client = Dinari(
    api_key_id=api_key_id,
    api_secret_key=api_secret_key,
    environment="sandbox",
)


def main() -> None:
    print("Connected to Dinari sandbox.\n")

    # 1. Create an entity (the account holder). The name is just a label in
    #    sandbox; in production this ties to a real, KYC-verified person/business.
    entity = client.v2.entities.create(name="Test Entity - Sandbox")
    print("Created entity:")
    print(f"  id:              {entity.id}")
    print(f"  name:            {entity.name}")
    print(f"  entity_type:     {getattr(entity, 'entity_type', None)}")
    print(f"  is_kyc_complete: {getattr(entity, 'is_kyc_complete', None)}")
    print()

    # 2. Create an account under that entity. The account is what actually holds
    #    cash and tokenized stocks and places orders.
    account = client.v2.entities.accounts.create(entity_id=entity.id)
    print("Created account:")
    print(f"  id:          {account.id}")
    print(f"  entity_id:   {account.entity_id}")
    print(f"  is_active:   {getattr(account, 'is_active', None)}")
    print(f"  created_dt:  {getattr(account, 'created_dt', None)}")
    print()

    print("Done. Refresh https://partners.dinari.com/home (Sandbox) to see them.")
    print(f"\nSave this account ID for later steps: {account.id}")


if __name__ == "__main__":
    main()

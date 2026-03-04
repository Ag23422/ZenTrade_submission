import json
import os

REGISTRY = "registry/account_registry.json"


def load_registry():

    if not os.path.exists(REGISTRY):
        return {"processed_accounts": []}

    with open(REGISTRY) as f:
        return json.load(f)


def save_registry(data):

    with open(REGISTRY, "w") as f:
        json.dump(data, f, indent=2)


def account_seen(account_id):

    reg = load_registry()
    return account_id in reg["processed_accounts"]


def register_account(account_id):

    reg = load_registry()

    if account_id not in reg["processed_accounts"]:
        reg["processed_accounts"].append(account_id)

    save_registry(reg)

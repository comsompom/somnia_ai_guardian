import json
from pathlib import Path

from web3 import Web3

from agent.config import get_settings


def main() -> None:
    cfg = get_settings()
    if not cfg.vault_address:
        raise ValueError("VAULT_ADDRESS is missing in .env")

    artifact = json.loads(Path("build/mock_vault_artifact.json").read_text(encoding="utf-8"))
    w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    contract = w3.eth.contract(address=cfg.vault_address, abi=artifact["abi"])
    health = contract.functions.health().call()
    last_attack = contract.functions.lastAttackTimestamp().call()
    print(f"health={health}")
    print(f"lastAttackTimestamp={last_attack}")


if __name__ == "__main__":
    main()

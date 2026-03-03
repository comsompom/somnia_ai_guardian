import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web3 import Web3

from agent.config import get_settings

ARTIFACT_FILE = PROJECT_ROOT / "build" / "mock_vault_artifact.json"


def main() -> None:
    cfg = get_settings()
    if not cfg.vault_address:
        raise ValueError("VAULT_ADDRESS is missing in .env")
    if not ARTIFACT_FILE.exists():
        raise FileNotFoundError(
            f"Artifact not found at {ARTIFACT_FILE}. Run deploy first: python scripts/deploy.py"
        )

    artifact = json.loads(ARTIFACT_FILE.read_text(encoding="utf-8"))
    w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    contract = w3.eth.contract(address=cfg.vault_address, abi=artifact["abi"])
    health = contract.functions.health().call()
    last_attack = contract.functions.lastAttackTimestamp().call()
    print(f"health={health}")
    print(f"lastAttackTimestamp={last_attack}")


if __name__ == "__main__":
    main()

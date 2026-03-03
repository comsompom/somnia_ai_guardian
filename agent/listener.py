import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from web3 import Web3

from agent.analysis import analyze_event
from agent.config import get_settings
from agent.reactor import send_emergency_action


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ARTIFACT_PATH = PROJECT_ROOT / "build" / "mock_vault_artifact.json"


def load_artifact() -> Dict[str, Any]:
    if not CONTRACT_ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"Artifact not found at {CONTRACT_ARTIFACT_PATH}. Run deploy first: python scripts/deploy.py"
        )
    return json.loads(CONTRACT_ARTIFACT_PATH.read_text(encoding="utf-8"))


async def run_listener() -> None:
    cfg = get_settings()
    if not cfg.vault_address:
        raise ValueError("VAULT_ADDRESS is missing in .env")
    if not cfg.private_key:
        raise ValueError("PRIVATE_KEY is missing in .env")

    artifact = load_artifact()
    abi = artifact["abi"]
    sync_w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    if not sync_w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {cfg.rpc_http_url}")
    account = sync_w3.eth.account.from_key(cfg.private_key)
    contract_sync = sync_w3.eth.contract(address=cfg.vault_address, abi=abi)
    attack_filter = contract_sync.events.AttackSimulated.create_filter(from_block="latest")

    print(f"Listening for AttackSimulated on {cfg.vault_address} ...")
    while True:
        events = attack_filter.get_new_entries()
        for event in events:
            args = event["args"]
            payload = {
                "attacker": args["attacker"],
                "new_health": int(args["newHealth"]),
                "timestamp": int(args["timestamp"]),
                "block": int(event["blockNumber"]),
                "tx_hash": event["transactionHash"].hex(),
            }
            print(f"[event] {payload}")

            decision = await analyze_event(payload)
            print(f"[decision] {decision}")

            if decision["should_react"]:
                try:
                    tx_hash = send_emergency_action(sync_w3, contract_sync, account.address)
                    print(f"[reactor] emergencyAction sent: {tx_hash}")
                except Exception as exc:
                    print(f"[reactor] failed to send emergencyAction: {exc}")
            else:
                print("[reactor] no action taken")

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(run_listener())

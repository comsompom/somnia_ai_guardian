import json
from pathlib import Path

from web3 import Web3

from agent.config import get_settings


def main() -> None:
    cfg = get_settings()
    if not cfg.private_key:
        raise ValueError("PRIVATE_KEY is missing in .env")
    if not cfg.vault_address:
        raise ValueError("VAULT_ADDRESS is missing in .env")

    artifact = json.loads(Path("build/mock_vault_artifact.json").read_text(encoding="utf-8"))
    w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    account = w3.eth.account.from_key(cfg.private_key)
    contract = w3.eth.contract(address=cfg.vault_address, abi=artifact["abi"])

    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.simulateAttack(40).build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": cfg.chain_id,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, cfg.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"simulateAttack tx: {receipt.transactionHash.hex()}")


if __name__ == "__main__":
    main()

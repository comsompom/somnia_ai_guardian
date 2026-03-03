from typing import Any

from web3 import Web3

from agent.config import get_settings
from agent.tx_utils import build_fee_params


def send_emergency_action(w3: Web3, contract: Any, account_address: str) -> str:
    cfg = get_settings()
    nonce = w3.eth.get_transaction_count(account_address, "pending")
    estimated_gas = contract.functions.emergencyAction().estimate_gas({"from": account_address})
    gas_limit = int(estimated_gas * 1.3)
    txn = contract.functions.emergencyAction().build_transaction(
        {
            "from": account_address,
            "nonce": nonce,
            "chainId": cfg.chain_id,
            "gas": gas_limit,
            **build_fee_params(w3),
        }
    )
    signed = w3.eth.account.sign_transaction(txn, private_key=cfg.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    if receipt.status != 1:
        raise RuntimeError(f"emergencyAction failed tx={tx_hash.hex()} status={receipt.status}")
    return receipt.transactionHash.hex()

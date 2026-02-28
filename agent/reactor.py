from typing import Any

from web3 import Web3

from agent.config import get_settings


def send_emergency_action(w3: Web3, contract: Any, account_address: str) -> str:
    cfg = get_settings()
    nonce = w3.eth.get_transaction_count(account_address)
    txn = contract.functions.emergencyAction().build_transaction(
        {
            "from": account_address,
            "nonce": nonce,
            "chainId": cfg.chain_id,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = w3.eth.account.sign_transaction(txn, private_key=cfg.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    return receipt.transactionHash.hex()

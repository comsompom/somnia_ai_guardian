from typing import Any, Dict

from web3 import Web3


def build_fee_params(w3: Web3) -> Dict[str, Any]:
    latest = w3.eth.get_block("latest")
    base_fee = latest.get("baseFeePerGas")
    if base_fee is not None:
        try:
            priority_fee = w3.eth.max_priority_fee
        except Exception:
            priority_fee = w3.to_wei(1, "gwei")
        max_fee = int(base_fee) * 2 + int(priority_fee)
        return {
            "maxPriorityFeePerGas": int(priority_fee),
            "maxFeePerGas": int(max_fee),
        }
    return {"gasPrice": int(w3.eth.gas_price)}

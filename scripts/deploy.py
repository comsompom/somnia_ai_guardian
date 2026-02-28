import json
from pathlib import Path

from solcx import compile_standard, install_solc
from web3 import Web3

from agent.config import get_settings


CONTRACT_FILE = Path("contracts/MockVault.sol")
BUILD_DIR = Path("build")
ARTIFACT_FILE = BUILD_DIR / "mock_vault_artifact.json"
SOLC_VERSION = "0.8.24"


def compile_contract() -> dict:
    source = CONTRACT_FILE.read_text(encoding="utf-8")
    install_solc(SOLC_VERSION)
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"MockVault.sol": {"content": source}},
            "settings": {
                "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}},
            },
        },
        solc_version=SOLC_VERSION,
    )
    contract_data = compiled["contracts"]["MockVault.sol"]["MockVault"]
    return {
        "abi": contract_data["abi"],
        "bytecode": contract_data["evm"]["bytecode"]["object"],
    }


def main() -> None:
    cfg = get_settings()
    if not cfg.private_key:
        raise ValueError("PRIVATE_KEY is missing in .env")

    contract = compile_contract()
    BUILD_DIR.mkdir(exist_ok=True)
    ARTIFACT_FILE.write_text(json.dumps(contract, indent=2), encoding="utf-8")

    w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {cfg.rpc_http_url}")

    account = w3.eth.account.from_key(cfg.private_key)
    factory = w3.eth.contract(abi=contract["abi"], bytecode=contract["bytecode"])
    nonce = w3.eth.get_transaction_count(account.address)
    tx = factory.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": cfg.chain_id,
            "gas": 2500000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, cfg.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    address = receipt.contractAddress

    print("Deployment complete")
    print(f"contract_address={address}")
    print("Add this to .env as VAULT_ADDRESS")


if __name__ == "__main__":
    main()

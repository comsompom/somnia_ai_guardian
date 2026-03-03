import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from solcx import compile_standard, install_solc
from web3 import Web3

from agent.config import get_settings
from agent.tx_utils import build_fee_params


CONTRACT_FILE = PROJECT_ROOT / "contracts" / "MockVault.sol"
BUILD_DIR = PROJECT_ROOT / "build"
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
                "evmVersion": "paris",
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
    nonce = w3.eth.get_transaction_count(account.address, "pending")
    estimated_gas = factory.constructor().estimate_gas({"from": account.address})
    gas_limit = int(estimated_gas * 1.2)
    tx = factory.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": cfg.chain_id,
            "gas": gas_limit,
            **build_fee_params(w3),
        }
    )
    signed = w3.eth.account.sign_transaction(tx, cfg.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    address = receipt.contractAddress
    if receipt.status != 1 or not address:
        raise RuntimeError(f"Deployment failed tx={tx_hash.hex()} status={receipt.status}")

    print("Deployment complete")
    print(f"deploy_tx_hash={tx_hash.hex()}")
    print(f"gas_estimate={estimated_gas}")
    print(f"gas_limit={gas_limit}")
    print(f"contract_address={address}")
    print("Add this to .env as VAULT_ADDRESS")


if __name__ == "__main__":
    main()

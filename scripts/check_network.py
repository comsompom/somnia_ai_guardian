from web3 import Web3

from agent.config import get_settings


def main() -> None:
    cfg = get_settings()
    if not cfg.private_key:
        raise ValueError("PRIVATE_KEY is missing in .env")

    w3 = Web3(Web3.HTTPProvider(cfg.rpc_http_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {cfg.rpc_http_url}")

    account = w3.eth.account.from_key(cfg.private_key)
    network_chain_id = w3.eth.chain_id
    latest_block = w3.eth.block_number
    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance_wei, "ether")

    print("Network check OK")
    print(f"rpc_http_url={cfg.rpc_http_url}")
    print(f"configured_chain_id={cfg.chain_id}")
    print(f"network_chain_id={network_chain_id}")
    print(f"latest_block={latest_block}")
    print(f"wallet_address={account.address}")
    print(f"wallet_balance_eth={balance_eth}")
    if int(network_chain_id) != int(cfg.chain_id):
        print("WARNING: CHAIN_ID in .env does not match RPC chain id")


if __name__ == "__main__":
    main()

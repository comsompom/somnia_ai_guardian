<p align="center">
  <img src="./somnia_guardian.jpg" alt="Somnia Guardian Agent" width="420" />
</p>

# Somnia Sentinel - AI Reactive Guardian (Python)

This repository contains a hackathon-ready baseline that demonstrates:
- event listening from an EVM chain (Somnia-ready),
- asynchronous multi-model AI analysis (OpenAI + Gemini),
- automatic on-chain reaction via `emergencyAction()` when an attack is detected.

## Structure

- `contracts/MockVault.sol`: vulnerable vault with `simulateAttack` and time-bounded `emergencyAction`.
- `scripts/deploy.py`: compiles and deploys `MockVault`.
- `scripts/check_network.py`: verifies RPC connectivity, chain id, and wallet balance.
- `scripts/simulate_attack.py`: triggers an attack event.
- `scripts/check_status.py`: prints current vault health and last attack timestamp.
- `agent/listener.py`: live event listener + AI decision + automatic reaction.
- `agent/analysis.py`: async model fan-out and majority vote.

## Quick Start

1. Create and activate virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy env template: `copy .env.example .env` (Windows) and fill values.
4. Run local chain (e.g., Anvil) or point `.env` to Somnia endpoints.
5. Validate network and wallet: `python scripts/check_network.py`
6. Deploy contract: `python scripts/deploy.py`
7. Put deployed address into `.env` as `VAULT_ADDRESS`.
8. Start guardian listener: `python -m agent.listener`
9. In another terminal, simulate attack: `python scripts/simulate_attack.py`
10. Check status: `python scripts/check_status.py`

When the listener catches `AttackSimulated`, it queries OpenAI and Gemini in parallel and sends `emergencyAction()` if the majority votes `attack`.  
Each provider tries its configured model list in order, automatically falling back to the next model when a model returns a bad/empty response or API error.

## Somnia Testnet Runbook

Network metadata:
- Network Name: Somnia Devnet
- RPC URL: `https://dream-rpc.somnia.network`
- Chain ID: `50312`
- Currency Symbol: `STT`

1. Set `.env` with Somnia testnet values:
   - `RPC_HTTP_URL=https://dream-rpc.somnia.network`
   - `CHAIN_ID=50312`
   - `PRIVATE_KEY=<funded_testnet_wallet>`
   - `RPC_WSS_URL` is optional in the current implementation (HTTP polling is used by default).
2. Run preflight check:
   - `python scripts/check_network.py`
3. Deploy:
   - `python scripts/deploy.py`
4. Copy `contract_address` output into `.env` as `VAULT_ADDRESS`.
5. Start listener:
   - `python -m agent.listener`
6. Trigger attack from another terminal:
   - `python scripts/simulate_attack.py`
7. Confirm recovery:
   - `python scripts/check_status.py` (expect `health=100`).

The transaction flow now supports both EIP-1559 and legacy gas pricing automatically, which improves compatibility across different testnet RPC configurations.

## Somnia Mainnet Profile

Network metadata:
- Network Name: Somnia Mainnet
- RPC URL: `https://api.infra.mainnet.somnia.network`
- Chain ID: `5031`
- Currency Symbol: `SOMI`
- Block Explorer: `https://mainnet.somnia.w3us.site` (optional if unavailable)

To switch from Devnet/Testnet to Mainnet, update `.env`:
- `RPC_HTTP_URL=https://api.infra.mainnet.somnia.network`
- `CHAIN_ID=5031`
- `PRIVATE_KEY=<funded_mainnet_wallet>`

Then run:
- `python scripts/check_network.py`
- `python scripts/deploy.py`

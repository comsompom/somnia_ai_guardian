Based on `description.md`, this repository now includes a Python-first implementation of:

- on-chain vulnerable contract (`MockVault`),
- deployment and test scripts,
- async AI decision engine (Gemini + OpenAI),
- real-time listener that reacts with an on-chain emergency transaction.

## What Was Implemented

### Smart Contract
- `contracts/MockVault.sol`
  - `simulateAttack(uint256 damage)` emits `AttackSimulated`.
  - `emergencyAction()` restores health only if called within 2 seconds.

### Python Agent
- `agent/listener.py`
  - Watches `AttackSimulated` events via WSS.
  - Sends event payload to AI models asynchronously.
  - Majority vote determines if it should call `emergencyAction()`.
- `agent/analysis.py`
  - Calls OpenAI and Gemini in parallel.
  - Has fallback heuristic when API keys are unavailable.
- `agent/reactor.py`
  - Signs and broadcasts emergency transaction.

### Deploy / Validation Scripts
- `scripts/deploy.py`: compile + deploy contract.
- `scripts/simulate_attack.py`: trigger attack event.
- `scripts/check_status.py`: verify contract health and attack timestamp.

## Detailed Deployment and Run Instructions

### 1) Prerequisites
- Python 3.10+
- A running EVM node (local Anvil/Hardhat, or Somnia RPC)
- Wallet private key funded on the target chain

### 2) Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Configure Environment

Copy `.env.example` to `.env` and set:
- `RPC_HTTP_URL`
- `RPC_WSS_URL`
- `CHAIN_ID`
- `PRIVATE_KEY`

Optional AI config:
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `GEMINI_API_KEY`, `GEMINI_MODEL`

### 4) Deploy Contract

```bash
python scripts/deploy.py
```

The script prints:
- `contract_address=...`

Copy that value to `.env` as:
- `VAULT_ADDRESS=<address>`

### 5) Start the Guardian Listener

```bash
python -m agent.listener
```

Expected output:
- listener starts on the configured vault
- event payload log
- AI decision log with vote summary
- emergency tx hash when triggered

### 6) Simulate Attack

In another terminal:

```bash
python scripts/simulate_attack.py
```

This emits `AttackSimulated`, and the listener should react quickly.

### 7) Verify State

```bash
python scripts/check_status.py
```

Expected after successful reaction:
- `health=100`

## How It Works

1. `simulateAttack` reduces vault health and emits event.
2. Listener captures event in near real-time.
3. AI fan-out queries 2 models concurrently.
4. Majority vote decides if event is malicious.
5. Reactor signs and sends `emergencyAction`.

## Somnia Usage

To use this on Somnia:
- replace `RPC_HTTP_URL`, `RPC_WSS_URL`, and `CHAIN_ID` in `.env` with Somnia devnet/testnet values.
- fund the guardian wallet and redeploy.
- keep the listener running locally.

## Notes

- No paid cloud is required for baseline behavior.
- If API keys are missing, fallback rule-based analysis still allows end-to-end demo.
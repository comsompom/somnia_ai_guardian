# Somnia Sentinel - AI Reactive Guardian (Python)

This repository contains a hackathon-ready baseline that demonstrates:
- event listening from an EVM chain (Somnia-ready),
- asynchronous multi-model AI analysis (OpenAI + Gemini),
- automatic on-chain reaction via `emergencyAction()` when an attack is detected.

## Structure

- `contracts/MockVault.sol`: vulnerable vault with `simulateAttack` and time-bounded `emergencyAction`.
- `scripts/deploy.py`: compiles and deploys `MockVault`.
- `scripts/simulate_attack.py`: triggers an attack event.
- `scripts/check_status.py`: prints current vault health and last attack timestamp.
- `agent/listener.py`: live event listener + AI decision + automatic reaction.
- `agent/analysis.py`: async model fan-out and majority vote.

## Quick Start

1. Create and activate virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy env template: `copy .env.example .env` (Windows) and fill values.
4. Run local chain (e.g., Anvil) or point `.env` to Somnia endpoints.
5. Deploy contract: `python scripts/deploy.py`
6. Put deployed address into `.env` as `VAULT_ADDRESS`.
7. Start guardian listener: `python -m agent.listener`
8. In another terminal, simulate attack: `python scripts/simulate_attack.py`
9. Check status: `python scripts/check_status.py`

When the listener catches `AttackSimulated`, it queries OpenAI and Gemini in parallel and sends `emergencyAction()` if the majority votes `attack`.

import os
from dataclasses import dataclass
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    rpc_http_url: str
    rpc_wss_url: str
    chain_id: int
    private_key: str
    vault_address: str
    openai_api_key: str
    openai_models: Tuple[str, ...]
    gemini_api_key: str
    gemini_models: Tuple[str, ...]


def _parse_models(csv_value: str, fallback_single: str, default_csv: str) -> Tuple[str, ...]:
    raw = csv_value.strip() or fallback_single.strip() or default_csv
    models = tuple(item.strip() for item in raw.split(",") if item.strip())
    return models


def get_settings() -> Settings:
    return Settings(
        rpc_http_url=os.getenv("RPC_HTTP_URL", "http://127.0.0.1:8545"),
        rpc_wss_url=os.getenv("RPC_WSS_URL", "ws://127.0.0.1:8545"),
        chain_id=int(os.getenv("CHAIN_ID", "31337")),
        private_key=os.getenv("PRIVATE_KEY", ""),
        vault_address=os.getenv("VAULT_ADDRESS", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_models=_parse_models(
            os.getenv("OPENAI_MODELS", ""),
            os.getenv("OPENAI_MODEL", ""),
            "gpt-4o-mini,gpt-4.1-mini,gpt-4.1",
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_models=_parse_models(
            os.getenv("GEMINI_MODELS", ""),
            os.getenv("GEMINI_MODEL", ""),
            "gemini-2.5-flash-preview-05-20,gemini-2.0-flash,gemini-2.5-pro,gemini-2.5-pro-preview-06-05,gemini-3-pro-preview",
        ),
    )

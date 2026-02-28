import os
from dataclasses import dataclass

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
    openai_model: str
    gemini_api_key: str
    gemini_model: str


def get_settings() -> Settings:
    return Settings(
        rpc_http_url=os.getenv("RPC_HTTP_URL", "http://127.0.0.1:8545"),
        rpc_wss_url=os.getenv("RPC_WSS_URL", "ws://127.0.0.1:8545"),
        chain_id=int(os.getenv("CHAIN_ID", "31337")),
        private_key=os.getenv("PRIVATE_KEY", ""),
        vault_address=os.getenv("VAULT_ADDRESS", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    )

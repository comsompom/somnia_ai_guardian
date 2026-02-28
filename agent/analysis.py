import asyncio
from dataclasses import dataclass
from typing import Dict, List

import aiohttp

from agent.config import get_settings


@dataclass
class ModelDecision:
    model: str
    verdict: str
    confidence: float
    summary: str


def _heuristic_fallback(payload: Dict) -> ModelDecision:
    new_health = int(payload.get("new_health", 100))
    is_attack = new_health < 80
    return ModelDecision(
        model="fallback-rule",
        verdict="attack" if is_attack else "safe",
        confidence=0.9 if is_attack else 0.8,
        summary=f"Rule-based decision from health={new_health}.",
    )


async def _call_openai(session: aiohttp.ClientSession, payload: Dict) -> ModelDecision:
    cfg = get_settings()
    if not cfg.openai_api_key:
        return _heuristic_fallback(payload)
    headers = {
        "Authorization": f"Bearer {cfg.openai_api_key}",
        "Content-Type": "application/json",
    }

    for model_name in cfg.openai_models:
        req_body = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Classify event as attack or safe and reply as JSON "
                    'with keys: verdict, confidence, summary.',
                },
                {"role": "user", "content": str(payload)},
            ],
            "response_format": {"type": "json_object"},
        }
        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=req_body,
                headers=headers,
                timeout=20,
            ) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                content = data["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    continue
                return ModelDecision(
                    model=f"openai:{model_name}",
                    verdict="attack" if "attack" in content.lower() else "safe",
                    confidence=0.75,
                    summary=content,
                )
        except Exception:
            continue

    return _heuristic_fallback(payload)


async def _call_gemini(session: aiohttp.ClientSession, payload: Dict) -> ModelDecision:
    cfg = get_settings()
    if not cfg.gemini_api_key:
        return _heuristic_fallback(payload)

    prompt = (
        "Classify this event as attack or safe. Return compact text with verdict/confidence/summary. "
        f"Event: {payload}"
    )
    for model_name in cfg.gemini_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={cfg.gemini_api_key}"
        )
        try:
            async with session.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=20,
            ) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    continue
                text = candidates[0]["content"]["parts"][0].get("text", "")
                if not text.strip():
                    continue
                return ModelDecision(
                    model=f"gemini:{model_name}",
                    verdict="attack" if "attack" in text.lower() else "safe",
                    confidence=0.72,
                    summary=text,
                )
        except Exception:
            continue

    return _heuristic_fallback(payload)


def _majority_vote(decisions: List[ModelDecision]) -> Dict:
    attack_votes = sum(1 for d in decisions if d.verdict == "attack")
    majority_threshold = (len(decisions) // 2) + 1
    should_react = attack_votes >= majority_threshold
    avg_conf = sum(d.confidence for d in decisions) / max(1, len(decisions))
    return {
        "should_react": should_react,
        "attack_votes": attack_votes,
        "model_count": len(decisions),
        "confidence": round(avg_conf, 3),
        "summaries": [f"[{d.model}] {d.summary}" for d in decisions],
    }


async def analyze_event(payload: Dict) -> Dict:
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            _call_openai(session, payload),
            _call_gemini(session, payload),
            return_exceptions=True,
        )

    decisions: List[ModelDecision] = []
    for item in results:
        if isinstance(item, Exception):
            decisions.append(_heuristic_fallback(payload))
        else:
            decisions.append(item)
    return _majority_vote(decisions)

from __future__ import annotations

import json
import os
import re
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import AppSettings
from engine.prompts import build_coach_prompt


_JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class LlmResult:
    text: str
    is_fallback: bool
    model_name: str = ""


class LocalLlmClient:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.model_path = Path(settings.llm_model_path) if settings.llm_model_path else None
        self.model_url = settings.llm_model_url.strip()
        self._model: Any = None
        self._load_error: Exception | None = None

    def is_enabled(self) -> bool:
        return self.settings.llm_provider.lower() in {"local", "llama", "llama.cpp"} and self.model_path is not None

    def model_name(self) -> str:
        if self.model_path is None:
            return "local model not configured"
        return self.model_path.name

    def _load(self) -> Any | None:
        if not self.is_enabled():
            return None
        if self._model is not None:
            return self._model
        if self.model_path is not None and not self.model_path.exists():
            if not self._download_model():
                return None
        try:
            from llama_cpp import Llama

            self._model = Llama(
                model_path=str(self.model_path),
                n_ctx=self.settings.llm_context_size,
                n_threads=max(1, (os.cpu_count() or 1)),
                verbose=False,
            )
            return self._model
        except Exception as exc:  # pragma: no cover - runtime dependency guard
            self._load_error = exc
            return None

    def _download_model(self) -> bool:
        if self.model_path is None or not self.model_url:
            return False

        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.model_path.with_suffix(self.model_path.suffix + ".download")
            with urllib.request.urlopen(self.model_url) as response, tmp_path.open("wb") as output_file:
                shutil.copyfileobj(response, output_file)
            tmp_path.replace(self.model_path)
            return True
        except Exception as exc:  # pragma: no cover - runtime dependency guard
            self._load_error = exc
            return False

    def generate(self, prompt: str) -> str | None:
        model = self._load()
        if model is None:
            return None

        try:
            response = model(
                prompt,
                max_tokens=self.settings.llm_max_tokens,
                temperature=self.settings.llm_temperature,
                stop=["```", "</json>"],
            )
            choices = response.get("choices", []) if isinstance(response, dict) else []
            if not choices:
                return None
            text = choices[0].get("text", "")
            return text.strip() or None
        except Exception as exc:  # pragma: no cover - runtime dependency guard
            self._load_error = exc
            return None

    def status(self) -> str:
        if not self.is_enabled():
            return "Local LLM disabled"
        if self.model_path is not None and not self.model_path.exists():
            if self.model_url:
                return f"Downloading {self.model_path.name}"
            return f"Missing model file: {self.model_path}"
        if self._model is not None:
            return f"Loaded {self.model_name()}"
        if self._load_error is not None:
            return f"LLM unavailable: {self._load_error}"
        return f"Ready to load {self.model_name()}"


def prepare_local_model(settings: AppSettings) -> str:
    client = LocalLlmClient(settings)
    if not client.is_enabled():
        return client.status()
    if client.model_path is not None and client.model_path.exists():
        return f"Model cached: {client.model_name()}"
    if client._download_model():
        return f"Model downloaded: {client.model_name()}"
    return client.status()


def _extract_json(text: str) -> dict[str, Any] | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
    match = _JSON_PATTERN.search(candidate)
    if match is not None:
        candidate = match.group(0)
    try:
        loaded = json.loads(candidate)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        return None
    return None


def _fallback_note(snapshot: dict[str, Any], recommendations: list[Any]) -> str:
    summary = snapshot.get("summary", {})
    lead_count = int(summary.get("leads", 0))
    cost_per_lead = float(summary.get("cost_per_lead", 0.0))
    if recommendations:
        top_recommendation = recommendations[0]
        if isinstance(top_recommendation, dict):
            campaign_name = top_recommendation.get("campaign_name", top_recommendation.get("campaign_id", "campaign"))
            action = top_recommendation.get("action", "Modify")
            reason = top_recommendation.get("reason", "")
            risk = top_recommendation.get("risk", "")
        else:
            campaign_name = getattr(top_recommendation, "campaign_name", getattr(top_recommendation, "campaign_id", "campaign"))
            action = getattr(top_recommendation, "action", "Modify")
            reason = getattr(top_recommendation, "reason", "")
            risk = getattr(top_recommendation, "risk", "")
        return (
            f"### AI Coach\n\n"
            f"**{action} {campaign_name}.** {reason} "
            f"This keeps the dashboard focused on efficient lead generation at roughly ${cost_per_lead:,.2f} CPL across {lead_count} leads. "
            f"Risk: {risk}."
        )

    return (
        "### AI Coach\n\n"
        f"The account is stable at about ${cost_per_lead:,.2f} CPL across {lead_count} leads. "
        "Keep spend tight, watch the lowest-performing campaign, and only scale once the trend stays consistent."
    )


def build_ai_coach_note(snapshot: dict[str, Any], recommendations: list[Any], settings: AppSettings) -> str:
    client = LocalLlmClient(settings)
    if not client.is_enabled():
        return _fallback_note(snapshot, recommendations)

    prompt = build_coach_prompt(snapshot, recommendations, client.model_name())
    generated_text = client.generate(prompt)
    if not generated_text:
        return _fallback_note(snapshot, recommendations)

    parsed = _extract_json(generated_text)
    if not parsed:
        return _fallback_note(snapshot, recommendations)

    headline = str(parsed.get("headline", "AI Coach"))
    chosen_campaign = str(parsed.get("chosen_campaign", ""))
    action = str(parsed.get("action", "Modify"))
    reason = str(parsed.get("reason", ""))
    expected_impact = str(parsed.get("expected_impact", ""))
    risk = str(parsed.get("risk", ""))
    confidence = str(parsed.get("confidence", ""))
    next_step = str(parsed.get("next_step", ""))

    parts = [f"### {headline}", ""]
    if chosen_campaign:
        parts.append(f"**Campaign:** {chosen_campaign}")
    parts.append(f"**Action:** {action}")
    if reason:
        parts.append(f"**Reason:** {reason}")
    if expected_impact:
        parts.append(f"**Expected impact:** {expected_impact}")
    if risk:
        parts.append(f"**Risk:** {risk}")
    if confidence:
        parts.append(f"**Confidence:** {confidence}")
    if next_step:
        parts.append(f"**Next step:** {next_step}")

    return "\n".join(parts)

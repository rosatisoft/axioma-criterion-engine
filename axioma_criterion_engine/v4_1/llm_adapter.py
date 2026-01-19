from __future__ import annotations

"""
axioma_criterion_engine.v4_1.llm_adapter

Objetivo:
- Un adaptador mínimo y robusto para usar un LLM con el Motor de Criterio V4.1.1.
- Interfaz única: generate(prompt: str) -> str
- Compatible con:
  - OpenAI Python SDK "responses" (nuevo)
  - OpenAI Python SDK "chat.completions" (legacy)
  - Cualquier cliente similar por duck-typing

Notas:
- El Motor (entrevista + detector) ya incluye instrucciones dentro del prompt.
  Por eso, este adaptador solo necesita "pasar el prompt" y devolver texto.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional


# -----------------------------
# Config / defaults
# -----------------------------

DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
DEFAULT_MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "700"))


# -----------------------------
# Helper: safely extract text
# -----------------------------

def _safe_strip(x: Any) -> str:
    return (str(x) if x is not None else "").strip()


def _extract_text_from_openai_responses(resp: Any) -> str:
    """
    Soporta OpenAI Responses API.
    Intenta varias rutas porque el SDK ha cambiado entre versiones.
    """
    # 1) resp.output_text (común)
    txt = getattr(resp, "output_text", None)
    if txt:
        return _safe_strip(txt)

    # 2) resp.output -> lista de items con content -> text
    out = getattr(resp, "output", None)
    if isinstance(out, list):
        chunks: list[str] = []
        for item in out:
            content = getattr(item, "content", None)
            if isinstance(content, list):
                for c in content:
                    t = getattr(c, "text", None)
                    if t:
                        chunks.append(_safe_strip(t))
        if chunks:
            return "\n".join([c for c in chunks if c])

    # 3) fallback genérico
    return _safe_strip(resp)


def _extract_text_from_openai_chat(resp: Any) -> str:
    """
    Soporta Chat Completions API (legacy): resp.choices[0].message.content
    """
    try:
        choices = getattr(resp, "choices", None)
        if choices and len(choices) > 0:
            msg = getattr(choices[0], "message", None)
            content = getattr(msg, "content", None)
            if content:
                return _safe_strip(content)
    except Exception:
        pass
    return _safe_strip(resp)


# -----------------------------
# Base interface
# -----------------------------

class BaseLLMAdapter:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


# -----------------------------
# Generic client wrapper (duck-typing)
# -----------------------------

@dataclass
class LLMClientAdapter(BaseLLMAdapter):
    """
    Wrapper genérico:
    - Si client tiene responses.create(...) -> usa Responses API
    - Si client tiene chat.completions.create(...) -> usa ChatCompletions
    """
    client: Any
    model: str = DEFAULT_OPENAI_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS

    def generate(self, prompt: str) -> str:
        prompt = _safe_strip(prompt)
        if not prompt:
            return ""

        # 1) Responses API (nuevo)
        if hasattr(self.client, "responses") and hasattr(self.client.responses, "create"):
            resp = self.client.responses.create(
                model=self.model,
                input=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            )
            return _extract_text_from_openai_responses(resp)

        # 2) Chat Completions (legacy)
        if (
            hasattr(self.client, "chat")
            and hasattr(self.client.chat, "completions")
            and hasattr(self.client.chat.completions, "create")
        ):
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return _extract_text_from_openai_chat(resp)

        # 3) Si el cliente trae un método "generate" propio
        if hasattr(self.client, "generate") and callable(self.client.generate):
            try:
                return _safe_strip(self.client.generate(prompt))
            except Exception:
                return ""

        # 4) No soportado
        return ""


# Alias esperado por otros módulos (soft_contradiction_detector intenta importarlo)
LLMAdapter = LLMClientAdapter


# -----------------------------
# Convenience: build OpenAI client (opcional)
# -----------------------------

def build_openai_client(api_key: Optional[str] = None) -> Any:
    """
    Crea un cliente OpenAI si está instalado el SDK.
    Uso típico:
        from .llm_adapter import build_openai_client, LLMClientAdapter
        client = build_openai_client()
        llm = LLMClientAdapter(client)
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY (env) or api_key parameter.")

    try:
        # SDK moderno
        from openai import OpenAI  # type: ignore
        return OpenAI(api_key=api_key)
    except Exception as e:
        raise RuntimeError(
            "OpenAI SDK not available or incompatible. Install/upgrade 'openai' package."
        ) from e

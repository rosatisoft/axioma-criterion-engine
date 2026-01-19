# axioma_criterion_engine/v4_1/llm_adapter.py
"""
LLM Adapter (v4.1.1)

Objetivo:
- Proveer una interfaz estable para llamar a un LLM (OpenAI) desde el motor de criterio (v4_1)
- Soportar modo "dummy" para pruebas offline
- Soportar respuesta en texto y respuesta JSON (con tolerancia)

Variables de entorno soportadas:
- LLM_PROVIDER: "openai" (default) | "dummy"
- OPENAI_API_KEY: requerido para OpenAI
- OPENAI_MODEL: default "gpt-4o-mini"
- OPENAI_BASE_URL: opcional (por si usas proxy/gateway)
- LLM_DEBUG: "1" para logs básicos

Dependencia:
- pip install openai
"""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, TypedDict, Union


# -----------------------------
# Tipos / contratos
# -----------------------------

class ChatMessage(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMError(RuntimeError):
    """Error base del adaptador."""


class LLMConfigError(LLMError):
    """Configuración inválida."""


class LLMCallError(LLMError):
    """Fallo al llamar al modelo."""


# -----------------------------
# Config
# -----------------------------

@dataclass
class LLMConfig:
    provider: str = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")

    temperature: float = 0.2
    max_tokens: int = 900
    top_p: float = 1.0

    max_retries: int = 3
    timeout_s: float = 60.0

    debug: bool = os.getenv("LLM_DEBUG", "0").strip() in ("1", "true", "True", "yes", "YES")


def _debug(cfg: LLMConfig, *args: Any) -> None:
    if cfg.debug:
        print("[llm_adapter]", *args)


def _backoff_sleep(attempt: int) -> None:
    # exponencial suave con jitter
    base = min(6.0, 0.6 * (2 ** attempt))
    jitter = random.uniform(0.0, 0.25)
    time.sleep(base + jitter)


def _normalize_messages(messages: Sequence[ChatMessage]) -> List[ChatMessage]:
    if not isinstance(messages, (list, tuple)) or len(messages) == 0:
        raise ValueError("messages debe ser una lista no vacía de {'role','content'}")

    norm: List[ChatMessage] = []
    for m in messages:
        if not isinstance(m, dict):
            raise ValueError("Cada mensaje debe ser dict")
        role = m.get("role")
        content = m.get("content")
        if role not in ("system", "user", "assistant"):
            raise ValueError(f"role inválido: {role!r}")
        if not isinstance(content, str):
            raise ValueError("content debe ser str")
        norm.append({"role": role, "content": content})
    return norm


def _extract_json_loose(text: str) -> Dict[str, Any]:
    """
    Intenta parsear JSON aunque el modelo haya agregado texto alrededor.
    """
    s = (text or "").strip()
    if not s:
        raise ValueError("Respuesta vacía; no hay JSON.")

    # caso directo
    if s.startswith("{") and s.endswith("}"):
        return json.loads(s)

    # buscar primer { y último }
    i = s.find("{")
    j = s.rfind("}")
    if i != -1 and j != -1 and j > i:
        chunk = s[i : j + 1]
        return json.loads(chunk)

    raise ValueError("No se encontró un objeto JSON en la respuesta.")


# -----------------------------
# Interfaz base
# -----------------------------

class BaseLLMAdapter:
    def __init__(self, cfg: Optional[LLMConfig] = None):
        self.cfg = cfg or LLMConfig()

    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        want_json: bool = False,
    ) -> str:
        raise NotImplementedError

    def chat_json(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Pide JSON al modelo y lo parsea de forma tolerante.
        """
        txt = self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            want_json=True,
        )
        try:
            return json.loads(txt)
        except Exception:
            return _extract_json_loose(txt)


# -----------------------------
# Dummy
# -----------------------------

class DummyAdapter(BaseLLMAdapter):
    """
    Adapter offline para pruebas.
    """
    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        want_json: bool = False,
    ) -> str:
        messages = _normalize_messages(messages)
        last_user = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user = m["content"]
                break

        if want_json:
            return json.dumps(
                {
                    "ok": True,
                    "provider": "dummy",
                    "model": "dummy",
                    "echo": last_user[:600],
                    "notes": "Respuesta dummy (sin llamada real).",
                },
                ensure_ascii=False,
                indent=2,
            )

        return (
            "⚙️ [DUMMY]\n"
            "No hay llamada a un LLM real.\n\n"
            f"Último user:\n{last_user[:1200]}"
        )


# -----------------------------
# OpenAI
# -----------------------------

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, cfg: Optional[LLMConfig] = None):
        super().__init__(cfg)
        if not self.cfg.api_key:
            raise LLMConfigError("Falta OPENAI_API_KEY (variable de entorno) para usar OpenAIAdapter.")

        try:
            from openai import OpenAI  # openai>=1.0.0
        except Exception as e:
            raise LLMConfigError("No se pudo importar 'openai'. Instala con: pip install openai") from e

        client_kwargs: Dict[str, Any] = {"api_key": self.cfg.api_key}
        if self.cfg.base_url:
            client_kwargs["base_url"] = self.cfg.base_url

        self._client = OpenAI(**client_kwargs)

    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        want_json: bool = False,
    ) -> str:
        cfg = self.cfg
        msgs = _normalize_messages(messages)

        temp = cfg.temperature if temperature is None else temperature
        mtok = cfg.max_tokens if max_tokens is None else max_tokens

        # Si queremos JSON: lo forzamos por instrucción + (si está disponible) response_format
        # Para no romper compatibilidad entre versiones, intentamos con response_format y si falla, caemos a prompt-only.
        if want_json:
            msgs = self._inject_json_guardrails(msgs)

        last_err: Optional[Exception] = None

        for attempt in range(cfg.max_retries + 1):
            try:
                _debug(cfg, f"OpenAI call attempt={attempt} model={cfg.model} want_json={want_json}")

                # 1) Intento con response_format si want_json
                if want_json:
                    try:
                        resp = self._client.chat.completions.create(
                            model=cfg.model,
                            messages=msgs,
                            temperature=temp,
                            max_tokens=mtok,
                            top_p=cfg.top_p,
                            response_format={"type": "json_object"},
                            timeout=cfg.timeout_s,
                        )
                        text = (resp.choices[0].message.content or "").strip()
                        if text:
                            return text
                    except Exception as e_rf:
                        # response_format puede no estar soportado en algunas combinaciones.
                        _debug(cfg, "response_format no disponible, fallback a prompt-only:", repr(e_rf))

                # 2) Fallback normal (prompt-only)
                resp2 = self._client.chat.completions.create(
                    model=cfg.model,
                    messages=msgs,
                    temperature=temp,
                    max_tokens=mtok,
                    top_p=cfg.top_p,
                    timeout=cfg.timeout_s,
                )
                text2 = (resp2.choices[0].message.content or "").strip()
                if not text2:
                    raise LLMCallError("Respuesta vacía del modelo.")
                return text2

            except Exception as e:
                last_err = e
                _debug(cfg, "OpenAI error:", repr(e))
                if attempt >= cfg.max_retries:
                    break
                _backoff_sleep(attempt)

        raise LLMCallError(f"Falló la llamada a OpenAI. Último error: {last_err!r}")

    @staticmethod
    def _inject_json_guardrails(msgs: List[ChatMessage]) -> List[ChatMessage]:
        """
        Inserta reglas para que el modelo devuelva SOLO JSON válido.
        No rompe si ya hay system prompt.
        """
        guard = (
            "IMPORTANTE: Devuelve EXCLUSIVAMENTE un objeto JSON válido.\n"
            "No incluyas texto adicional, ni Markdown, ni explicaciones.\n"
            "Asegúrate de que el JSON sea parseable."
        )

        out = list(msgs)
        # Si existe system, lo reforzamos al final del system; si no, lo creamos.
        for i, m in enumerate(out):
            if m["role"] == "system":
                out[i] = {"role": "system", "content": m["content"].rstrip() + "\n\n" + guard}
                return out

        return [{"role": "system", "content": guard}] + out


# -----------------------------
# Factory
# -----------------------------

def build_llm_adapter(cfg: Optional[LLMConfig] = None) -> BaseLLMAdapter:
    cfg = cfg or LLMConfig()
    p = (cfg.provider or "").strip().lower()

    if p in ("dummy", "offline", "noop"):
        return DummyAdapter(cfg)

    if p in ("openai", "oai"):
        return OpenAIAdapter(cfg)

    raise LLMConfigError(f"Proveedor no soportado: {cfg.provider!r}. Usa 'openai' o 'dummy'.")


# -----------------------------
# Mini self-test (opcional)
# -----------------------------
if __name__ == "__main__":
    llm = build_llm_adapter()
    test_messages: List[ChatMessage] = [
        {"role": "system", "content": "Eres un asistente de criterio F–C–P. Sé claro y concreto."},
        {"role": "user", "content": "Devuelve un JSON con keys: ok, idea. Idea: 'Motor de criterio'."},
    ]
    print(llm.chat(test_messages, want_json=True))


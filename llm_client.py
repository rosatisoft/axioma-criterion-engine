# axioma_criterion_engine/llm_client.py

from __future__ import annotations
import os
from typing import List, Dict, Any, Optional

from openai import OpenAI


class LLMClient:
    """
    Wrapper simple para el cliente de OpenAI (Responses API).
    Lo dejamos lo más minimalista posible: un método `complete(prompt)`.
    """

    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        """
        - `api_key`: si no se pasa, toma OPENAI_API_KEY del entorno.
        - `base_url`: útil si luego usas Azure o proxy.
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en variables de entorno o en el constructor de LLMClient.")

        client_kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = OpenAI(**client_kwargs)
        self.model = model

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Llamada básica de texto: prompt → texto.
        Usa `client.responses.create` y devuelve `output_text`.
        """
        input_items: List[Dict[str, Any]] = []
        if system:
            input_items.append({
                "role": "system",
                "content": [{"type": "input_text", "text": system}],
            })

        input_items.append({
            "role": "user",
            "content": [{"type": "input_text", "text": prompt}],
        })

        response = self._client.responses.create(
            model=self.model,
            input=input_items,
        )
        # `output_text` es la forma más cómoda de leer todo el texto plano
        return response.output_text

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """
        Versión tipo 'chat' con messages ya estructurado (role, content).
        Lo envolvemos también como `responses.create`.
        """
        response = self._client.responses.create(
            model=self.model,
            input=messages,
        )
        return response.output_text

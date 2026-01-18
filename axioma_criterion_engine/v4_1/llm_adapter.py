from __future__ import annotations

from .interview_agent_v4_1 import LLMInterface


class LLMClientAdapter(LLMInterface):
    """
    Adapta tu cliente real a la interfaz mínima LLMInterface.
    Espera que tu cliente tenga un método tipo `complete(prompt: str) -> str`
    o similar. Ajusta una sola línea si tu método se llama distinto.
    """

    def __init__(self, client) -> None:
        self.client = client

    def generate(self, prompt: str) -> str:
        # Ajusta aquí si tu método es chat(), responses(), invoke(), etc.
        return self.client.complete(prompt)

"""Prozessweite Laufzeitobjekte.

Der ModelGateway wird im FastAPI-Lifespan gesetzt und hier für Komponenten
außerhalb des Request-Objekts (MCP-Tools, Eval-Runner) bereitgestellt.
"""

from .llm import ModelGateway

_gateway: ModelGateway | None = None


def set_gateway(gateway: ModelGateway | None) -> None:
    global _gateway
    _gateway = gateway


def gateway() -> ModelGateway:
    if _gateway is None:
        raise RuntimeError("ModelGateway nicht initialisiert (Lifespan nicht gelaufen)")
    return _gateway

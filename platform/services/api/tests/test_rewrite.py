from app.config import settings
from app.rag import rewrite_query

HISTORY = [
    {"role": "user", "content": "Was ist bei der Presse P-300 wöchentlich zu warten?"},
    {"role": "assistant", "content": "Abschmieren und Öldruck messen [1]."},
]


class ScriptedGateway:
    def __init__(self, reply):
        self.reply = reply

    async def chat(self, messages, **overrides):
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


async def test_rewrites_followup_question():
    gateway = ScriptedGateway("Presse P-300 Öldruck Sollwert wöchentliche Wartung")
    result = await rewrite_query(gateway, HISTORY, "Und welcher Druck ist dabei richtig?")
    assert result == "Presse P-300 Öldruck Sollwert wöchentliche Wartung"


async def test_no_history_returns_original():
    result = await rewrite_query(ScriptedGateway("egal"), [], "Wie viele Urlaubstage?")
    assert result == "Wie viele Urlaubstage?"


async def test_error_falls_back_to_original():
    result = await rewrite_query(ScriptedGateway(RuntimeError("down")), HISTORY, "Frage?")
    assert result == "Frage?"


async def test_garbage_output_falls_back():
    assert await rewrite_query(ScriptedGateway(""), HISTORY, "Frage?") == "Frage?"
    assert await rewrite_query(ScriptedGateway("x" * 500), HISTORY, "Frage?") == "Frage?"
    assert (
        await rewrite_query(ScriptedGateway("Zeile1\nZeile2"), HISTORY, "Frage?") == "Frage?"
    )


async def test_disabled_via_settings(monkeypatch):
    monkeypatch.setattr(settings, "query_rewrite_enabled", False)
    result = await rewrite_query(ScriptedGateway("umformuliert"), HISTORY, "Original?")
    assert result == "Original?"
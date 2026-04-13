"""Tests for ReplSession state."""

from __future__ import annotations

from app.cli.repl.session import ReplSession


class TestReplSession:
    def test_defaults(self) -> None:
        session = ReplSession()
        assert session.history == []
        assert session.last_state is None
        assert session.accumulated_context == {}
        assert session.trust_mode is False

    def test_record_appends_entry(self) -> None:
        session = ReplSession()
        session.record("alert", "cpu high")
        session.record("slash", "/status", ok=True)
        session.record("alert", "bad one", ok=False)
        assert len(session.history) == 3
        assert session.history[-1]["type"] == "alert"
        assert session.history[-1]["ok"] is False

    def test_clear_preserves_trust_mode(self) -> None:
        session = ReplSession()
        session.trust_mode = True
        session.accumulated_context["service"] = "api"
        session.record("alert", "something")
        session.last_state = {"foo": "bar"}

        session.clear()

        assert session.history == []
        assert session.last_state is None
        assert session.accumulated_context == {}
        assert session.trust_mode is True  # preserved intentionally

"""Tests for slash command dispatch."""

from __future__ import annotations

import io

from rich.console import Console

from app.cli.repl.commands import SLASH_COMMANDS, dispatch_slash
from app.cli.repl.session import ReplSession


def _capture() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=False, highlight=False), buf


class TestDispatchSlash:
    def test_exit_returns_false(self) -> None:
        session = ReplSession()
        console, _ = _capture()
        assert dispatch_slash("/exit", session, console) is False
        assert dispatch_slash("/quit", session, console) is False

    def test_help_lists_all_commands(self) -> None:
        session = ReplSession()
        console, buf = _capture()
        assert dispatch_slash("/help", session, console) is True
        output = buf.getvalue()
        for name in SLASH_COMMANDS:
            assert name in output

    def test_trust_toggle(self) -> None:
        session = ReplSession()
        console, _ = _capture()
        assert session.trust_mode is False
        dispatch_slash("/trust", session, console)
        assert session.trust_mode is True
        dispatch_slash("/trust off", session, console)
        assert session.trust_mode is False

    def test_reset_clears_session(self) -> None:
        session = ReplSession()
        session.record("alert", "test")
        session.last_state = {"x": 1}
        session.trust_mode = True
        console, _ = _capture()

        dispatch_slash("/reset", session, console)

        assert session.history == []
        assert session.last_state is None
        assert session.trust_mode is True  # reset keeps trust mode

    def test_status_shows_session_fields(self) -> None:
        session = ReplSession()
        session.record("alert", "hello")
        console, buf = _capture()
        dispatch_slash("/status", session, console)
        output = buf.getvalue()
        assert "interactions" in output
        assert "trust mode" in output

    def test_unknown_command_does_not_exit(self) -> None:
        session = ReplSession()
        console, buf = _capture()
        assert dispatch_slash("/made-up", session, console) is True
        assert "unknown command" in buf.getvalue()

    def test_empty_input_is_noop(self) -> None:
        session = ReplSession()
        console, _ = _capture()
        assert dispatch_slash("   ", session, console) is True

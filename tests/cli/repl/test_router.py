"""Tests for REPL input classification."""

from __future__ import annotations

from app.cli.repl.router import classify_input
from app.cli.repl.session import ReplSession


class TestClassifyInput:
    def test_slash_command(self) -> None:
        session = ReplSession()
        assert classify_input("/help", session) == "slash"
        assert classify_input("  /status", session) == "slash"

    def test_bare_command_word_classified_as_slash(self) -> None:
        session = ReplSession()
        # A bare word matching a slash command short name should route to slash
        # even without the leading '/' and even with no prior investigation.
        for word in ("help", "exit", "quit", "status", "clear", "reset", "trust"):
            assert classify_input(word, session) == "slash", word

    def test_bare_command_is_case_insensitive(self) -> None:
        session = ReplSession()
        assert classify_input("HELP", session) == "slash"
        assert classify_input("Exit", session) == "slash"

    def test_no_prior_state_is_new_alert(self) -> None:
        session = ReplSession()
        assert classify_input("why is the database slow?", session) == "new_alert"

    def test_short_question_with_prior_state_is_follow_up(self) -> None:
        session = ReplSession()
        session.last_state = {"root_cause": "disk full"}
        assert classify_input("why?", session) == "follow_up"
        assert classify_input("what caused it?", session) == "follow_up"

    def test_alert_keywords_with_prior_state_still_new_alert(self) -> None:
        session = ReplSession()
        session.last_state = {"root_cause": "disk full"}
        assert classify_input("CPU spiked on orders-api", session) == "new_alert"
        assert classify_input("5xx errors from checkout service", session) == "new_alert"

    def test_long_non_question_defaults_to_new_alert(self) -> None:
        session = ReplSession()
        session.last_state = {"root_cause": "disk full"}
        long_text = (
            "the orders-api service started returning intermittent failures "
            "around 14:00 UTC today and our on-call is paged"
        )
        assert classify_input(long_text, session) == "new_alert"

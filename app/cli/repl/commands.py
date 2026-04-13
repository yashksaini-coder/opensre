"""Slash command handlers for the REPL."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from app.cli.repl.banner import render_banner
from app.cli.repl.session import ReplSession


@dataclass(frozen=True)
class SlashCommand:
    name: str
    help_text: str
    handler: Callable[[ReplSession, Console, list[str]], bool]


def _cmd_help(session: ReplSession, console: Console, args: list[str]) -> bool:  # noqa: ARG001
    table = Table(title="Slash commands", title_style="bold cyan", show_header=False)
    table.add_column("name", style="bold")
    table.add_column("description", style="dim")
    for cmd in SLASH_COMMANDS.values():
        table.add_row(cmd.name, cmd.help_text)
    console.print(table)
    return True


def _cmd_exit(session: ReplSession, console: Console, args: list[str]) -> bool:  # noqa: ARG001
    console.print("[dim]goodbye.[/dim]")
    return False


def _cmd_clear(session: ReplSession, console: Console, args: list[str]) -> bool:  # noqa: ARG001
    console.clear()
    render_banner(console)
    return True


def _cmd_reset(session: ReplSession, console: Console, args: list[str]) -> bool:  # noqa: ARG001
    session.clear()
    console.print("[dim]session state cleared.[/dim]")
    return True


def _cmd_trust(session: ReplSession, console: Console, args: list[str]) -> bool:
    if args and args[0].lower() in ("off", "false", "disable"):
        session.trust_mode = False
        console.print("[dim]trust mode off[/dim]")
    else:
        session.trust_mode = True
        console.print("[yellow]trust mode on[/yellow] — future approval prompts will be skipped")
    return True


def _cmd_status(session: ReplSession, console: Console, args: list[str]) -> bool:  # noqa: ARG001
    table = Table(title="Session status", title_style="bold cyan", show_header=False)
    table.add_column("key", style="bold")
    table.add_column("value")
    table.add_row("interactions", str(len(session.history)))
    table.add_row("last investigation", "yes" if session.last_state else "none")
    table.add_row("trust mode", "on" if session.trust_mode else "off")
    table.add_row("provider", os.getenv("LLM_PROVIDER", "anthropic"))
    acc = session.accumulated_context
    if acc:
        table.add_row("accumulated context", ", ".join(sorted(acc.keys())))
    console.print(table)
    return True


SLASH_COMMANDS: dict[str, SlashCommand] = {
    "/help": SlashCommand("/help", "show available commands", _cmd_help),
    "/exit": SlashCommand("/exit", "exit the REPL", _cmd_exit),
    "/quit": SlashCommand("/quit", "alias for /exit", _cmd_exit),
    "/clear": SlashCommand("/clear", "clear the screen and re-render the banner", _cmd_clear),
    "/reset": SlashCommand("/reset", "clear session state (keeps trust mode)", _cmd_reset),
    "/trust": SlashCommand("/trust", "toggle trust mode ('/trust off' to disable)", _cmd_trust),
    "/status": SlashCommand("/status", "show session status", _cmd_status),
}


def dispatch_slash(command_line: str, session: ReplSession, console: Console) -> bool:
    """Dispatch a slash command line. Returns False iff the REPL should exit."""
    parts = command_line.strip().split()
    if not parts:
        return True
    name = parts[0].lower()
    args = parts[1:]
    cmd = SLASH_COMMANDS.get(name)
    if cmd is None:
        console.print(f"[red]unknown command:[/red] {name}  (type [bold]/help[/bold])")
        return True
    return cmd.handler(session, console, args)

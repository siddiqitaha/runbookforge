"""Distill: turn a noisy session into the minimal golden path."""
from __future__ import annotations

from .models import Session, Runbook, Step

# Inspection/navigation commands that don't belong in a runbook.
# (`echo` is intentionally NOT here — `echo … > file` is a real build step.)
NOISE_PREFIXES = ("cd", "ls", "ll", "pwd", "clear", "history", "exit",
                  "man", "help", "which", "cat", "less", "more", "top", "htop")


def _is_noise(cmd: str) -> bool:
    head = cmd.strip().split(" ", 1)[0]
    return head in NOISE_PREFIXES


def distill(session: Session, title: str | None = None) -> Runbook:
    steps: list[Step] = []
    last = None
    for c in session.commands:
        if c.exit_code != 0:          # failed attempts / dead ends
            continue
        if _is_noise(c.cmd):          # navigation & inspection noise
            continue
        if c.cmd == last:             # consecutive duplicates
            continue
        steps.append(Step(cmd=c.cmd))
        last = c.cmd

    return Runbook(
        title=title or session.title,
        description="Distilled golden path — only the commands that succeeded and mattered.",
        steps=steps,
    )

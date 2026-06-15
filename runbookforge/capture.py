"""Capture: run an interactive session, recording every command + its result."""
from __future__ import annotations

import os
import subprocess

from .models import Session, Command

BANNER = """\
RunbookForge capture — type commands as you would in a shell.
They run for real and are recorded. Type `:done` to finish, `:abort` to cancel.
"""


def capture(out_path: str, title: str | None = None) -> Session:
    print(BANNER)
    session = Session(title=title or "Captured session")
    cwd = os.getcwd()
    idx = 0
    while True:
        try:
            line = input(f"[{idx}] {cwd} $ ").strip()
        except EOFError:
            break
        if line in (":done", ""):
            if line == ":done":
                break
            continue
        if line == ":abort":
            print("aborted, nothing written.")
            return session

        # `cd` must change our own process dir so later steps see it.
        if line.startswith("cd "):
            target = os.path.expanduser(line[3:].strip()) or "."
            new = target if os.path.isabs(target) else os.path.join(cwd, target)
            if os.path.isdir(new):
                cwd = os.path.normpath(new)
                session.commands.append(Command(idx, line, 0, cwd, ""))
            else:
                print(f"  cd: no such directory: {target}")
                session.commands.append(Command(idx, line, 1, cwd, "no such directory"))
            idx += 1
            continue

        proc = subprocess.run(line, shell=True, cwd=cwd,
                              capture_output=True, text=True)
        out = (proc.stdout + proc.stderr)
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        session.commands.append(
            Command(idx, line, proc.returncode, cwd, out.strip()[-500:])
        )
        idx += 1

    session.to_json(out_path)
    print(f"\nCaptured {len(session.commands)} commands → {out_path}")
    return session

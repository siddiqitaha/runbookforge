"""Unit tests for the distill stage."""
from runbookforge.models import Session, Command
from runbookforge.distill import distill


def _session():
    return Session(title="t", commands=[
        Command(0, "python3 --version", 0),
        Command(1, "ls", 0),                                  # noise
        Command(2, "pip install nope-xyz", 1),                # failed
        Command(3, "mkdir -p build", 0),
        Command(4, "echo x > build/app.py", 0),
        Command(5, "cat build/app.py", 0),                    # noise
        Command(6, "python3 build/app.py", 0),
        Command(7, "python3 build/app.py", 0),                # duplicate
    ])


def test_distill_keeps_only_golden_path():
    rb = distill(_session())
    cmds = [s.cmd for s in rb.steps]
    assert cmds == [
        "python3 --version",
        "mkdir -p build",
        "echo x > build/app.py",
        "python3 build/app.py",
    ]


def test_distill_drops_failures_and_noise():
    rb = distill(_session())
    assert all("pip install" not in s.cmd for s in rb.steps)  # failed dropped
    assert all(s.cmd != "ls" for s in rb.steps)               # noise dropped

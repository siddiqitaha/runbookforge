"""Data model + (de)serialization for sessions and runbooks."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import yaml


@dataclass
class Command:
    """A single recorded command from a capture session."""
    index: int
    cmd: str
    exit_code: int = 0
    cwd: str = ""
    output_tail: str = ""


@dataclass
class Session:
    title: str = "Captured session"
    commands: list[Command] = field(default_factory=list)

    def to_json(self, path: str) -> None:
        with open(path, "w") as fh:
            json.dump({"title": self.title, "commands": [asdict(c) for c in self.commands]},
                      fh, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "Session":
        with open(path) as fh:
            d = json.load(fh)
        return cls(title=d.get("title", "Captured session"),
                   commands=[Command(**c) for c in d.get("commands", [])])


@dataclass
class Step:
    cmd: str
    description: str = ""


@dataclass
class Runbook:
    title: str = "Runbook"
    description: str = ""
    steps: list[Step] = field(default_factory=list)

    def to_yaml(self, path: str) -> None:
        with open(path, "w") as fh:
            yaml.safe_dump(
                {"title": self.title, "description": self.description,
                 "steps": [asdict(s) for s in self.steps]},
                fh, sort_keys=False, default_flow_style=False,
            )

    @classmethod
    def from_yaml(cls, path: str) -> "Runbook":
        with open(path) as fh:
            d = yaml.safe_load(fh) or {}
        return cls(title=d.get("title", "Runbook"), description=d.get("description", ""),
                   steps=[Step(**s) for s in d.get("steps", [])])

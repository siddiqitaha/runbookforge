"""Validate: replay a runbook on a clean environment and report reproducibility."""
from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess
import tempfile

from .models import Runbook


@dataclass
class StepResult:
    cmd: str
    exit_code: int
    output_tail: str


def _run_local(rb: Runbook) -> list[StepResult]:
    workdir = tempfile.mkdtemp(prefix="rbf-validate-")
    results: list[StepResult] = []
    try:
        cwd = workdir
        for step in rb.steps:
            if step.cmd.startswith("cd "):
                target = os.path.expanduser(step.cmd[3:].strip())
                cwd = target if os.path.isabs(target) else os.path.normpath(os.path.join(cwd, target))
                results.append(StepResult(step.cmd, 0 if os.path.isdir(cwd) else 1, ""))
                continue
            p = subprocess.run(step.cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            results.append(StepResult(step.cmd, p.returncode, (p.stdout + p.stderr).strip()[-300:]))
            if p.returncode != 0:
                break
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return results


def _run_docker(rb: Runbook, image: str) -> list[StepResult]:
    script = " && ".join(s.cmd for s in rb.steps)
    p = subprocess.run(
        ["docker", "run", "--rm", image, "bash", "-lc", script],
        capture_output=True, text=True,
    )
    return [StepResult(f"(docker {image}) full runbook", p.returncode,
                       (p.stdout + p.stderr).strip()[-1000:])]


def validate(rb: Runbook, docker_image: str | None = None) -> tuple[bool, list[StepResult]]:
    results = _run_docker(rb, docker_image) if docker_image else _run_local(rb)
    ok = all(r.exit_code == 0 for r in results)
    return ok, results

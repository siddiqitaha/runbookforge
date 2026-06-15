"""`rbf` command-line entrypoint."""
from __future__ import annotations

import argparse
import sys

from .capture import capture
from .distill import distill
from .validate import validate
from .publish import publish
from .models import Session, Runbook


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rbf", description="RunbookForge")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("capture", help="record an interactive build session")
    p.add_argument("-o", "--out", default="session.json")
    p.add_argument("-t", "--title")

    p = sub.add_parser("distill", help="session.json -> runbook.yaml (golden path)")
    p.add_argument("session", nargs="?", default="session.json")
    p.add_argument("-o", "--out", default="runbook.yaml")
    p.add_argument("-t", "--title")

    p = sub.add_parser("validate", help="replay a runbook on a clean environment")
    p.add_argument("runbook", nargs="?", default="runbook.yaml")
    p.add_argument("--docker", metavar="IMAGE", help="validate inside this docker image")

    p = sub.add_parser("publish", help="render a runbook into a docs site")
    p.add_argument("runbook", nargs="?", default="runbook.yaml")
    p.add_argument("-o", "--out", default="site")
    p.add_argument("--build", action="store_true", help="run `mkdocs build`")

    args = parser.parse_args(argv)

    if args.command == "capture":
        capture(args.out, args.title)
        return 0

    if args.command == "distill":
        rb = distill(Session.from_json(args.session), args.title)
        rb.to_yaml(args.out)
        print(f"Distilled {len(rb.steps)} steps → {args.out}")
        return 0

    if args.command == "validate":
        rb = Runbook.from_yaml(args.runbook)
        ok, results = validate(rb, args.docker)
        for r in results:
            mark = "✓" if r.exit_code == 0 else "✗"
            print(f"  {mark} ({r.exit_code}) {r.cmd}")
            if r.exit_code != 0 and r.output_tail:
                print(f"      {r.output_tail}")
        print("\nRESULT:", "PASS — runbook reproduces" if ok else "FAIL — runbook is not reproducible")
        return 0 if ok else 1

    if args.command == "publish":
        rb = Runbook.from_yaml(args.runbook)
        out = publish(rb, args.out, build=args.build)
        print(f"Published → {out}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

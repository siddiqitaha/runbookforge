# RunbookForge

Turn a **messy, trial-and-error build** into a **clean, validated runbook** — automatically.

You build something the hard way (dead ends, half-remembered commands). RunbookForge records what
you actually did, distills the *golden path* that worked, **re-runs it on a clean environment to prove
it's correct**, and publishes a polished docs site.

## Install

```bash
pip install -e .          # or: pip install runbookforge
```

This installs the `rbf` command.

## The pipeline

```
 rbf capture  ─►  rbf distill  ─►  rbf validate  ─►  rbf publish
 (record)        (golden path)    (clean replay)    (docs site)
```

### 1. Capture
```bash
rbf capture -o session.json
```
Runs an interactive shell that executes and records each command (with exit codes and output).
`cd` is tracked so later steps see the right directory. Type `:done` to finish.

### 2. Distill
```bash
rbf distill session.json -o runbook.yaml
```
Drops failed attempts, navigation/inspection noise (`ls`, `cd`, `cat`…), and duplicate commands,
leaving the minimal sequence that actually worked.

### 3. Validate
```bash
rbf validate runbook.yaml                 # replays in a fresh temp dir
rbf validate runbook.yaml --docker python:3.12-slim   # or in a clean container
```
Replays the runbook on a clean environment and **fails loudly** if any step doesn't reproduce.
Exit code is non-zero on failure, so it drops straight into CI.

### 4. Publish
```bash
rbf publish runbook.yaml -o site --build  # --build runs mkdocs (needs the [docs] extra)
```
Renders the runbook to Markdown + an MkDocs site.

## Try it now

```bash
rbf distill examples/session.example.json -o runbook.yaml
rbf validate runbook.yaml      # → PASS, reproduces on a clean temp dir
rbf publish runbook.yaml -o site
```

## Design

- **Pluggable stages** — `capture`, `distill`, `validate`, `publish` are independent modules; swap or
  extend any of them.
- **Clean-room validation** — a runbook isn't "done" until it passes where nothing was set up before.

```
runbookforge/
  capture.py   distill.py   validate.py   publish.py   models.py   cli.py
```

## Tests

```bash
pip install pytest && pytest
```

## License

MIT

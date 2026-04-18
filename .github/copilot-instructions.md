# ppnotify – Copilot Instructions

## Project overview
`ppnotify` is a Python CLI tool and importable library for sending notifications to **Slack** and **MS Teams**. Message content is read from stdin. The default method is `teams`.

## Build, lint, and test

```bash
# Install dependencies and build
pip install -U pip setuptools wheel build pycodestyle
pip install .

# Lint (max line length 120)
pycodestyle --max-line-length=120 ppnotify

# Smoke-test the installed CLI
python -m ppnotify --version
ppnotify --help
```

There is no automated test suite beyond the pycodestyle lint and CLI smoke tests (see `.github/workflows/test.yml`). Tests run against Python 3.8–3.14.

## Release workflow
- Pushing a **tag** triggers the `main.yml` workflow: build → publish to TestPyPI → publish to PyPI (OIDC trusted publishing, no tokens in code).
- Non-`main` branch pushes trigger the `test.yml` workflow (lint + smoke tests only).
- Version is defined in `ppnotify/__version__.py` and read dynamically by `pyproject.toml`.

## Architecture

| File | Role |
|---|---|
| `ppnotify/main.py` | CLI entry point. Reads stdin, dispatches to `Slack` or `Teams`. |
| `ppnotify/slack.py` | `Slack` class – wraps `slack_sdk.WebClient`. Resolves recipients by email, `@username`, channel name, or username. Splits long code blocks at ~3800 chars. |
| `ppnotify/teams.py` | `Teams` class – posts Adaptive Card payloads via webhook. Handles retries with exponential backoff + jitter. |
| `ppnotify/__init__.py` | Re-exports `Slack` and `Teams` for library use (both are eagerly imported). |

## Configuration
Config is read via `ppconfig.Config('ppnotify')` → `~/.config/ppnotify` (override with `$XDG_CONFIG_HOME`).

```ini
[default]
slack_key = <Bot OAuth token>
email_domain = example.com

[teams]
webhook_url = https://...          # default webhook
channel1 = team_id,channel_id      # OR
channel2 = https://dedicated-url   # per-channel webhook
```

For Teams, if the value of a channel key starts with `https://`, it is used directly as the webhook URL; otherwise it is parsed as `team_id,channel_id` and the default `webhook_url` is used.

## Key conventions
- **`argparse` runs at module level** in `main.py` (not inside `main()`), so `parse_args()` is called on import. Keep this in mind when writing tests or importing `main.py` directly.
- **Teams is single-recipient**: the CLI passes only `args.recipients[0]` to `Teams(channel)`. The `Slack.send()` method accepts a list; `Teams.send()` does not take a recipients argument at all — the channel is fixed at construction time.
- **Lazy vs eager imports**: `Slack` and `Teams` are imported lazily inside the dispatch block in `main.py`. Importing from `ppnotify` directly (e.g. `from ppnotify import Slack`) triggers both imports via `__init__.py`.
- **Slack recipient resolution order**: email address containing `@<email_domain>` → `@username` → channel name → username. Only non-deleted, non-bot members are considered.
- **Teams indentation preservation**: each line is prefixed with a zero-width space (`\u200B`) and spaces replaced with non-breaking spaces (`\u00A0`) to work around Adaptive Cards collapsing whitespace. Lines are joined with `'   \n'` (three trailing spaces) to force Markdown line breaks.
- **URL auto-linking in Teams**: bare URLs are wrapped as `[url](url)` via `_url_replacer` using the regex `r'(?<!]\()https?://\S+'`; URLs already inside `(…)` are skipped via negative lookbehind.
- **Code blocks**: `-H/--code` flag sets `fontType: Monospace` in Teams cards; wraps text in triple-backticks for Slack, chunked at 3800 chars per message.
- **Exit behaviour**: `main()` calls `sys.exit(0)` on non-fatal conditions (nothing to send, unknown method, or caught exception) and logs at `critical` level rather than raising.
- All source files use `# -*- coding: utf-8 -*-` headers with the GPLv3 copyright block.

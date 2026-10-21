"""Opt-in Claude Code hooks for meta-harness lanes.

Nothing in harness/, scripts/ or CI imports this package; it runs only when a lane installs a hook in its own
.claude/settings.local.json (see agent_hooks/README.md). Ported from e156-ecosystem-starter
scripts/protect-test-config.py (v1.0.0, 2026-10-21) and adapted to this repo's gates.
"""
from __future__ import annotations

__version__ = "1.0.0"

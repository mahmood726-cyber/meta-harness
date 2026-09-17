"""External topic identifiers used by legacy policies and acquisition recipes.

New strand membership lives in each topic configuration, never in this registry.
This registry preserves existing policies without embedding page slugs in code.
"""
import json
from pathlib import Path

_IDENTIFIERS = json.loads((Path(__file__).resolve().parents[1] /
                          'registry/topic_identifiers.json').read_text(encoding='utf-8'))


def topic_id(role):
    return _IDENTIFIERS[role]

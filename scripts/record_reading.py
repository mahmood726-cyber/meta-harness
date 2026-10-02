"""Record an integrator-supplied reading offline; provider identity is self-reported."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from reproducible_ai import model_source as ms


def build_reading(reading_bytes, prompt_bytes, reference, *, provider, model, request_utc, response_utc):
    ms.replay(reference)  # verifies immutable reference bytes before using its prompt/input pins
    if hashlib.sha256(prompt_bytes).hexdigest() != reference['prompt']['sha256']:
        raise ValueError('PROMPT_REFUSED: reading must use the SAME prompt bytes as the reference')
    if not isinstance(json.loads(reading_bytes), dict):
        raise ValueError('READING_REFUSED: JSON object required')
    if provider.strip().casefold() == reference['model']['provider'].strip().casefold():
        raise ValueError('PROVIDER_REFUSED: additional reading requires a different provider')
    inputs = [dict(d) for d in reference['input_digests'] if d.get('media_type', '').startswith('image/')]
    return ms.build_record(prompt_bytes=prompt_bytes, response_bytes=reading_bytes,
        model={'provider': provider, 'id_requested': model, 'id_reported': model,
               'reported_by': 'self-reported by in-session assistant; not a server attestation'},
        params={}, not_controllable=['all generation parameters', 'temperature', 'top_p', 'seed',
            'reasoning effort', 'token budget', 'server-side model revision', 'system/developer instructions',
            'prior conversation/context', 'image preprocessing', 'tools', 'provider/model identity attestation'],
        client={'name': 'in-session assistant reading'}, request_utc=request_utc, response_utc=response_utc,
        caller={'file': 'scripts/record_reading.py', 'line': 'build_reading',
                'purpose': 'Recorded self-reported cross-provider reading; never a server attestation',
                'lane': reference.get('caller', {}).get('lane')}, input_digests=inputs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('reading', 'prompt', 'reference-record', 'provider', 'model', 'request-utc', 'response-utc', 'output-dir'):
        ap.add_argument('--' + flag, required=True)
    args = ap.parse_args(argv)
    try:
        rec = build_reading(Path(args.reading).read_bytes(), Path(args.prompt).read_bytes(),
            ms.load_record(args.reference_record), provider=args.provider, model=args.model,
            request_utc=args.request_utc, response_utc=args.response_utc)
        print(ms.write_record(rec, Path(args.output_dir)))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'REFUSED', 'reason': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

"""Explicit typed prose construction, before HTML rendering (no text scraping).

Owners supply named computations and structured inputs. The graph recomputes
transformations independently of the stored value and validates rendered bytes.
"""
from __future__ import annotations

from . import claimgraph


class Writer:
    def __init__(self, graph, prefix):
        self.graph = graph
        self.prefix = prefix

    def add(self, key, kind, **fields):
        cid = self.prefix + '-' + key
        self.graph.add(cid, kind, **fields)
        return self.ref(cid)

    @staticmethod
    def ref(cid):
        return '<!--claim:' + cid + '-->'

    def computation(self, key, inputs, unit=None, **fields):
        from . import manuscript, risk_prose
        owner = {'manuscript': manuscript, 'risk': risk_prose}[self.prefix]
        unit = unit or key
        return self.add(key, 'TRANSFORMATION', operation='section_text',
                        owner=self.prefix, unit=unit, inputs=inputs,
                        value=owner.compute(unit, inputs), **fields)

    def judgement(self, key, text, basis, owed=False):
        return self.add(key, 'JUDGEMENT', text=text, basis=basis,
                        adjudication='OWED' if owed else 'RULE')

    def interpretation(self, key, text, alternative, **fields):
        return self.add(key, 'INTERPRETATION', text=text, alternatives=[alternative], **fields)

    def effect_display(self, key, input_ref, mode):
        reference = self.add(key, 'TRANSFORMATION', operation='section_effect_display',
                             input_ref=input_ref, depends_on=[input_ref], mode=mode, value=None)
        cid = self.prefix + '-' + key
        try:
            self.graph.objects[cid]['value'] = self.graph.recompute(cid)
        except (ValueError, KeyError, TypeError, ZeroDivisionError):
            pass
        return self.svg(reference)

    def finish(self, document):
        for cid, rendered in self.graph.render_all().items():
            document = document.replace(self.ref(cid), rendered)
            svg = (rendered.replace('<span', '<tspan').replace('</span>', '</tspan>')
                   .replace('<strong>', '').replace('</strong>', ''))
            document = document.replace('<!--svgclaim:' + cid + '-->', svg)
        return document

    @staticmethod
    def svg(reference):
        return reference.replace('<!--claim:', '<!--svgclaim:')


def register_pool(graph, cid, trials, scale, label):
    """Reported effects require held source evidence, and are freshly pooled.

    Unsupported input types remain an explicit refusal; no copied pool is
    upgraded to a recomputed result just because it is present in review.json.
    """
    refs = []
    for trial in trials:
        row = dict(trial, scale=trial.get('scale') or scale)
        ref = 'fact-' + claimgraph._sha(row)[:16]
        if ref not in graph.objects:
            graph.add(ref, 'FACT', row=row)
        refs.append(ref)
    graph.add(cid, 'TRANSFORMATION', operation='reported_effect_pool', scale=scale,
              input_refs=refs, depends_on=sorted(set(refs)), label=label,
              precision=2, value=None)
    try:
        graph.objects[cid]['value'] = graph.recompute(cid)
    except (ValueError, KeyError, TypeError, ZeroDivisionError):
        pass  # The registered transformation renders UNRENDERABLE, never a fake pool.
    return Writer.ref(cid)

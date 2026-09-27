"""Denominators belong to the class whose measurements are read."""


def denominator_blocks(measure, selected_class):
    """Use the entire class block when present; never fill missing arms from FAS."""
    return (selected_class or {}).get("denoms") or measure.get("denoms") or []


def denominator_counts(blocks, convert=lambda value: value):
    return {count.get("groupId"): convert(count.get("value"))
            for block in blocks for count in block.get("counts") or []}


def analysis_set_metadata(measure, selected_class, intervention, comparator, convert):
    if not (selected_class or {}).get("denoms"):
        return {}
    counts = denominator_counts(measure.get("denoms") or [], convert)
    return {"n_source": "class-level denominators of the class read",
            "n_analysis_set": {"n1i": counts.get(intervention), "n2i": counts.get(comparator)}}

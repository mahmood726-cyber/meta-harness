"""Single build/render contract for the GS objects."""
from . import envelope, fragility, decomposer


def build(review, root=envelope.ROOT):
    env = envelope.build(review, root)
    return {'envelope': env, 'fragility': fragility.build(review, env, root),
            'decomposer': decomposer.build(review, env, root)}


def render(objects):
    return '<div id="gs-statistical-layers">' + envelope.render(objects['envelope']) + fragility.render(objects['fragility']) + decomposer.render(objects['decomposer']) + '</div>'

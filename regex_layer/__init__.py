"""The regex layer, measured: every extraction pattern has a written specification (what it should find, in plain
words), a named plant (a planted input it must accept and one it must refuse, with a mutation proving the plant can
fire), and a measured precision and recall against labelled spans from held sources.

Kept OUT of harness/ on purpose: every CERTIFICATE.json lists harness/*.py outside its closure, so a new module there
re-certifies 32 pages for code no page runs (see reproducible_ai/__init__.py). Nothing under harness/ imports this
package; it only READS the harness's compiled patterns.
"""

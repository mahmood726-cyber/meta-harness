"""Round-3 limitations, reconstructed from the captain's finding descriptions.

The full reviewer reproductions were not supplied; exact-input fidelity awaits
that review. These synthetic plants are not research evidence or parser fixes.
"""
import xml.etree.ElementTree as ET

import pytest

from harness import typed_routes as tr
from harness.table_rows import read_row


def table(header, body):
    return ('<table-wrap><label>T</label><table>' + header + '<tbody>' + body
            + '</tbody></table></table-wrap>')


def read(text):
    return read_row(text, table_label='T', row_label='Any AE',
                    intervention='Drug', comparator='Placebo')[0]


def header(denom='N=100'):
    return ('<thead><tr><th>Outcome</th><th>Drug ' + denom + ' n (%)</th>'
            '<th>Placebo ' + denom + ' n (%)</th></tr></thead>')


ZERO_ROW = '<tr><td>Any AE</td><td>0 (0.0)</td><td>0 (0.0)</td></tr>'


@pytest.mark.xfail(strict=True, raises=AssertionError, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P1-3 dual-N label after its N')
def test_dual_n_label_after_n():
    got = read(table(header('N=99 safety; N=100 randomised'), ZERO_ROW))
    assert (got['n1i'], got['n2i']) == (99, 99)


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P1-4 but clause binds another endpoint')
def test_hr_but_clause():
    with pytest.raises(ValueError):
        tr.sentence_hr('Hospitalization for heart failure was unchanged, but cardiovascular mortality was reduced (HR 0.70; 95% CI, 0.60 to 0.90).')


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P1-4 prior hospitalization is not the measured endpoint')
def test_hr_prior_hospitalization():
    with pytest.raises(ValueError):
        tr.sentence_hr('Among patients with prior hospitalization for heart failure, cardiovascular mortality was reduced (HR 0.70; 95% CI, 0.60 to 0.90).')


@pytest.mark.xfail(strict=True, raises=AssertionError, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P1-5 body-row rowspan shifts arm columns')
def test_body_rowspan_column_shift():
    h = ('<thead><tr><th>Group</th><th>Outcome</th><th>Drug N=100 n (%)</th>'
         '<th>Placebo N=100 n (%)</th><th>Other N=100 n (%)</th></tr></thead>')
    body = ('<tr><td rowspan="2">Safety</td><td>Other AE</td><td>0 (0.0)</td><td>0 (0.0)</td><td>0 (0.0)</td></tr>'
            '<tr><td>Any AE</td><td>10 (10.0)</td><td>20 (20.0)</td><td>30 (30.0)</td></tr>')
    assert read(table(h, body)) == dict(ai=10, n1i=100, ci=20, n2i=100)


@pytest.mark.xfail(strict=True, raises=ET.ParseError, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P2-1 nbsp header aborts with ParseError')
def test_nbsp_header():
    assert read(table(header().replace('Drug ', 'Drug&nbsp;'), ZERO_ROW))['n1i'] == 100


@pytest.mark.xfail(strict=True, raises=AttributeError, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P2-1 no thead aborts with AttributeError')
def test_no_thead():
    # A typed refusal would be acceptable; an unhandled AttributeError is not.
    try:
        read(table(header().replace('<thead>', '').replace('</thead>', ''), ZERO_ROW))
    except ValueError:
        pass


@pytest.mark.xfail(strict=True, raises=AssertionError, reason='KNOWN LIMIT (b1 r3, review closed at three rounds): P2-3 N = 1,067 read as 1')
def test_thousands_separator_n():
    got = read(table(header('N = 1,067'), ZERO_ROW))
    assert (got['n1i'], got['n2i']) == (1067, 1067)

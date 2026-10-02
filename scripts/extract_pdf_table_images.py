"""Offline DISPERSE-2 image inventory; page-level captions are candidates, not OCR."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = Path('evidence/acquisition_cascade/held/PLATO-regulatory/022433Orig1s000MedR.pdf')
MENTION = re.compile(r'\b(?:DISPERSE[\s-]*2|D5130C00002)\b', re.I)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def captions(text):
    return [m.group().strip() for m in re.finditer(
        r'(?m)^\s*Table\s+\d+[. :][^\n]*(?:\n(?!\s*$|\s*(?:Table|Source|===))[^\n]+)?', text)]


def image_context(reader, rendered_page, page_number, rectangle):
    """Nearest caption above the image; last study-section heading before that caption."""
    blocks = [b for b in rendered_page.get_text('blocks')
              if b[3] <= rectangle.y0 + 2 and re.match(r'\s*Table\s+\d+[. :]', b[4])]
    if not blocks:
        return {'bound_caption': None, 'study': 'UNKNOWN'}
    block = max(blocks, key=lambda b: b[3])
    number = re.search(r'Table\s+(\d+)', block[4])[1]
    page_text = reader.pages[page_number - 1].extract_text() or ''
    cap = next((c for c in captions(page_text) if re.match(r'Table\s+' + number + r'\b', c)), None)
    if cap is None:
        return {'bound_caption': None, 'study': 'UNKNOWN'}
    prefix = page_text[:page_text.index(cap)]
    heading = re.compile(r'8\.2\.\d+\s+(DISPERSE(?:-2)?)\s*\[Study', re.I)
    for index in range(page_number - 1, -1, -1):
        text = prefix if index == page_number - 1 else (reader.pages[index].extract_text() or '')
        matches = list(heading.finditer(text))
        if matches:
            return {'bound_caption': cap, 'study': matches[-1][1].upper()}
    return {'bound_caption': cap, 'study': 'UNKNOWN'}


def extract(root=ROOT):
    from pypdf import PdfReader
    import fitz
    root = Path(root)
    source = root / PDF
    out = root / '.tmp/disp2img'
    out.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(source)
    rendered = fitz.open(source)
    pages, images = [], []
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        if not MENTION.search(text):
            continue
        caps = captions(text)
        page_images = list(page.images)
        pages.append({'page': number, 'image_count': len(page_images), 'captions': caps,
                      'text': text, 'text_sha256': digest(text.encode('utf-8'))})
        for index, img in enumerate(page_images, 1):
            sha = digest(img.data)
            suffix = Path(img.name).suffix.lower()
            name = f'page-{number:04d}-image-{index:02d}-{sha[:12]}{suffix}'
            (out / name).write_bytes(img.data)
            # Malformed indexed palettes in this held PDF yield black pypdf exports.
            # Preserve those exact exports and separately render the PDF image rectangle.
            xref = img.indirect_reference.idnum
            rectangles = rendered[number - 1].get_image_rects(xref)
            if len(rectangles) != 1:
                raise ValueError(f'REFUSED_IMAGE_PLACEMENT: page {number}, xref {xref}')
            pix = rendered[number - 1].get_pixmap(matrix=fitz.Matrix(2, 2), clip=rectangles[0], alpha=False)
            display = pix.tobytes('png')
            display_name = f'page-{number:04d}-image-{index:02d}-rendered.png'
            (out / display_name).write_bytes(display)
            extrema = img.image.convert('L').getextrema()
            images.append({'page': number, 'image_index': index, 'pdf_image_name': img.name,
                           **image_context(reader, rendered[number - 1], number, rectangles[0]),
                           'path': (Path('.tmp/disp2img') / name).as_posix(), 'sha256': sha,
                           'width': img.image.width, 'height': img.image.height,
                           'xref': xref, 'raw_export_uniform': extrema[0] == extrema[1],
                           'rendered_path': (Path('.tmp/disp2img') / display_name).as_posix(),
                           'rendered_sha256': digest(display), 'rendered_width': pix.width,
                           'rendered_height': pix.height, 'rectangle': list(rectangles[0]),
                           'table_status': 'CAPTION_CANDIDATE' if caps else 'UNCLASSIFIED',
                           'caption_scope': 'PAGE_ONLY_NOT_SPATIAL_BINDING', 'captions': caps,
                           'outcome_hints': sorted(set(re.findall(
                               r'bleeding|dyspn(?:ea|oea)|myocardial infarction|\bMI\b|death|composite|pauses',
                               text, re.I)))})
    manifest = {'version': 1, 'source': PDF.as_posix(), 'source_sha256': digest(source.read_bytes()),
                'pages_examined': len(reader.pages), 'mention_pages': pages, 'images': images}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    rendered.close()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = extract(args.root)
    print(json.dumps({'pages_examined': result['pages_examined'],
                      'mention_pages': [p['page'] for p in result['mention_pages']],
                      'images': len(result['images']), 'manifest': '.tmp/disp2img/manifest.json'}, indent=2))


if __name__ == '__main__':
    main()

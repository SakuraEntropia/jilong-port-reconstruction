"""Lay out genuine Blender renders for quick review; no generated imagery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
VIEWS = (
    ('01_hero_daylight.png', '01  BRIDGE-FACING ELEVATION'),
    ('02_oblique_daylight.png', '02  THREE-QUARTER STRUCTURE'),
    ('03_rear_daylight.png', '03  REAR ELEVATION / INFERRED DETAILS'),
    ('04_portal_detail.png', '04  NESTED PORTAL AND FACADE'),
    ('05_site_overview.png', '05  APPROXIMATE SITE AND VALLEY'),
    ('06_dusk.png', '06  DUSK / ART-DIRECTED LIGHTING'),
)


def _font(size):
    for font in ('/System/Library/Fonts/Supplemental/Arial.ttf', 'DejaVuSans.ttf', 'Arial.ttf'):
        try:
            return ImageFont.truetype(font, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def make_contact_sheet(base=BASE):
    base = Path(base)
    missing = [name for name, _ in VIEWS if not (base / 'renders' / name).is_file()]
    if missing:
        raise RuntimeError('Contact sheet requires all six final renders: ' + ', '.join(missing))
    sheet = Image.new('RGB', (2100, 2260), (24, 29, 31))
    draw = ImageDraw.Draw(sheet)
    title, label, small = _font(48), _font(26), _font(23)
    draw.text((55, 35), 'JILONG PORT  /  2019 EXTERIOR', font=title, fill=(235, 232, 222))
    draw.text((57, 97), 'Editable architecture  |  Cycles PBR  |  Photograph-based reconstruction',
              font=small, fill=(160, 173, 171))
    for i, (name, caption) in enumerate(VIEWS):
        x, y = 55 + (i % 2) * 1025, 170 + (i // 2) * 660
        with Image.open(base / 'renders' / name) as source:
            source.load()
            img = source.convert('RGB')
        img.thumbnail((970, 600), Image.Resampling.LANCZOS)
        sheet.paste(img, (x + (970 - img.width) // 2, y))
        draw.text((x, y + 612), caption, font=label, fill=(210, 215, 210))
    draw.text((57, 2170),
              'Building dimensions, hidden rear geometry and terrain remain estimated. See research and QA files.',
              font=small, fill=(159, 172, 170))
    output = base / 'renders' / 'contact_sheet.jpg'
    temporary = output.with_name(output.name + '.tmp')
    try:
        sheet.save(temporary, format='JPEG', quality=94)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(output)
    return output


if __name__ == '__main__':
    make_contact_sheet()

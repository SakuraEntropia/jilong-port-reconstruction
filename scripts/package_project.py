"""Package real local artifacts after final scene and image validation."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import os
import zipfile

BASE = Path(__file__).resolve().parent.parent
FINAL_RENDERS = (
    '01_hero_daylight.png', '02_oblique_daylight.png', '03_rear_daylight.png',
    '04_portal_detail.png', '05_site_overview.png', '06_dusk.png',
)


def _digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _archive_files(base):
    return sorted(p for p in base.rglob('*')
                  if p.is_file() and not p.is_symlink()
                  and '__pycache__' not in p.parts
                  and p.suffix not in ('.pyc', '.blend1', '.blend2')
                  and p.name not in ('.DS_Store', 'project_manifest.json'))


def build_package(base=BASE):
    base = Path(base).resolve()
    validation = base / 'logs' / 'validation.json'
    report = json.loads(validation.read_text())
    checks = report.get('checks', {})
    if not report.get('passed') or not all(checks.values()) or not checks.get('final_images_decoded'):
        raise RuntimeError('Full final scene and decoded-image validation must pass before packaging.')
    main = base / 'Jilong_Port_2019.blend'
    if Path(report.get('blend', '')).resolve() != main:
        raise RuntimeError('validation.json must describe this project\'s final daylight scene.')
    required = [main, base / 'Jilong_Port_2019_Dusk.blend', base / 'renders' / 'contact_sheet.jpg',
                base / 'README.md', base / 'QA.md', base / 'PLAN.md']
    required += [base / 'renders' / name for name in FINAL_RENDERS]
    required += [base / 'research' / name for name in
                 ('architecture.md', 'source_index.md', 'dimensions.md', 'uncertainties.md')]
    missing = [str(p.relative_to(base)) for p in required if not p.is_file() or p.stat().st_size == 0]
    if missing:
        raise RuntimeError('Required delivery artifacts missing or empty: ' + ', '.join(missing))
    decoded = {r['name']: r for r in report.get('renders', [])}
    for name in FINAL_RENDERS:
        path = base / 'renders' / name
        image = decoded.get(name)
        if not image or image.get('width', 0) < 1800 or image.get('pixel_range', 0) <= .08:
            raise RuntimeError('Expected final image was not successfully decoded: ' + name)
        if path.stat().st_size != image.get('file_bytes'):
            raise RuntimeError('Final image changed after validation: ' + name)
    validated_artifacts = [main, base / 'Jilong_Port_2019_Dusk.blend']
    validated_artifacts += [base / 'renders' / name for name in FINAL_RENDERS]
    if any(p.stat().st_mtime > validation.stat().st_mtime for p in validated_artifacts):
        raise RuntimeError('A scene or render changed after validation; reopen and validate the final main file again.')

    files = _archive_files(base)
    manifest = {
        'created': datetime.now(ZoneInfo('Asia/Singapore')).isoformat(),
        'target': 'Jilong Port Resuo gate, 2019 front baseline',
        'scope': 'Editable PBR exterior; hidden geometry and terrain inferred',
        'validation': {
            'report': 'logs/validation.json', 'main_scene_reopened': True,
            'six_final_images_decoded': True,
            'dusk_scene': 'Saved rendered lighting variant; not independently reopened by this report',
        },
        'blender': report['blender_version'], 'scene_objects': report['objects'],
        'material_count': report['PBR_materials'],
        'checksum_note': 'Every archived file except this manifest is listed below.',
        'files': [{'path': str(p.relative_to(base)), 'bytes': p.stat().st_size,
                   'sha256': _digest(p)} for p in files],
    }
    manifest_path = base / 'project_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    output = base.parent / (base.name + '.zip')
    temporary = output.with_name(output.name + f'.{os.getpid()}.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in [*files, manifest_path]:
                archive.write(path, str(Path(base.name) / path.relative_to(base)))
        with zipfile.ZipFile(temporary, 'r') as archive:
            damaged = archive.testzip()
            if damaged:
                raise RuntimeError('Archive integrity check failed: ' + damaged)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print('PACKAGE', output, 'bytes', output.stat().st_size)
    return output


if __name__ == '__main__':
    build_package()

"""Create reproducible-ish release archives and a SHA-256 manifest."""
from __future__ import annotations
import hashlib, tarfile, zipfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    """Package the project while excluding PDFs, caches and local secrets."""
    root = Path(__file__).resolve().parents[1]; out = root.parent
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    files = []
    excluded = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'data/backup', 'data/tmp', 'data/quarantine'}
    for path in sorted(root.rglob('*')):
        if not path.is_file(): continue
        rel = path.relative_to(root)
        if path.suffix.lower() == '.pdf' or any(str(rel) == x or str(rel).startswith(x + '/') for x in excluded): continue
        files.append((path, rel))
    manifest = root / 'MANIFEST.txt'
    manifest.write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {r}' for p,r in files) + '\n', encoding='utf-8')
    files.append((manifest, manifest.relative_to(root)))
    zip_path, tar_path = out / f'sim800-platform-all-{stamp}.zip', out / f'sim800-platform-all-{stamp}.tar.gz'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for p,r in files: z.write(p, Path(root.name)/r)
    with tarfile.open(tar_path, 'w:gz') as t:
        for p,r in files: t.add(p, arcname=Path(root.name)/r)
    print(zip_path); print(tar_path); return 0

if __name__ == '__main__': raise SystemExit(main())

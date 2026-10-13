"""Verify only an explicitly supplied offline bundle; no save/world discovery."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(root, archive=None):
    root = root.resolve()
    manifest = json.loads((root / 'M121_SHA256_MANIFEST.json').read_text(encoding='utf-8'))
    entries = manifest['entries']
    assert len(entries) == manifest['total_files_except_manifest'] == 45
    names = [entry['relative_path'] for entry in entries]
    assert len(set(names)) == len(names)
    expected = set(names) | {'M121_SHA256_MANIFEST.json'}
    for entry in entries:
        name = PurePosixPath(entry['relative_path'])
        assert not name.is_absolute() and '..' not in name.parts
        path = root.joinpath(*name.parts).resolve()
        assert path.is_relative_to(root)
        data = path.read_bytes()
        assert len(data) == entry['bytes'], str(name)
        assert digest(data) == entry['sha256'], str(name)
    inherited = {}
    for phase in ('M119', 'M120'):
        files = json.loads((root / f'{phase}_FILE_SHA256_MANIFEST.json').read_text(encoding='utf-8'))['files']
        checked = 0
        skipped = 0
        for name, sha in files.items():
            if '__pycache__' in PurePosixPath(name).parts:
                skipped += 1
                continue
            path = root.joinpath(*PurePosixPath(name).parts).resolve()
            assert path.is_relative_to(root)
            assert digest(path.read_bytes()) == sha, name
            checked += 1
        inherited[phase] = {'verified': checked, 'omitted_original_pyc': skipped}
    result = {'manifest_files_verified': len(entries), 'inherited': inherited}
    if archive:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            members = z.namelist()
            assert len(members) == len(set(members)) == len(expected)
            assert set(members) == {'M121/' + name for name in expected}
            for name in sorted(expected):
                assert z.read('M121/' + name) == (root / name).read_bytes(), name
        result.update(archive_sha256=digest(archive.read_bytes()), zip_members_verified=len(expected),
                      archive_hash_trust='computed local fingerprint; independent M121 ZIP expected hash unavailable')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle, args.archive), indent=2))

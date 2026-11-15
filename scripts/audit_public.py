#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fail closed: audit the public file allowlist, index, and reachable Git history."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    '.gitignore', '.gitattributes', 'VERSION', 'LICENSE', 'README.md', 'NOTICE.md',
    'CHANGELOG.md', 'build.py', 'sources.lock.json', 'rom-manifest.json',
    'publish-manifest.json', 'patches/port.patch', 'scripts/audit_public.py',
    'scripts/run-bazzite.sh', 'tests/test_kit.py', '.github/workflows/audit.yml',
}
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
PERSONAL = re.compile(rb'(?:[CD]:[\\/]Users[\\/]|192\.168\.\d+\.\d+|[\w.+-]+@(?:gmail|hotmail|outlook)\.com)', re.I)


def inspect(name, data):
    if name not in ALLOWED:
        raise ValueError(f'Unapproved public path: {name}')
    if len(data) > 250_000 or b'\0' in data:
        raise ValueError(f'Binary or oversized public file: {name}')
    data.decode('utf-8')
    if SECRET.search(data) or PERSONAL.search(data):
        raise ValueError(f'Sensitive content in {name}')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    manifest = json.loads((ROOT / 'publish-manifest.json').read_text())
    if set(manifest) != ALLOWED - {'publish-manifest.json'}:
        raise ValueError('Publication manifest differs from the reviewed file allowlist')
    for name, expected in manifest.items():
        data = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
        inspect(name, data)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Changed file requires review and manifest update: {name}')
    inspect('publish-manifest.json', (ROOT / 'publish-manifest.json').read_bytes())
    if (ROOT / '.git').exists():
        names = git('ls-files', '-z').decode().split('\0')
        tracked = set(filter(None, names))
        if tracked != ALLOWED:
            raise ValueError(f'Git index differs from allowlist: {tracked ^ ALLOWED}')
        for name in tracked:
            data = git('show', ':' + name).replace(b'\r\n', b'\n')
            inspect(name, data)
            if name in manifest and hashlib.sha256(data).hexdigest() != manifest[name]:
                raise ValueError(f'Staged content differs from reviewed file: {name}')
        seen = set()
        for commit in git('rev-list', '--all').decode().splitlines():
            for entry in git('ls-tree', '-r', '-z', commit).split(b'\0'):
                if not entry:
                    continue
                meta, name = entry.split(b'\t', 1)
                mode, kind, sha = meta.split()
                path = name.decode()
                if path not in ALLOWED or kind != b'blob' or mode not in (b'100644', b'100755'):
                    raise ValueError(f'Unapproved historical path/type: {path}')
                if sha not in seen:
                    inspect(path, git('cat-file', 'blob', sha.decode()))
                    seen.add(sha)
    print(f'Public audit passed: {len(ALLOWED)} text files; index/history checked when available.')


if __name__ == '__main__':
    main()

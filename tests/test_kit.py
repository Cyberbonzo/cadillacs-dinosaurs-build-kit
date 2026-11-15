# SPDX-License-Identifier: GPL-3.0-only
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


build = module('kit_build', ROOT / 'build.py')
audit = module('kit_audit', ROOT / 'scripts/audit_public.py')


class KitTests(unittest.TestCase):
    def test_correct_rom_and_repacked_zip(self):
        data = b'Synthetic test bytes, not game content.'
        manifest = {'revision': 'test', 'files': [{'name': 'sample', 'size': len(data), 'sha1': hashlib.sha1(data).hexdigest()}]}
        with tempfile.TemporaryDirectory() as temp:
            for compression in [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED]:
                path = Path(temp) / 'synthetic.zip'
                with zipfile.ZipFile(path, 'w', compression=compression) as z:
                    z.writestr('sample', data)
                build.validate_rom(path, manifest)
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('sample', b'X' * len(data))
            with self.assertRaisesRegex(ValueError, 'hash'):
                build.validate_rom(path, manifest)
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('different', data)
            with self.assertRaisesRegex(ValueError, 'Missing'):
                build.validate_rom(path, manifest)

    def test_archive_escape_is_rejected(self):
        for name in ['../outside', '/absolute', 'C:/absolute', 'folder/../../outside', '..\\outside']:
            with self.assertRaises(ValueError):
                build.safe_path(name)
        build.safe_path('safe/path.cpp')

    def test_public_audit_rejects_assets_and_secrets(self):
        for name in ['dino.zip', 'dino.exe', 'generated/native_000.cpp', 'screenshot.png']:
            with self.assertRaises(ValueError):
                audit.inspect(name, b'synthetic')
        with self.assertRaises(ValueError):
            audit.inspect('README.md', b'\0binary')
        with self.assertRaises(ValueError):
            audit.inspect('README.md', b'gh' + b'p_' + b'a' * 40)


if __name__ == '__main__':
    unittest.main()

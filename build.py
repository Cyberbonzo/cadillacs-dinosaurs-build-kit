#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build the Windows/Proton port locally from a user-supplied ROM. Python 3.11+."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_rom(path, manifest):
    """Check individual ROM members; ZIP timestamps/compression do not matter."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP entries are not supported')
        for item in manifest['files']:
            name = item['name']
            if name not in names:
                raise ValueError(f'Missing ROM member: {name}; expected {manifest["revision"]}')
            info = archive.getinfo(name)
            if info.file_size != item['size']:
                raise ValueError(f'Incorrect ROM size: {name}')
            data = archive.read(name)
            if hashlib.sha1(data).hexdigest() != item['sha1']:
                raise ValueError(f'Incorrect ROM hash: {name}; expected {manifest["revision"]}')


def safe_path(name):
    path = PurePosixPath(name.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in name:
        raise ValueError(f'Unsafe archive path: {name}')


def unpack(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == '.zip':
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                safe_path(member.filename)
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Archive symlinks are not supported')
            z.extractall(destination)
    else:
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                safe_path(member.name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError('Only regular files/directories are supported')
            t.extractall(destination)


def fetch(item, cache):
    archive = cache / item['archive']
    if not archive.exists():
        print('Downloading', item['url'], flush=True)
        request = urllib.request.Request(item['url'], headers={'User-Agent': 'dino-build-kit/0.1.0'})
        temporary = archive.with_name(archive.name + '.part')
        with urllib.request.urlopen(request, timeout=90) as response, temporary.open('wb') as out:
            shutil.copyfileobj(response, out)
        if digest(temporary) != item['sha256']:
            raise ValueError(f'Download checksum mismatch: {archive.name}')
        temporary.replace(archive)
    if digest(archive) != item['sha256']:
        raise ValueError(f'Cached archive checksum mismatch: {archive.name}')
    return archive


def execute(args, *, cwd=None, env=None, log=None):
    args = [str(a) for a in args]
    print('+', subprocess.list2cmdline(args), flush=True)
    if log:
        with Path(log).open('w', encoding='utf-8') as output:
            result = subprocess.run(args, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
        if result.returncode:
            tail = Path(log).read_text(encoding='utf-8', errors='replace')[-6000:]
            raise RuntimeError(f'Command failed ({result.returncode}); {log.name}\n{tail}')
    else:
        subprocess.run(args, cwd=cwd, env=env, check=True)


def create_packages(source, build, sdl, rom, local, version):
    output = local / 'output'
    windows = output / f'Cadillacs-Dinosaurs-Windows-{version}'
    bazzite = output / f'Cadillacs-Dinosaurs-Bazzite-{version}'
    if windows.exists() or bazzite.exists():
        raise ValueError('Output already exists; choose another --work-dir')
    for package, game in [(windows, windows), (bazzite, bazzite / 'game')]:
        (game / 'roms').mkdir(parents=True)
        (game / 'user').mkdir()
        shutil.copy2(build / 'dino.exe', game / 'dino.exe')
        shutil.copy2(sdl / 'bin/SDL3.dll', game / 'SDL3.dll')
        shutil.copy2(rom, game / 'roms/dino.zip')
        (game / 'portable.txt').write_text('')
        (package / 'VERSION').write_text(version + '\n')
        (package / 'LOCAL-BUILD.txt').write_text(
            'Locally generated from your ROM. Contains game-derived code and ROM data.\n'
            'This output is not part of the public build kit. Do not upload it to the kit repository.\n')
        shutil.copy2(ROOT / 'LICENSE', package / 'LICENSE')
        shutil.copy2(ROOT / 'NOTICE.md', package / 'NOTICE.md')
        shutil.copytree(sdl / 'share/licenses', package / 'licenses', dirs_exist_ok=True)
        if (source / 'THIRD_PARTY_NOTICES.md').exists():
            shutil.copy2(source / 'THIRD_PARTY_NOTICES.md', package / 'THIRD_PARTY_NOTICES.md')
        if (source / 'licenses').exists():
            shutil.copytree(source / 'licenses', package / 'licenses', dirs_exist_ok=True)
    (windows / 'PLAY.cmd').write_bytes(
        b'@echo off\r\nset RECOMP_LANGUAGE=en\r\ncd /d "%~dp0"\r\n'
        b'start "" "%~dp0dino.exe" --rom roms\\dino.zip --cpu native --renderer sdl --video board '
        b'--fullscreen --features widescreen,free_play,display_shape=0,display_scaling=0,display_shader=0 '
        b'--settings user\\settings.ini --eeprom user\\eeprom.bin\r\n')
    shutil.copy2(ROOT / 'scripts/run-bazzite.sh', bazzite / 'jogar.sh')
    (bazzite / 'jogar.sh').chmod(0o755)
    for package in [windows, bazzite]:
        hashes = {p.relative_to(package).as_posix(): digest(p) for p in package.rglob('*') if p.is_file()}
        (package / 'SHA256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    with tarfile.open(output / f'{bazzite.name}.tar.gz', 'w:gz') as t:
        def permissions(member):
            member.uid = member.gid = 0
            member.uname = member.gname = ''
            member.mode = 0o755 if member.isdir() or member.name.endswith('/jogar.sh') else 0o644
            return member
        t.add(bazzite, arcname=bazzite.name, filter=permissions)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path, help='Your dino World 930201 ZIP; never uploaded')
    parser.add_argument('--verify-rom', action='store_true', help='Check the ROM locally, without downloads/build')
    parser.add_argument('--work-dir', type=Path, default=ROOT / '.local', help='Private build/output directory')
    parser.add_argument('--cache-dir', type=Path, help='Optional cache for hash-verified dependency archives')
    parser.add_argument('--jobs', type=int, default=min(os.cpu_count() or 2, 8))
    args = parser.parse_args()
    rom = args.rom.resolve(strict=True)
    validate_rom(rom, json.loads((ROOT / 'rom-manifest.json').read_text()))
    print('ROM verified: dino World 930201 (16 required members).', flush=True)
    if args.verify_rom:
        return
    if sys.platform != 'win32':
        raise ValueError('Version 0.1.0 builds on Windows x64; the output runs on Bazzite with Proton')
    if not shutil.which('git'):
        raise ValueError('Install Git for Windows and open a new terminal first')
    if args.jobs < 1:
        raise ValueError('--jobs must be positive')
    local = args.work_dir.resolve()
    # Generated proprietary data must never land in a public source folder.
    if local == ROOT or ROOT.is_relative_to(local):
        raise ValueError('--work-dir must not be the repository root or its parent')
    if local.is_relative_to(ROOT) and local != ROOT / '.local':
        raise ValueError('Inside the repository, use only the ignored .local directory')
    local.mkdir(parents=True, exist_ok=True)
    source_dir = local / 'deps/source'
    if source_dir.exists():
        raise ValueError('Build directory was already used; choose a new --work-dir (cache may be reused)')
    cache = (args.cache_dir or local / 'cache').resolve()
    cache.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / 'sources.lock.json').read_text())
    paths = {}
    for key, item in lock['downloads'].items():
        archive = fetch(item, cache)
        destination = local / 'deps' / key
        unpack(archive, destination)
        paths[key] = destination / item['root']
    source = paths['source']
    execute(['git', 'apply', '--check', ROOT / 'patches/port.patch'], cwd=source)
    execute(['git', 'apply', ROOT / 'patches/port.patch'], cwd=source)
    cmake = paths['cmake'] / 'bin/cmake.exe'
    ninja = paths['ninja'] / 'ninja.exe'
    toolbin = paths['llvm'] / 'bin'
    sdl = paths['sdl'] / 'x86_64-w64-mingw32'
    env = os.environ.copy()
    env['PATH'] = str(toolbin) + os.pathsep + env.get('PATH', '')
    env['RECOMP_LANGUAGE'] = 'en'
    common = ['-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}',
              f'-DCMAKE_C_COMPILER={(toolbin / "x86_64-w64-mingw32-clang.exe").as_posix()}',
              f'-DCMAKE_CXX_COMPILER={(toolbin / "x86_64-w64-mingw32-clang++.exe").as_posix()}']
    logs = local / 'logs'
    logs.mkdir()
    zbuild, zinstall = local / 'zlib-build', local / 'zlib-install'
    execute([cmake, '-S', paths['zlib'], '-B', zbuild, *common,
             '-DZLIB_BUILD_SHARED=OFF', '-DZLIB_BUILD_TESTING=OFF', '-DZLIB_BUILD_STATIC=ON',
             f'-DCMAKE_INSTALL_PREFIX={zinstall.as_posix()}'], env=env, log=logs / 'zlib-configure.txt')
    execute([cmake, '--build', zbuild, '--target', 'install', '--parallel', args.jobs], env=env, log=logs / 'zlib-build.txt')
    work = source / 'work/dino'
    gen = work / 'gen'
    gen.mkdir(parents=True)
    for name in ['entries.txt', 'entries.txt.z80']:
        shutil.copy2(source / 'games/dino' / name, work / name)
    execute([sys.executable, 'tools/gamecfg.py', '--header', gen / 'game_info.h', 'dino'], cwd=source)
    result = subprocess.run([sys.executable, 'tools/gamecfg.py', 'video_writes', 'dino'], cwd=source, capture_output=True, text=True, check=True)
    (gen / 'video_watches.txt').write_text('\n'.join(re.findall(r'\b[0-9A-Fa-f]{6}\b', result.stdout)) + '\n')
    build = local / 'build'
    execute([cmake, '-S', source, '-B', build, *common, '-DGAME=dino',
             f'-DGAME_DIR={(source / "games/dino").as_posix()}', f'-DWORK_DIR={work.as_posix()}',
             f'-DSDL3_DIR={(sdl / "lib/cmake/SDL3").as_posix()}',
             f'-DZLIB_INCLUDE_DIR={(zinstall / "include").as_posix()}',
             f'-DZLIB_LIBRARY={(zinstall / "lib/libzs.a").as_posix()}', '-DCMAKE_EXE_LINKER_FLAGS=-static'],
            env=env, log=logs / 'configure.txt')
    execute([cmake, '--build', build, '--target', 'dino', '--parallel', args.jobs], env=env, log=logs / 'bootstrap.txt')
    shutil.copy2(sdl / 'bin/SDL3.dll', build / 'SDL3.dll')
    execute([build / 'dino.exe', '--rom', rom, '--dump-program', work / 'program.bin'], env=env, log=logs / 'extract.txt')
    execute([sys.executable, 'tools/recomp.py', '--program', work / 'program.bin', '--entries', work / 'entries.txt',
             '--out', gen, '--limit', '180000', '--list', work / 'program.lst', '--guess', work / 'guessed.txt',
             '--data', work / 'program.bin.data', '--hook-sources', 'games/dino/src', '--watches', gen / 'video_watches.txt'],
            cwd=source, log=logs / 'translate-main.txt')
    execute([sys.executable, 'tools/recompz80.py', '--program', work / 'program.bin.z80', '--entries', work / 'entries.txt.z80',
             '--out', gen, '--list', work / 'sound.lst', '--opcodes', work / 'program.bin.z80ops'], cwd=source, log=logs / 'translate-sound.txt')
    execute([cmake, '--build', build, '--target', 'dino', '--parallel', args.jobs], env=env, log=logs / 'native-build.txt')
    execute([build / 'dino.exe', '--rom', rom, '--cpu', 'native', '--video', 'board', '--headless', '--frames', '1800',
             '--stats', '--auto', '123:400:3', '--features', 'widescreen,free_play', '--settings', local / 'test-settings.ini',
             '--eeprom', local / 'test-eeprom.bin'], env=env, log=logs / 'smoke.txt')
    smoke = (logs / 'smoke.txt').read_text()
    if '0 instructions had no translation and ran in the interpreter' not in smoke or 'sound driver: 0 instructions had no translation' not in smoke:
        raise RuntimeError('Native execution verification failed; see smoke.txt')
    version = (ROOT / 'VERSION').read_text().strip()
    output = create_packages(source, build, sdl, rom, local, version)
    (local / 'build-result.json').write_text(json.dumps({'version': version, 'upstream_commit': lock['upstream_commit'],
        'patch_sha256': digest(ROOT / 'patches/port.patch'), 'exe_sha256': digest(build / 'dino.exe'),
        'smoke_frames': 1800, 'native_only_smoke_passed': True}, indent=2) + '\n')
    print(f'Build completed. Your local Windows and Bazzite packages: {output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        sys.exit(f'ERROR: {error}')

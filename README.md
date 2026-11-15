# Cadillacs and Dinosaurs â€” Build Kit 0.1.0

Build an unofficial Windows x64 port of **Cadillacs and Dinosaurs (World 930201)**
from your own original arcade ROM set. The Windows output also runs on Bazzite
on the ROG Ally through Proton.

**This repository contains no ROM, game executable, translated game program,
game artwork, audio, screenshots or save states.** It contains build scripts,
a GPL source patch and compatibility metadata. There are no game downloads.
You must supply a ROM you are entitled to use. The ROM is checked and processed
on your computer; the build script never uploads it.

## Features

- Expanded 16:9 presentation using the game's existing scenery tiles, without
  stretching the original picture. Some extensions repeat appropriate scenery
  elements; they are not previously hidden original artwork.
- Wider enemy drawing and player movement limits.
- Adapted opening, story cards, transitions and ending presentation.
- Start during play opens **Paused â†’ Cheats**, with independent
  **Infinite Ammo** and **Infinite Health** switches (**No / Yes**).
- English menus and portable settings.
- Ahead-of-time translated 68000 and Z80 game code. The production build fails
  if untranslated CPU code is encountered instead of using interpreter fallback.
  Board, video and sound hardware behavior is still implemented by CPS2Recomp.

## Build on Windows

Requirements: **Windows x64, Python 3.11 or newer, Git for Windows**, internet
access for dependencies, and several GB of available disk space. Python and Git
must be on PATH. No global installation of the downloaded compiler is needed.

1. Clone or download this repository, preferably into a short path such as
   `C:\dino-kit`.
2. Open PowerShell in that folder.
3. Run, substituting the path to your own ROM:

```powershell
python build.py --rom "D:\MyROMs\dino.zip"
```

The script verifies the 16 required ROM members, downloads the pinned tools and
CPS2Recomp source, checks their SHA-256 hashes, applies the patch, extracts and
translates the game locally, compiles it and runs a 1,800-frame native smoke test.
It then creates:

```text
.local/output/Cadillacs-Dinosaurs-Windows-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0.tar.gz
```

Launch **PLAY.cmd** in the Windows package. The output includes a local copy of
the supplied ROM. **Do not publish these generated packages or their contents.**
The ignored `.local` directory contains private ROM-derived data, tool downloads,
generated source and logs; it is never part of the public kit.

To check only your ROM, with no downloads:

```powershell
python build.py --rom "D:\MyROMs\dino.zip" --verify-rom
```

Only the **World 930201 parent set (`dino`)** is supported. US, Japanese, bootleg
and modified sets are not accepted. Matching is by each required member's size
and hash, not by the ZIP container hash, so recompressing a correct set is fine.
Missing or different members are reported before any dependency download.

The default build uses at most eight compiler jobs. Use `--jobs 2` on a machine
with limited RAM. A failed build leaves its logs available for diagnosis; retry
in a new work directory and optionally reuse the verified download cache:

```powershell
python build.py --rom "D:\MyROMs\dino.zip" --work-dir "C:\dino-build-2" --cache-dir ".local\cache" --jobs 4
```

## Bazzite / ROG Ally

Version 0.1.0 is **built on Windows**; compilation directly on Bazzite is not
provided. Transfer the generated Bazzite `.tar.gz` to the Ally, then:

1. Extract it into a folder under your home directory.
2. Have Steam and Proton installed. The launcher looks for Proton 11.0,
   Experimental or 10.0. For another version, set `DINO_PROTON` to its `proton`
   executable path.
3. Add the extracted **jogar.sh** as a non-Steam game and launch that shortcut.
   Do not force an additional Steam compatibility layer on the shell script;
   the launcher invokes Proton itself.
4. If the file manager removed execution permission, run `chmod +x jogar.sh`.

The launcher creates its own `compatdata`, logs and user settings inside the
package directory. No SSH access, account name, device IP or existing Steam
library configuration is required. It does not edit your other shortcuts.

## Controls

Use the existing game controls for movement, attack and jump. During an active
game, **Start** opens the compact pause menu. D-pad selects items; A enters or
changes a switch; left/right also changes No/Yes; B goes back; Start resumes.
During the opening/selection/continue flow, Start keeps its original game role.

Infinite Ammo preserves ammunition while firing an equipped gun; it does not
create weapons or cover grenades and melee durability. Infinite Health protects
living players against damage and special-move health cost; it does not resurrect
a dead player or disable every time limit or scripted death.

## Scope and known limitations

This is an initial experimental release. Windows gameplay and Proton on the ROG
Ally have been exercised, including sound and gamepad controls. The latest camera
fixes passed 36,600 test frames across 11 directed cases and four movement checks.
These checks do not establish that every scene and gameplay combination is free
of defects. An unexpected exit was reported during manual play; its cause has
not yet been established.

Completely black fade frames and intentionally dark artwork are part of the
game; the widescreen work targets unwanted borders and missing scenery. Reports
should identify the stage, scene and steps to reproduce. Do not attach ROMs,
extracted game data or generated executables to issues.

## Source, licenses and publication boundary

This kit applies `patches/port.patch` to CPS2Recomp **v1.5.0**, upstream commit
`eea67d13bd2eccab1712db063ebf2eda06853f2b`. Versions, URLs and checksums are in
`sources.lock.json`. All translation happens after the user supplies their ROM.

Kit software and modifications: **GPL-3.0-only**. This does not license the
original game content. See [NOTICE.md](NOTICE.md), [LICENSE](LICENSE), and
[CPS2Recomp](https://github.com/tmcleroy/cps2recomp). No affiliation or endorsement
by the original game's rights holders is claimed.

CI runs public-source auditing and synthetic tests only. It never receives a ROM,
builds the game or uploads game artifacts. `scripts/audit_public.py` checks an
explicit text-file allowlist, reviewed checksums, the Git index and reachable
history. Maintainers must review changes and update `publish-manifest.json` before
publishing; the manifest alone is not a substitute for reviewing source contents.

## Resumo em portuguÃªs

Este repositÃ³rio Ã© um **kit de construÃ§Ã£o**, nÃ£o um download do jogo. No Windows,
instale Python 3.11+ e Git, abra a pasta do kit e execute
`python build.py --rom "D:\MinhasROMs\dino.zip"` com sua prÃ³pria ROM **World 930201**.
O script baixa as ferramentas oficiais e gera tudo localmente. Os pacotes prontos
ficam em `.local/output`. No Windows, abra `PLAY.cmd`; no Bazzite, transfira o
pacote gerado e adicione `jogar.sh` Ã  Steam. A ROM, o executÃ¡vel e os arquivos
gerados nÃ£o devem ser enviados para o GitHub.

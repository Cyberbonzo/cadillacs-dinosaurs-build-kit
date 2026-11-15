# Cadillacs and Dinosaurs Build Kit

**English** | [Português (Brasil)](README.pt-BR.md)

An unofficial toolkit for building a Windows x64 port of **Cadillacs and Dinosaurs**
with expanded 16:9 scenery and an in-game cheats menu. The generated executable
also runs on Bazzite through Proton, including on the ROG Ally.

**Version: 0.1.0 · Required ROM set: dino — World 930201**

The repository provides build scripts and source modifications. It does not
distribute the ROM, a playable game executable, artwork or audio. Building requires
a compatible ROM obtained independently and used with the necessary rights.
All ROM processing takes place locally; the script does not upload game data.

## Features

- Expanded 16:9 scenery without stretching the original image.
- Enemy visibility and player movement adapted to the wider screen.
- Widescreen adjustments for the opening, transitions, story screens and ending.
- A pause menu with **Infinite Ammo** and **Infinite Health**, independently
  selectable as **No / Yes**.
- English menus and settings stored alongside the game.
- Local package generation for Windows and Bazzite/Proton.

Scenery extensions use existing game tiles, including repeated elements where
needed. They are adaptations rather than recovered artwork beyond the original
screen. The game program is translated to native C++ during the build. Board,
video and sound behavior is provided by CPS2Recomp; the production executable
does not fall back to a CPU interpreter when translated code is missing.

## Requirements

- Windows x64 for building.
- Python 3.11 or newer and Git for Windows, both available on `PATH`.
- Internet access to download the build dependencies.
- Several GB of free disk space.
- The **dino World 930201** ROM set, supplied as a ZIP file.

The compiler and other tools are downloaded into the working directory, without
requiring a global installation. Version 0.1.0 does not include a Linux build
script. Bazzite runs the package generated on Windows through Proton.

## Build

Clone the repository or download and extract its source archive. A short path,
such as `C:\dino-kit`, is recommended. Open PowerShell in that folder and run:

```powershell
python build.py --rom "D:\ROMs\dino.zip"
```

Replace the example path with the location of the compatible ROM. The script
verifies its required files, downloads and verifies the pinned dependencies,
applies the source changes, translates the game program, compiles the port and
runs a short native execution test.

Successful builds produce:

```text
.local/output/Cadillacs-Dinosaurs-Windows-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0.tar.gz
```

On Windows, open **PLAY.cmd** in the Windows package.

The generated packages contain a copy of the supplied ROM and the executable
built from it. They are local build outputs, not releases distributed by this
project. Do not attach them to this repository, its issues or its releases.

### Check ROM compatibility

```powershell
python build.py --rom "D:\ROMs\dino.zip" --verify-rom
```

This command checks the ROM without downloading tools or building the game.
The 16 required files are checked by size and hash. ZIP compression and timestamps
do not affect validation. US, Japanese, bootleg and modified sets are unsupported.
Incompatible or incomplete sets are rejected before dependency downloads begin.

### Build options and troubleshooting

The build uses up to eight compiler jobs by default. Use `--jobs 2` if memory is
limited. Logs are stored in `.local/logs` when using the default working directory.

To retry a failed build, select a new working directory. The previous download
cache can be reused; its files are checked again before use:

```powershell
python build.py --rom "D:\ROMs\dino.zip" --work-dir "C:\dino-build-2" --cache-dir ".local\cache" --jobs 4
```

## Run on Bazzite / ROG Ally

1. Copy the generated Bazzite `.tar.gz` to the device and extract it under the
   home directory.
2. Install Steam and a supported Proton version. The launcher checks for
   Proton 11.0, Proton Experimental and Proton 10.0, in that order.
3. Add **jogar.sh** from the extracted package to Steam as a non-Steam game.
4. Launch it from Steam. Leave Steam's forced compatibility option disabled
   for this shortcut; the script launches Proton itself.

If execution permission was lost during extraction, run `chmod +x jogar.sh` in
the package directory. To use another Proton installation, set `DINO_PROTON` to
the full path of its `proton` executable before launching the script.

The package keeps its Proton prefix, logs and game settings in its own directory.

## Pause menu and cheats

During gameplay, press **Start** to open **Paused**, then select **Cheats**.

| Input | Action |
| --- | --- |
| D-pad up/down | Select an item |
| A | Open an item or change its value |
| D-pad left/right | Change No / Yes |
| B | Return to the previous menu |
| Start | Resume gameplay |

**Infinite Ammo** preserves ammunition when firing an equipped gun. It does not
create weapons, replenish an already empty weapon, affect grenades or prevent
melee weapons from breaking.

**Infinite Health** protects living players from damage and special-move health
costs. It does not revive a defeated character or remove all time limits and
scripted deaths. Each cheat setting is saved independently.

Outside active gameplay, Start retains its normal role in starting or continuing
a game. Movement, attack and jump use the game's normal controls.

## Status and issue reports

Version 0.1.0 is experimental. Windows builds and Bazzite/Proton on the ROG Ally
have been tested, including audio and controller input. An unexpected exit has
been reported during gameplay; its cause remains unresolved.

Completely black fade frames and dark areas belonging to the original artwork
remain part of the presentation. The widescreen changes address missing scenery
and unwanted borders, rather than removing every black pixel.

For bug reports, include the kit version, operating system, Proton version if
applicable, affected stage and steps to reproduce. Review logs for personal
information before sharing them. Do not attach ROMs, extracted game data,
save states or generated executables.

## Source and licensing

The kit applies `patches/port.patch` to [CPS2Recomp v1.5.0](https://github.com/tmcleroy/cps2recomp),
commit `eea67d13bd2eccab1712db063ebf2eda06853f2b`.
Dependency versions, download URLs and SHA-256 hashes are recorded in
`sources.lock.json`.

The kit software and source modifications are licensed under **GPL-3.0-only**.
This license does not cover the original game's ROM, artwork, audio or trademarks.
See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). This project is not affiliated
with or endorsed by Capcom or the game's other rights holders.

For contribution checks and publication rules, see [CONTRIBUTING.md](CONTRIBUTING.md).

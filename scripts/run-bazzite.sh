#!/usr/bin/env bash
set -euo pipefail
DINO_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
STEAM_ROOT="${STEAM_COMPAT_CLIENT_INSTALL_PATH:-$HOME/.local/share/Steam}"
if [[ ! -d "$STEAM_ROOT/steamapps" && -d "$HOME/.steam/steam/steamapps" ]]; then
    STEAM_ROOT="$HOME/.steam/steam"
fi
PROTON="${DINO_PROTON:-}"
if [[ -z "$PROTON" ]]; then
    for candidate in "$STEAM_ROOT/steamapps/common/Proton 11.0/proton" \
                     "$STEAM_ROOT/steamapps/common/Proton - Experimental/proton" \
                     "$STEAM_ROOT/steamapps/common/Proton 10.0/proton"; do
        if [[ -x "$candidate" ]]; then PROTON="$candidate"; break; fi
    done
fi
if [[ ! -x "$PROTON" ]]; then
    printf 'Proton não encontrado. Instale o Proton pela Steam ou defina DINO_PROTON com o caminho do executável proton.\n' >&2
    exit 2
fi
if [[ ! -f "$DINO_ROOT/game/dino.exe" || ! -f "$DINO_ROOT/game/roms/dino.zip" ]]; then
    printf 'Pacote incompleto. Extraia a pasta inteira novamente.\n' >&2
    exit 3
fi
mkdir -p "$DINO_ROOT/compatdata" "$DINO_ROOT/logs" "$DINO_ROOT/game/user"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT"
export STEAM_COMPAT_DATA_PATH="$DINO_ROOT/compatdata"
export WINEDEBUG=-all
export RECOMP_LANGUAGE=en
cd "$DINO_ROOT/game"
exec "$PROTON" waitforexitandrun "$DINO_ROOT/game/dino.exe" \
    --rom roms/dino.zip --cpu native --renderer sdl --video board \
    --fullscreen --features widescreen,free_play,display_shape=0,display_scaling=0,display_shader=0 \
    --settings user/settings.ini --eeprom user/eeprom.bin "$@" \
    >> "$DINO_ROOT/logs/game.log" 2>&1

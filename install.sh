#!/bin/sh
# Instala GlassPad Pizarra para el usuario actual (sin root).
# uso: ./install.sh [--quitar]
set -eu

AQUI=$(cd "$(dirname "$0")" && pwd)
BIN=${XDG_BIN_HOME:-$HOME/.local/bin}
DATOS=${XDG_DATA_HOME:-$HOME/.local/share}
CONF=${XDG_CONFIG_HOME:-$HOME/.config}
COMPLEMENTO=$DATOS/glasspad/complementos/pizarra
UNIDAD=$CONF/systemd/user/glasspad-pizarra.service
DBUS=$DATOS/dbus-1/services/io.github.kan0p.GlassPad.Pizarra.service

if [ "$(id -u)" = 0 ]; then
    echo "Se instala por usuario: ejecútalo sin sudo." >&2
    exit 1
fi

reiniciar_launcher() {
    if systemctl --user -q is-active glasspad-launcher 2>/dev/null; then
        systemctl --user restart glasspad-launcher
    fi
}

if [ "${1:-}" = "--quitar" ]; then
    systemctl --user stop glasspad-pizarra 2>/dev/null || true
    rm -f "$BIN/glasspad-pizarra" "$UNIDAD" "$DBUS"
    rm -rf "$COMPLEMENTO"
    systemctl --user daemon-reload
    reiniciar_launcher
    echo "GlassPad Pizarra quitado. Los ajustes quedan en ~/.local/state/glasspad/pizarra.json"
    exit 0
fi

falta=""
python3 -c "import cairo" 2>/dev/null || falta="$falta python-cairo"
python3 -c "import gi; gi.require_version('Gtk4LayerShell', '1.0')" 2>/dev/null \
    || falta="$falta gtk4-layer-shell"
command -v wtype >/dev/null || falta="$falta wtype"
if [ -n "$falta" ]; then
    echo "Faltan dependencias:$falta" >&2
    echo "En Arch: sudo pacman -S$falta" >&2
    exit 1
fi

install -Dm755 "$AQUI/glasspad-pizarra" "$BIN/glasspad-pizarra"
rm -rf "$COMPLEMENTO"
mkdir -p "$COMPLEMENTO"
cp -r "$AQUI/complemento/pizarra/." "$COMPLEMENTO/"
rm -rf "$COMPLEMENTO/__pycache__"
mkdir -p "$(dirname "$UNIDAD")" "$(dirname "$DBUS")"
sed "s|@BINDIR@|$BIN|g" "$AQUI/systemd/glasspad-pizarra.service" > "$UNIDAD"
sed "s|@BINDIR@|$BIN|g" "$AQUI/dbus/io.github.kan0p.GlassPad.Pizarra.service" > "$DBUS"

systemctl --user daemon-reload
# que el bus de la sesión vea el archivo de activación nuevo
gdbus call --session -d org.freedesktop.DBus -o /org/freedesktop/DBus \
    -m org.freedesktop.DBus.ReloadConfig >/dev/null 2>&1 || true
systemctl --user try-restart glasspad-pizarra
reiniciar_launcher
echo "GlassPad Pizarra instalado: el mosaico Pizarra aparece en el inicio del launcher."

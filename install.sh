#!/bin/sh
# Instala GlassPad Pizarra para el usuario actual (sin root).
# uso: ./install.sh [--quitar]
#      sudo ./install.sh --sistema [--quitar]    el lector de teclas y su regla de polkit
set -eu

AQUI=$(cd "$(dirname "$0")" && pwd)
BIN=${XDG_BIN_HOME:-$HOME/.local/bin}
DATOS=${XDG_DATA_HOME:-$HOME/.local/share}
CONF=${XDG_CONFIG_HOME:-$HOME/.config}
COMPLEMENTO=$DATOS/glasspad/complementos/pizarra
UNIDAD=$CONF/systemd/user/glasspad-pizarra.service
DBUS=$DATOS/dbus-1/services/io.github.kan0p.GlassPad.Pizarra.service
# fuera de $HOME y de root: pkexec lo corre como root sin contraseña
LIBEXEC=/usr/local/libexec
# polkit solo lee acciones de /usr/share
POLITICA=/usr/share/polkit-1/actions/io.github.kan0p.glasspad.pizarra.policy
GLASSPAD_MINIMO=0.9.1

# La Pizarra es un complemento de GlassPad: sin el ScreenPad y el launcher no hay dónde manejarla.
requisitos() {
    modelo=$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)
    case "$modelo" in
        *UX580*) ;;
        *)
            echo "GlassPad Pizarra necesita el ScreenPad de la ASUS ZenBook Pro 15 UX580." >&2
            echo "Este equipo es: ${modelo:-desconocido}" >&2
            exit 1 ;;
    esac
    config=$(command -v glasspad-config || true)
    if [ -z "$config" ] || ! command -v glasspad-launcher >/dev/null; then
        echo "GlassPad Pizarra es un complemento de GlassPad: instala GlassPad $GLASSPAD_MINIMO o" >&2
        echo "posterior (https://github.com/kan0p/asus-screenpad-linux)." >&2
        exit 1
    fi
    version=$(sed -n 's/^VERSION = "\(.*\)"/\1/p' "$config")
    menor=$(printf '%s\n%s\n' "$GLASSPAD_MINIMO" "$version" | sort -V | head -n1)
    if [ -z "$version" ] || [ "$menor" != "$GLASSPAD_MINIMO" ]; then
        echo "GlassPad ${version:-desconocido} no carga complementos: actualiza a $GLASSPAD_MINIMO o posterior." >&2
        exit 1
    fi
}

if [ "${1:-}" = "--sistema" ]; then
    if [ "$(id -u)" != 0 ]; then
        echo "La parte del sistema necesita root: sudo ./install.sh --sistema" >&2
        exit 1
    fi
    if [ "${2:-}" = "--quitar" ]; then
        rm -f "$LIBEXEC/glasspad-pizarra-teclas" "$POLITICA"
        echo "Lector de teclas quitado."
        exit 0
    fi
    requisitos
    if ! python3 -c "import evdev" 2>/dev/null; then
        echo "Falta python-evdev. En Arch: pacman -S python-evdev" >&2
        exit 1
    fi
    install -Dm755 -o root -g root "$AQUI/glasspad-pizarra-teclas" "$LIBEXEC/glasspad-pizarra-teclas"
    sed "s|@LIBEXEC@|$LIBEXEC|g" "$AQUI/polkit/io.github.kan0p.glasspad.pizarra.policy" > "$POLITICA"
    chmod 644 "$POLITICA"
    echo "Lector de teclas instalado en $LIBEXEC."
    exit 0
fi

if [ "$(id -u)" = 0 ]; then
    echo "Se instala por usuario: ejecútalo sin sudo." >&2
    echo "La parte del sistema (Teclas) va aparte: sudo ./install.sh --sistema" >&2
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

requisitos
if [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo "GlassPad Pizarra funciona en una sesión Wayland (COSMIC); esta sesión no lo es." >&2
    exit 1
fi
if ! systemctl --user -q is-active glasspad-launcher 2>/dev/null; then
    echo "Aviso: GlassPad Launcher no está corriendo; la página Pizarra aparece cuando arranque."
fi

falta=""
python3 -c "import cairo" 2>/dev/null || falta="$falta python-cairo"
python3 -c "import gi; gi.require_version('Gtk4LayerShell', '1.0')" 2>/dev/null \
    || falta="$falta gtk4-layer-shell"
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
if [ ! -x "$LIBEXEC/glasspad-pizarra-teclas" ]; then
    echo "Para Teclas y la marca de clics falta la parte del sistema: sudo ./install.sh --sistema"
fi

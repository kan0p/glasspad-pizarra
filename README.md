# GlassPad Pizarra

Herramientas para dar clases con el ScreenPad de la ZenBook Pro 15 UX580: escribir sobre la pantalla principal, un foco que sigue al mouse y las teclas pulsadas con su equivalente en Windows. Se maneja desde una página propia en [GlassPad Launcher](https://github.com/kan0p/asus-screenpad-linux), como complemento, sin tocar GlassPad.

Funciona encima de cualquier ventana, también de una presentación a pantalla completa (PowerPoint Online, Google Slides, LibreOffice Impress): las herramientas se dibujan en una capa por encima de todo y el teclado sigue llegando a la presentación.

Estado: **Escribir** y **Foco** están listos. **Teclas** llega en la próxima versión.

## Requisitos

- GlassPad 0.9.1 o posterior, con el launcher funcionando
- COSMIC u otro compositor Wayland con `wlr-layer-shell`
- `python-cairo`, `gtk4-layer-shell` y `wtype`

## Instalación

```sh
git clone https://github.com/kan0p/glasspad-pizarra
cd glasspad-pizarra
./install.sh
```

Se instala para el usuario, sin root: el programa en `~/.local/bin`, el complemento en `~/.local/share/glasspad/complementos/pizarra` y un servicio de usuario que D-Bus inicia la primera vez que se usa. Para quitarlo: `./install.sh --quitar`.

## Escribir

En el ScreenPad, el mosaico **Pizarra** abre la página. Tocar **Escribir** lo enciende o lo apaga.

- Encendido, el mouse (o el touchpad, o un lápiz) dibuja sobre la pantalla principal. Al apagarlo, lo dibujado queda visible y los clics vuelven a pasar a las ventanas.
- **Lápiz**, **Resaltar**, **Láser** (el trazo se borra solo al segundo), **Flecha**, **Recuadro** y **Borrador** (quita trazos enteros).
- Seis colores, tres grosores, **Deshacer** y **Borrar todo**.
- **Pizarra blanca** y **Pizarra negra** tapan la pantalla con una hoja aparte; al volver a **Sobre la diapositiva**, lo dibujado sobre la presentación sigue ahí.
- **◀ ▶** pasan de diapositiva desde el pad sin apagar el lápiz. Con **Borrar al cambiar de diapositiva**, lo dibujado se borra al pasar.
- **Apagar todo** apaga las herramientas y borra todo lo dibujado.

## Foco

Tocar **Foco** oscurece la pantalla principal salvo un círculo que sigue al cursor. Los clics y el teclado siguen llegando a la presentación.

- **Radio** (60 a 400 px) y **Oscurecer** (30 a 90 %) se ajustan arrastrando el dedo, y se ven en vivo.
- **Con anillo** o **Sin anillo** alrededor del círculo.
- Si el cursor pasa al ScreenPad, el foco se queda donde estaba.

COSMIC informa la posición del cursor solo mientras se captura su imagen (`ext-image-copy-capture-v1`, 24×24 px), así que el foco la captura 60 veces por segundo mientras el cursor se mueve y 10 cuando está quieto. El oscurecido es una capa propia que en cada cuadro repinta solo el cuadrado alrededor del círculo: con el mouse en movimiento gasta alrededor del 6 % de un núcleo, y quieto, menos del 1 %.

Los ajustes se guardan en `~/.local/state/glasspad/pizarra.json`.

## Desde la terminal

```sh
glasspad-pizarra alternar escribir
glasspad-pizarra alternar foco
glasspad-pizarra deshacer
glasspad-pizarra borrar
glasspad-pizarra apagar
```

Sirven para asignar atajos de teclado en la configuración del escritorio.

## Licencia

GPL-3.0-or-later.

# GlassPad Pizarra

Herramientas para dar clases con el ScreenPad de la ZenBook Pro 15 UX580: escribir sobre la pantalla principal, un foco que sigue al mouse y las teclas pulsadas con su equivalente en Windows. Se maneja desde una página propia en [GlassPad Launcher](https://github.com/kan0p/asus-screenpad-linux), como complemento, sin tocar GlassPad.

Funciona encima de cualquier ventana, también de una presentación a pantalla completa (PowerPoint Online, Google Slides, LibreOffice Impress): las herramientas se dibujan en una capa por encima de todo y el teclado sigue llegando a la presentación.

## Requisitos

- GlassPad 0.9.1 o posterior, con el launcher funcionando
- COSMIC u otro compositor Wayland con `wlr-layer-shell`
- `python-cairo`, `gtk4-layer-shell` y `wtype`
- Para Teclas y la marca de clics: `python-evdev` y `polkit`

## Instalación

```sh
git clone https://github.com/kan0p/glasspad-pizarra
cd glasspad-pizarra
./install.sh
```

Se instala para el usuario, sin root: el programa en `~/.local/bin`, el complemento en `~/.local/share/glasspad/complementos/pizarra` y un servicio de usuario que D-Bus inicia la primera vez que se usa. Para quitarlo: `./install.sh --quitar`.

Teclas y la marca de clics del Foco necesitan leer el teclado y el mouse, y eso va aparte, con root:

```sh
sudo ./install.sh --sistema
```

Instala el lector en `/usr/local/libexec/glasspad-pizarra-teclas` y una acción de polkit que permite abrirlo con `pkexec` sin contraseña, solo desde la sesión local activa. Para quitarlo: `sudo ./install.sh --sistema --quitar`.

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

Con **Marcar clics**, cada clic dentro del foco deja una onda: amarilla el izquierdo, azul el derecho.

## Teclas

Tocar **Teclas** muestra abajo de la pantalla principal los atajos que se pulsan, con lo que hacen y su equivalente en Windows: Super se muestra como **⊞ Win**, y si en Windows el atajo es otro, aparece debajo (Super+Esc bloquea la sesión; en Windows, ⊞ Win + L).

Muestra **solo atajos**, nunca lo que se escribe:

- combinaciones con Ctrl, Alt o Super (AltGr no cuenta: escribe caracteres);
- Shift con una tecla que no escribe texto: Shift+Tab, Shift+flechas, Shift+F5;
- las flechas, las teclas de función e Impr Pant solas;
- Super solo, que abre el lanzador.

Si se repite el mismo atajo, la tarjeta cuenta las veces (→ ×5) en lugar de sumar otra.

El filtro está dentro del lector, que corre como root: las letras, números y signos escritos sin Ctrl, Alt ni Super se descartan ahí y nunca llegan a la sesión. El lector solo corre mientras Teclas o la marca de clics están encendidos, y se cierra solo al apagarlos. No lee el teclado virtual de Number Key ni el pad del ScreenPad.

Los nombres de los signos siguen la distribución de teclado de COSMIC (`us`, `latam` y `es`). **Como en Linux** muestra Super sin los nombres de Windows. La posición (abajo al centro o a la derecha) y el tamaño se eligen en el pad.

Los ajustes se guardan en `~/.local/state/glasspad/pizarra.json`.

## Atajos de teclado

El botón ⚙ junto a **Apagar todo** muestra los atajos de la Pizarra:

| Atajo | Acción |
|---|---|
| Super+Alt+E | Escribir |
| Super+Alt+F | Foco |
| Super+Alt+T | Teclas |
| Super+Alt+Z | Deshacer |
| Super+Alt+0 | Apagar todo |

**Registrar en COSMIC** los agrega a los atajos propios de COSMIC (`~/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/custom`) sin tocar los demás, y **Quitar de COSMIC** los saca. Para cambiar uno, se toca **Cambiar** y se pulsa la combinación nueva en el teclado: la lee el lector de Teclas, así que necesita la parte del sistema. Si COSMIC u otra acción de la Pizarra ya la usan, avisa y no la guarda. **Restablecer** vuelve a los de la tabla.

## Desde la terminal

```sh
glasspad-pizarra alternar escribir
glasspad-pizarra alternar foco
glasspad-pizarra alternar teclas
glasspad-pizarra deshacer
glasspad-pizarra borrar
glasspad-pizarra apagar
```

Sirven para asignar atajos de teclado en la configuración del escritorio.

## Licencia

GPL-3.0-or-later.

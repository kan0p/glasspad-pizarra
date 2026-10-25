# Pizarra - escribir, foco y teclas en pantalla para dar clases (complemento de GlassPad)
# kan0p - https://github.com/kan0p/glasspad-pizarra - GPL-3.0-or-later
import os

from gi.repository import Gio, GLib, Gtk

NOMBRE = "Pizarra"
ICONO = "icono.svg"

BUS = "io.github.kan0p.GlassPad.Pizarra"
RUTA = "/io/github/kan0p/GlassPad/Pizarra"
INTERFAZ = "io.github.kan0p.GlassPad.Pizarra"

HERRAMIENTAS = [("lapiz", "Lápiz"), ("resaltador", "Resaltar"), ("laser", "Láser"),
                ("flecha", "Flecha"), ("recuadro", "Recuadro"), ("borrador", "Borrador")]
COLORES = [("rojo", "#ff5a4e"), ("amarillo", "#ffd23f"), ("verde", "#3ddc84"),
           ("azul", "#4c9bff"), ("blanco", "#ffffff"), ("negro", "#111111")]
FONDOS = [("transparente", "Sobre la diapositiva"), ("blanca", "Pizarra blanca"),
          ("negra", "Pizarra negra")]
NOMBRE_HERRAMIENTA = dict(HERRAMIENTAS) | {"resaltador": "Resaltador"}

CSS = """
.pizarra { margin: 36px 77px 30px 77px; }
.pizarra-titulo { font-size: 40px; font-weight: 600; }
.pizarra-gris { font-size: 26px; color: alpha(white, 0.6); }
.pizarra-boton { background: alpha(black, 0.4); border: 1px solid alpha(white, 0.14);
                 box-shadow: none; outline: none; border-radius: 26px; color: white;
                 font-size: 26px; min-height: 88px; padding: 0 28px; }
.pizarra-boton.flecha { min-width: 140px; padding: 0; }
.pizarra-boton.peligro { background: alpha(#e5484d, 0.3); color: #ffd0cc; }
.pizarra-boton.presionado { background: alpha(white, 0.25); }
.pizarra-mosaico { background: alpha(black, 0.42); border: 2px solid alpha(white, 0.1);
                   box-shadow: none; outline: none; border-radius: 40px; color: white;
                   min-height: 190px; padding: 26px 32px; }
.pizarra-mosaico.elegido { border-color: #ff8a3d; }
.pizarra-mosaico.encendido { background: alpha(#1d2230, 0.85); }
.pizarra-mosaico.presionado { background: alpha(white, 0.2); }
.pizarra-mosaico.proximamente { opacity: 0.55; }
.pizarra-mosaico .nombre { font-size: 36px; font-weight: 600; }
.pizarra-mosaico .detalle { font-size: 24px; color: alpha(white, 0.65); }
.pizarra-interruptor { min-width: 84px; min-height: 46px; border-radius: 23px; padding: 5px;
                       background: alpha(white, 0.2); }
.pizarra-interruptor.encendido { background: #ff8a3d; }
.pizarra-perilla { min-width: 36px; min-height: 36px; border-radius: 18px; background: white; }
.pizarra-panel { background: alpha(#141b2b, 0.9); border: 1px solid alpha(white, 0.1);
                 border-radius: 40px; padding: 28px 36px; }
.pizarra-subtitulo { font-size: 30px; font-weight: 600; }
.pizarra-etiqueta { font-size: 26px; color: alpha(white, 0.6); min-width: 170px; }
.pizarra-opcion { background: alpha(white, 0.08); border: 2px solid transparent;
                  box-shadow: none; outline: none; border-radius: 24px; color: white;
                  font-size: 25px; min-height: 92px; padding: 0 24px; }
.pizarra-opcion.elegido { background: alpha(#ff8a3d, 0.28); border-color: #ff8a3d; }
.pizarra-opcion.presionado { background: alpha(white, 0.25); }
.pizarra-color { min-width: 80px; min-height: 80px; border-radius: 40px; padding: 0;
                 border: 3px solid alpha(white, 0.25); box-shadow: none; outline: none; }
.pizarra-color.elegido { border: 6px solid #ff8a3d; }
.pizarra-grosor { min-width: 104px; padding: 0; }
.pizarra-punto { background: white; }
.pizarra-chip { background: alpha(black, 0.4); border: 1px solid alpha(white, 0.14);
                box-shadow: none; outline: none; border-radius: 30px; color: white;
                font-size: 24px; padding: 10px 26px; }
.pizarra-chip.elegido { background: alpha(#ff8a3d, 0.28); border-color: #ff8a3d; }
.pizarra-chip.presionado { background: alpha(white, 0.25); }
.pizarra-vacio { font-size: 30px; color: alpha(white, 0.65); }
""" + "".join(f".pizarra-color.{n} {{ background: {c}; }}\n" for n, c in COLORES)


def crear(api):
    api.css(CSS)
    iconos = os.path.join(api.carpeta, "iconos")
    estado = {}
    widgets = {"herramienta": {}, "color": {}, "grosor": {}, "fondo": {}}
    avisado = [False]

    def icono(nombre, tam):
        return Gtk.Image(file=os.path.join(iconos, nombre + ".svg"), pixel_size=tam)

    # ----- D-Bus -------------------------------------------------------------

    bus = Gio.bus_get_sync(Gio.BusType.SESSION)

    def llamar(metodo, params=None, despues=None):
        def fin(con, res):
            try:
                r = con.call_finish(res)
            except GLib.Error as e:
                if not avisado[0]:
                    avisado[0] = True
                    api.avisar("No se pudo hablar con glasspad-pizarra")
                print(f"pizarra: {metodo}: {e.message}", flush=True)
                return
            avisado[0] = False
            if despues:
                despues(r)
        bus.call(BUS, RUTA, INTERFAZ, metodo, params, None, Gio.DBusCallFlags.NONE, 5000,
                 None, fin)

    def ajustar(**cambios):
        llamar("Ajustar", GLib.Variant("(a{sv})", ({k: (
            GLib.Variant("b", v) if isinstance(v, bool) else
            GLib.Variant("i", v) if isinstance(v, int) else GLib.Variant("s", v))
            for k, v in cambios.items()},)))

    def refrescar():
        llamar("Estado", None, lambda r: mostrar(r.unpack()[0]))

    bus.signal_subscribe(None, INTERFAZ, "Cambio", RUTA, None, Gio.DBusSignalFlags.NONE,
                         lambda *a: mostrar(a[5].unpack()[0]))

    # ----- cabecera ----------------------------------------------------------

    def boton(texto=None, nombre_icono=None, al_tocar=None, clases=()):
        hijo = Gtk.Box(spacing=14, halign=Gtk.Align.CENTER)
        if nombre_icono:
            hijo.append(icono(nombre_icono, 40))
        if texto:
            hijo.append(Gtk.Label(label=texto))
        return api.accion(Gtk.Button(child=hijo, css_classes=["pizarra-boton", *clases]),
                          al_tocar)

    def pasar(tecla):
        llamar("CambioDiapositiva", None, lambda _r: api.atajo(tecla))

    cabecera = Gtk.Box(spacing=18)
    cabecera.append(Gtk.Label(label="Pizarra", css_classes=["pizarra-titulo"], xalign=0,
                              hexpand=True))
    cabecera.append(Gtk.Label(label="Diapositiva", css_classes=["pizarra-gris"]))
    cabecera.append(boton(None, "anterior", lambda: pasar("Left"), ["flecha"]))
    cabecera.append(boton(None, "siguiente", lambda: pasar("Right"), ["flecha"]))
    cabecera.append(boton("Apagar todo", "apagar", lambda: llamar("ApagarTodo")))

    # ----- mosaicos ----------------------------------------------------------

    mosaicos = Gtk.Box(spacing=28, homogeneous=True)

    def mosaico(clave, nombre, al_tocar):
        interruptor = Gtk.Box(css_classes=["pizarra-interruptor"], valign=Gtk.Align.CENTER)
        perilla = Gtk.Box(css_classes=["pizarra-perilla"], hexpand=True, halign=Gtk.Align.START)
        interruptor.append(perilla)
        arriba = Gtk.Box()
        arriba.append(icono(clave, 64))
        arriba.append(Gtk.Box(hexpand=True))
        arriba.append(interruptor)
        detalle = Gtk.Label(css_classes=["detalle"], xalign=0)
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        caja.append(arriba)
        caja.append(Gtk.Box(vexpand=True))
        caja.append(Gtk.Label(label=nombre, css_classes=["nombre"], xalign=0))
        caja.append(detalle)
        b = api.accion(Gtk.Button(child=caja, css_classes=["pizarra-mosaico"]), al_tocar)
        mosaicos.append(b)
        return b, interruptor, perilla, detalle

    m_escribir = mosaico("escribir", "Escribir",
                         lambda: ajustar(escribir=not estado.get("escribir", False)))
    m_foco = mosaico("foco", "Foco", lambda: api.avisar("Foco llega en la próxima versión"))
    m_teclas = mosaico("teclas", "Teclas", lambda: api.avisar("Teclas llega en una próxima versión"))
    for m in (m_foco, m_teclas):
        m[0].add_css_class("proximamente")
        m[3].set_label("Próximamente")
    m_escribir[0].add_css_class("elegido")

    # ----- ajustes de Escribir ----------------------------------------------

    def fila(etiqueta):
        f = Gtk.Box(spacing=16)
        if etiqueta:
            f.append(Gtk.Label(label=etiqueta, css_classes=["pizarra-etiqueta"], xalign=0))
        return f

    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20,
                    css_classes=["pizarra-panel"], vexpand=True)
    sub = Gtk.Box(spacing=16)
    sub.append(Gtk.Label(label="Ajustes de Escribir", css_classes=["pizarra-subtitulo"],
                         xalign=0, hexpand=True))
    borrar_al_pasar = api.accion(
        Gtk.Button(label="Borrar al cambiar de diapositiva", css_classes=["pizarra-chip"]),
        lambda: ajustar(borrar_al_pasar=not estado.get("borrar_al_pasar", True)))
    sub.append(borrar_al_pasar)
    panel.append(sub)

    f = fila("Herramienta")
    for clave, nombre in HERRAMIENTAS:
        hijo = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER)
        hijo.append(icono(clave, 36))
        hijo.append(Gtk.Label(label=nombre))
        b = api.accion(Gtk.Button(child=hijo, css_classes=["pizarra-opcion"], hexpand=True),
                       lambda c=clave: ajustar(herramienta=c, escribir=True))
        widgets["herramienta"][clave] = b
        f.append(b)
    panel.append(f)

    f = fila("Color")
    for clave, _c in COLORES:
        b = api.accion(Gtk.Button(css_classes=["pizarra-color", clave], valign=Gtk.Align.CENTER,
                                  tooltip_text=clave),
                       lambda c=clave: ajustar(color=c, escribir=True))
        widgets["color"][clave] = b
        f.append(b)
    f.append(Gtk.Box(hexpand=True))
    f.append(Gtk.Label(label="Grosor", css_classes=["pizarra-etiqueta"], xalign=1))
    for n, tam in ((1, 10), (2, 20), (3, 32)):
        punto = Gtk.Box(css_classes=["pizarra-punto"], halign=Gtk.Align.CENTER,
                        valign=Gtk.Align.CENTER, width_request=tam, height_request=tam)
        api.css(f".pizarra-punto.g{n} {{ border-radius: {tam // 2}px; }}")
        punto.add_css_class(f"g{n}")
        b = api.accion(Gtk.Button(child=punto, css_classes=["pizarra-opcion", "pizarra-grosor"]),
                       lambda g=n: ajustar(grosor=g))
        widgets["grosor"][n] = b
        f.append(b)
    panel.append(f)

    f = fila("Fondo")
    for clave, nombre in FONDOS:
        b = api.accion(Gtk.Button(label=nombre, css_classes=["pizarra-opcion"]),
                       lambda c=clave: ajustar(fondo=c, escribir=True))
        widgets["fondo"][clave] = b
        f.append(b)
    f.append(Gtk.Box(hexpand=True))
    deshacer = boton("Deshacer", "deshacer", lambda: llamar("Deshacer"))
    f.append(deshacer)
    f.append(boton("Borrar todo", "borrar", lambda: llamar("Borrar"), ["peligro"]))
    panel.append(f)

    # ----- estado ------------------------------------------------------------

    def mostrar(nuevo):
        estado.clear()
        estado.update(nuevo)
        on = estado.get("escribir", False)
        b, interruptor, perilla, detalle = m_escribir
        for w in (b, interruptor):
            (w.add_css_class if on else w.remove_css_class)("encendido")
        perilla.set_halign(Gtk.Align.END if on else Gtk.Align.START)
        h = estado.get("herramienta", "lapiz")
        texto = NOMBRE_HERRAMIENTA.get(h, h)
        if h != "borrador":
            texto += " " + estado.get("color", "")
        detalle.set_label(("Activo · " if on else "Apagado · ") + texto)
        for grupo, valor in (("herramienta", h), ("color", estado.get("color")),
                             ("grosor", estado.get("grosor")), ("fondo", estado.get("fondo"))):
            for clave, w in widgets[grupo].items():
                (w.add_css_class if clave == valor else w.remove_css_class)("elegido")
        (borrar_al_pasar.add_css_class if estado.get("borrar_al_pasar")
         else borrar_al_pasar.remove_css_class)("elegido")
        deshacer.set_sensitive(bool(estado.get("puede_deshacer")))

    api.al_mostrar(lambda visible: visible and refrescar())

    pagina = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24, css_classes=["pizarra"])
    pagina.append(cabecera)
    pagina.append(mosaicos)
    pagina.append(panel)
    return pagina

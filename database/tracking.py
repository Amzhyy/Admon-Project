"""
Servidor de tracking + helper de registro de clics.

Este módulo cumple dos funciones:

  1. **Como módulo importable** — provee `registrar_click(email)` para que otros
     componentes registren clics en la base de datos.

  2. **Como script ejecutable** — al correrlo directamente (`python tracking.py`)
     arranca el servidor HTTP que escucha clics de los correos de simulación.

Compatibilidad de ejecución:
    Cualquiera de estos comandos funciona:

        python tracking.py                       (estando dentro de database/)
        python database/tracking.py              (estando en la raíz del proyecto)
        python tracking_server.py                (wrapper en la raíz)

Cómo lo logra: el bloque inicial detecta su propia ubicación y agrega la
raíz del proyecto a `sys.path` ANTES de cualquier import del paquete `database`.
"""

import os
import sys

# ── Auto path setup ──────────────────────────────────────────────────────────
# Esto se ejecuta SIEMPRE al cargar el módulo, no solo en __main__, para que
# `from database.tracking import registrar_click` también funcione desde
# contextos donde el path no esté correctamente configurado.
_HERE = os.path.dirname(os.path.abspath(__file__))      # …/database/
_ROOT = os.path.dirname(_HERE)                           # raíz del proyecto
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Ya con el path corregido, los imports relativos al paquete funcionan
from database.connection import conectar, safe_close


def registrar_click(email_str: str) -> bool:
    """
    Registra un clic de un correo enviado en la tabla `result`.

    Busca el correo más reciente enviado a esa dirección y, si encuentra uno,
    incrementa su contador de clics (o lo crea si es el primero).

    Returns:
        True si se registró correctamente, False en caso de error o no-encontrado.
    """
    conexion = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Buscar el id_email basado en el correo del usuario (el más reciente)
        cursor.execute("""
            SELECT e.id_email
            FROM email e
            JOIN user  u ON e.id_user = u.id_user
            WHERE u.email = %s
            ORDER BY e.id_email DESC LIMIT 1
        """, (email_str,))
        res = cursor.fetchone()

        if not res:
            print(f"[tracking] Sin correo enviado registrado para {email_str}")
            return False

        id_email = res[0]
        cursor.execute(
            "SELECT id_result, clic FROM result WHERE id_email = %s",
            (id_email,),
        )
        result_row = cursor.fetchone()

        if result_row:
            id_result, clic_actual = result_row
            cursor.execute(
                "UPDATE result SET clic = %s WHERE id_result = %s",
                (clic_actual + 1, id_result),
            )
        else:
            cursor.execute(
                "INSERT INTO result (id_email, clic, report) VALUES (%s, 1, '')",
                (id_email,),
            )

        conexion.commit()
        print(f"[tracking] Clic registrado para {email_str}")
        return True

    except Exception as e:
        print(f"[tracking] Error registrando clic: {e}")
        return False
    finally:
        safe_close(conexion)


# ═════════════════════════════════════════════════════════════════════════════
#  Servidor HTTP — sólo se ejecuta cuando el archivo se corre como script
# ═════════════════════════════════════════════════════════════════════════════
def _run_server(port: int = 8081) -> None:
    """Levanta el servidor HTTP que escucha clics de phishing."""
    import http.server
    import socketserver
    import urllib.parse

    class PhishingHandler(http.server.SimpleHTTPRequestHandler):
        # Silenciar log por defecto (es muy ruidoso); imprimimos nuestro propio log
        def log_message(self, format, *args):
            return

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/click":
                params = urllib.parse.parse_qs(parsed.query)
                email = params.get("email", [None])[0]

                if email:
                    print(f"\n[server] Clic detectado de: {email}")
                    registrar_click(email)

                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(_PHISHING_PAGE.encode("utf-8"))
                    return

            # Cualquier otra ruta: 404
            self.send_response(404)
            self.end_headers()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), PhishingHandler) as httpd:
        _print_banner(port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[server] Detenido por usuario.")
            httpd.shutdown()


_PHISHING_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Simulación de Phishing — Admon Project</title>
    <style>
        body { font-family: -apple-system, "Segoe UI", sans-serif;
               text-align: center; padding-top: 80px;
               background: #f8d7da; color: #721c24; }
        h1 { font-size: 48px; margin: 0; }
        .subtitle { font-size: 20px; margin: 14px 0; }
        .footer { font-size: 13px; color: #555; margin-top: 30px; }
        hr { max-width: 420px; border: none; border-top: 1px solid #e0a3a8; }
    </style>
</head>
<body>
    <h1>🔴 ¡HAS SIDO PHISHEADO!</h1>
    <p class="subtitle">Esta es una <b>simulación de seguridad</b> de Admon Project.</p>
    <p>En un ataque real, tus datos habrían sido comprometidos.</p>
    <hr>
    <p class="footer">Tu clic ha sido registrado para fines estadísticos.</p>
</body>
</html>
"""


def _print_banner(port: int) -> None:
    bar = "═" * 60
    print(bar)
    print("  Servidor de tracking de phishing — Admon Project")
    print(bar)
    print(f"  Escuchando en:  http://localhost:{port}")
    print(f"  Endpoint:       /click?email=<dirección>")
    print()
    print("  Mantén esta terminal abierta. Cada clic en un correo de")
    print("  simulación se registrará en la base de datos.")
    print()
    print("  Ctrl+C para detener.")
    print(bar)


if __name__ == "__main__":
    # Verificar que el path quedó bien configurado
    try:
        from database.connection import test_connection
        ok, msg = test_connection()
        if not ok:
            print(f"[ADVERTENCIA] Base de datos: {msg}")
            print("  El servidor arrancará igualmente, pero los clics no se podrán")
            print("  registrar hasta que la DB esté accesible.\n")
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo verificar la DB: {e}\n")

    # Permitir puerto personalizado vía CLI:  python tracking.py 9090
    port = 8081
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Puerto inválido: {sys.argv[1]}. Usando 8081 por defecto.")
            port = 8081

    try:
        _run_server(port)
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"\n[ERROR] El puerto {port} ya está en uso.")
            print(f"  ¿Tienes otra instancia corriendo?")
            print(f"  Prueba con otro puerto:  python tracking.py 9090")
            sys.exit(1)
        raise

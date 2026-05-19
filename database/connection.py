"""
Gestión de conexiones a MySQL con pool — evita el problema de Windows
donde abrir/cerrar muchas conexiones rápido agota los sockets (errno 10038).

Uso:
    from database.connection import conectar
    conn = conectar()      # toma una conexión del pool
    ...
    conn.close()           # la devuelve al pool (no cierra el socket)
"""

import os
import threading

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


_POOL = None
_POOL_LOCK = threading.Lock()
_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))


def _build_pool():
    """Construye el pool una sola vez. Devuelve el pool o None si falla."""
    import mysql.connector.pooling
    cfg = {
        "host":               os.getenv("DB_HOST", "localhost"),
        "user":               os.getenv("DB_USER", "root"),
        "password":           os.getenv("DB_PASSWORD", ""),
        "database":           os.getenv("DB_NAME", "admon_project"),
        "use_pure":           True,
        "connection_timeout": 5,
        "autocommit":         False,
    }
    return mysql.connector.pooling.MySQLConnectionPool(
        pool_name="admon_pool",
        pool_size=_POOL_SIZE,
        pool_reset_session=True,
        **cfg,
    )


def _get_pool():
    """Lazy-init thread-safe del pool."""
    global _POOL
    if _POOL is None:
        with _POOL_LOCK:
            if _POOL is None:
                _POOL = _build_pool()
    return _POOL


def conectar():
    """
    Obtiene una conexión MySQL desde el pool.
    Si el pool falla (DB caída, credenciales malas) cae a una conexión directa
    para no romper completamente la app.
    """
    import mysql.connector

    try:
        pool = _get_pool()
        conn = pool.get_connection()
        # Verificar que la conexión esté viva (puede haber sido invalidada)
        try:
            conn.ping(reconnect=True, attempts=2, delay=0)
        except Exception:
            # Pool rota: forzar reconstrucción en próxima llamada
            global _POOL
            _POOL = None
            raise
        return conn
    except Exception as e:
        # Fallback: conexión directa (sin pool) — útil cuando se prueba en CI
        print(f"[DB] Pool no disponible ({e}). Usando conexión directa.")
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "admon_project"),
            use_pure=True,
            connection_timeout=5,
        )


def safe_close(conexion) -> None:
    """
    Cierra una conexión sin lanzar excepciones.

    Importante en Windows: si el socket subyacente ya fue invalidado, la propia
    llamada a close() puede lanzar WinError 10038 — la atrapamos en silencio.
    """
    if conexion is None:
        return
    try:
        if conexion.is_connected():
            conexion.close()
    except Exception:
        pass


def test_connection() -> tuple[bool, str]:
    """Health check para mostrar mensaje al arrancar la app."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        safe_close(conn)
        return True, "Conexión exitosa."
    except Exception as e:
        msg = str(e)
        if "Access denied" in msg:
            return False, "Credenciales de base de datos incorrectas. Revisa DB_USER y DB_PASSWORD en .env"
        if "Unknown database" in msg:
            return False, "La base de datos no existe. Ejecuta el script SQL de creación."
        if "Can't connect" in msg or "refused" in msg.lower():
            return False, "No se puede conectar al servidor MySQL. ¿Está corriendo?"
        return False, f"Error de base de datos: {msg}"

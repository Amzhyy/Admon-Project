import re
from database.connection import conectar, safe_close

# Longitud mínima de contraseña
_MIN_PASSWORD_LENGTH = 8

# Mapeo de opciones de UI → ENUM de la base de datos
# Claves en minúsculas para comparación insensible al caso
_ROLE_MAP: dict[str, str] = {
    "administrador": "admin",
    "administrador": "admin",   # alias
    "admin":         "admin",
    "analista":      "analyst",
    "analyst":       "analyst",
    "marketing":     "marketing",
}

_EMAIL_PATTERN = re.compile(r"^[\w\.\+\-]+@[\w\.-]+\.\w{2,}$")


def registrar_usuario(nombre: str, email: str, rol: str, password: str) -> tuple[bool, str]:
    """
    Registra un nuevo usuario en la base de datos.

    BUG CORREGIDO:
        La versión anterior normalizaba `rol` a minúsculas antes de buscar en el dict,
        pero las claves estaban capitalizadas ("Administrador"), por lo que
        "Administrador".lower() = "administrador" nunca coincidía y siempre
        guardaba "analyst" por defecto.

    Returns:
        (True, mensaje) en éxito, (False, mensaje) en error.
    """
    import bcrypt

    # --- Validaciones básicas ---
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío."

    if not email or not _EMAIL_PATTERN.match(email.strip()):
        return False, "El formato del correo electrónico no es válido."

    if not password or len(password) < _MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {_MIN_PASSWORD_LENGTH} caracteres."

    # --- Mapeo de rol (insensible al caso) ---
    # FIX CLAVE: comparar en minúsculas para no depender de capitalización
    db_role = _ROLE_MAP.get(rol.strip().lower(), None)
    if db_role is None:
        # Rol desconocido → seguro por defecto
        db_role = "analyst"

    # --- Hash de contraseña con bcrypt ---
    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")
    except Exception as e:
        return False, f"Error al proteger la contraseña: {e}"

    # --- Inserción en DB ---
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO user (name, email, rol, password_hash) VALUES (%s, %s, %s, %s)",
            (nombre.strip(), email.strip().lower(), db_role, password_hash),
        )

        conexion.commit()
        safe_close(conexion)
        return True, "Usuario registrado exitosamente."

    except Exception as e:
        print(f"Error registrando usuario: {e}")
        if "Duplicate entry" in str(e):
            return False, "El correo ya está registrado."
        return False, str(e)

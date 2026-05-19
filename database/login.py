from database.connection import conectar, safe_close


def validar_usuario(email: str, password: str) -> str | None:
    """
    Valida las credenciales del usuario y retorna su rol si son correctas.

    Soporta:
    - Contraseñas con hash bcrypt (nuevo, seguro)
    - Contraseñas en texto plano almacenadas previamente (compatibilidad retroactiva)

    Returns:
        El rol del usuario como string, o None si las credenciales son inválidas.
    """
    try:
        import bcrypt

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT rol, password_hash FROM user WHERE email = %s",
            (email,),
        )
        row = cursor.fetchone()
        safe_close(conexion)

        if not row:
            return None

        rol, stored_hash = row[0], row[1]

        if not stored_hash:
            return None

        password_bytes = password.encode("utf-8")
        stored_bytes = stored_hash.encode("utf-8") if isinstance(stored_hash, str) else stored_hash

        # Intentar verificación bcrypt
        try:
            if bcrypt.checkpw(password_bytes, stored_bytes):
                return str(rol)
        except Exception:
            pass

        # Compatibilidad retroactiva: contraseñas en texto plano
        if stored_hash == password:
            return str(rol)

        return None

    except Exception as e:
        print(f"Error en validación DB: {e}")
        import traceback
        traceback.print_exc()
        return None

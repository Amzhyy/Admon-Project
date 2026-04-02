from database.connection import conectar

def registrar_usuario(nombre, email, rol, password):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        
        # Mapeo de rol legible a ENUM de la base de datos
        role_map = {
            "Administrador": "admin",
            "Analista": "analyst",
            "Marketing": "marketing",
            "admin": "admin",
            "analyst": "analyst",
            "marketing": "marketing"
        }
        db_role = role_map.get(rol.lower(), "analyst")
        
        query = "INSERT INTO user (name, email, rol, password_hash) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, email, db_role, password))
        
        conexion.commit()
        conexion.close()
        return True, "Usuario registrado exitosamente."
    except Exception as e:
        print(f"Error registrando usuario: {e}")
        if "Duplicate entry" in str(e):
            return False, "El correo ya está registrado."
        return False, str(e)

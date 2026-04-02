from database.connection import conectar

def validar_usuario(email, password):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        query = "SELECT rol FROM user WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        conexion.close()
        
        if user:
            return str(user[0])  # Retorna el rol como string
        return None
    except Exception as e:
        print(f"Error en validación DB: {e}")
        import traceback
        traceback.print_exc()
        return None

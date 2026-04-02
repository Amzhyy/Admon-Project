from database.connection import conectar

def registrar_click(email_str):
    """
    Función utilitaria para registrar un clic en un correo enviado.
    Busca el correo en la tabla 'email' por el string de correo del usuario.
    """
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        
        # Buscar el id_email basado en el correo del usuario
        query_find = """
            SELECT e.id_email 
            FROM email e
            JOIN user u ON e.id_user = u.id_user
            WHERE u.email = %s
            ORDER BY e.id_email DESC LIMIT 1
        """
        cursor.execute(query_find, (email_str,))
        res = cursor.fetchone()
        
        if res:
            id_email = res[0]
            # Verificar si ya existe un registro en 'result' para este correo
            cursor.execute("SELECT id_result, clic FROM result WHERE id_email = %s", (id_email,))
            result_row = cursor.fetchone()
            
            if result_row:
                # Incrementar clic
                id_result = result_row[0]
                nuevo_clic = result_row[1] + 1
                cursor.execute("UPDATE result SET clic = %s WHERE id_result = %s", (nuevo_clic, id_result))
            else:
                # Insertar nuevo registro de clic
                cursor.execute("INSERT INTO result (id_email, clic, report) VALUES (%s, 1, '')", (id_email,))
            
            conexion.commit()
            print(f"Éxito: Clic registrado para {email_str}")
        else:
            print(f"Error: No se encontró un correo enviado para {email_str}")
            
        conexion.close()
    except Exception as e:
        print(f"Error registrando clic: {e}")

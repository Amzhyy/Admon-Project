from database.connection import conectar

# Almacenamiento temporal de códigos de recuperación (En una app real, usar tabla DB o Redis)
_RECOVERY_CODES = {}

def enviar_codigo_recuperacion(email):
    import random
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT name FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        conexion.close()
        
        if not user:
            return False, "El correo no está registrado en el sistema."
        
        nombre = user[0]
        codigo = str(random.randint(100000, 999999))
        _RECOVERY_CODES[email] = codigo
        
        # Enviar correo con el código
        asunto = "Código de recuperación de contraseña"
        cuerpo_html = f"""
        <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; border: 1px solid #eee; padding: 30px;">
            <h2 style="color: #2b3e50;">Recuperación de Contraseña</h2>
            <p>Hola <b>{nombre}</b>,</p>
            <p>Has solicitado restablecer tu contraseña. Tu código de seguridad es:</p>
            <div style="background: #f4f4f4; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #0067b8;">
                {codigo}
            </div>
            <p style="margin-top: 30px; font-size: 13px; color: #777;">Si no solicitaste este cambio, puedes ignorar este correo.</p>
        </div>
        """
        
        # Reutilizar lógica de envío
        return enviar_correo_generico(email, asunto, cuerpo_html)
        
    except Exception as e:
        print(f"Error en envío de recuperación: {e}")
        return False, str(e)

def verificar_codigo_y_cambiar_password(email, codigo, nueva_password):
    try:
        if email not in _RECOVERY_CODES or _RECOVERY_CODES[email] != str(codigo):
            return False, "El código de verificación es incorrecto o ha expirado."
        
        conexion = conectar()
        cursor = conexion.cursor()
        query = "UPDATE user SET password_hash = %s WHERE email = %s"
        cursor.execute(query, (nueva_password, email))
        
        if cursor.rowcount == 0:
            conexion.close()
            return False, "No se pudo actualizar la contraseña."
            
        conexion.commit()
        conexion.close()
        
        # Limpiar el código usado
        _RECOVERY_CODES.pop(email, None)
        return True, "Contraseña actualizada exitosamente."
        
    except Exception as e:
        print(f"Error cambiando password: {e}")
        return False, str(e)

def enviar_correo_generico(destinatario, asunto, html_content):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Credenciales configuradas anteriormente
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    # IMPORTANTE: Configurar con credenciales reales para producción
    SENDER_EMAIL = "tu-correo@gmail.com"
    SENDER_PASSWORD = "tu-app-password"

    msg = MIMEMultipart()
    msg['From'] = f"Seguridad Admon <{SENDER_EMAIL}>"
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Correo enviado."
    except Exception as e:
        return False, str(e)

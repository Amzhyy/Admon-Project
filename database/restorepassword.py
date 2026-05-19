import random
import time
from database.connection import conectar, safe_close

# Tiempo de vida del código de recuperación en segundos (15 minutos)
_CODE_TTL_SECONDS = 15 * 60

# Estructura: { email: (codigo, timestamp_creacion) }
_RECOVERY_CODES: dict[str, tuple[str, float]] = {}


def _limpiar_codigos_expirados() -> None:
    """Elimina códigos que ya pasaron su tiempo de vida."""
    now = time.time()
    expired = [email for email, (_, ts) in _RECOVERY_CODES.items() if now - ts > _CODE_TTL_SECONDS]
    for email in expired:
        _RECOVERY_CODES.pop(email, None)


def enviar_codigo_recuperacion(email: str) -> tuple[bool, str]:
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT name FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        safe_close(conexion)

        if not user:
            return False, "El correo no está registrado en el sistema."

        nombre = user[0]

        _limpiar_codigos_expirados()

        codigo = str(random.randint(100000, 999999))
        _RECOVERY_CODES[email] = (codigo, time.time())

        asunto = "Código de recuperación de contraseña"
        cuerpo_html = f"""
        <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;
                    border: 1px solid #eee; padding: 30px; border-radius: 8px;">
            <h2 style="color: #2b3e50;">Recuperación de Contraseña</h2>
            <p>Hola <b>{nombre}</b>,</p>
            <p>Has solicitado restablecer tu contraseña. Tu código de seguridad es:</p>
            <div style="background: #f4f4f4; padding: 20px; text-align: center;
                        font-size: 32px; font-weight: bold; letter-spacing: 8px;
                        color: #0067b8; border-radius: 6px; margin: 20px 0;">
                {codigo}
            </div>
            <p style="color: #e53e3e; font-weight: bold;">
                ⏰ Este código expira en 15 minutos.
            </p>
            <p style="font-size: 13px; color: #777;">
                Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
            </p>
        </div>
        """

        return enviar_correo_generico(email, asunto, cuerpo_html)

    except Exception as e:
        print(f"Error en envío de recuperación: {e}")
        return False, str(e)


def verificar_codigo_y_cambiar_password(
    email: str, codigo: str, nueva_password: str
) -> tuple[bool, str]:
    """
    Verifica el código y actualiza la contraseña con hash bcrypt.
    """
    import bcrypt

    _limpiar_codigos_expirados()

    entry = _RECOVERY_CODES.get(email)
    if not entry:
        return False, "El código ha expirado o no existe. Solicita uno nuevo."

    stored_code, timestamp = entry

    # Verificar expiración manualmente (doble check)
    if time.time() - timestamp > _CODE_TTL_SECONDS:
        _RECOVERY_CODES.pop(email, None)
        return False, "El código ha expirado. Solicita uno nuevo."

    if stored_code != str(codigo).strip():
        return False, "El código de verificación es incorrecto."

    if not nueva_password or len(nueva_password) < 8:
        return False, "La nueva contraseña debe tener al menos 8 caracteres."

    try:
        password_hash = bcrypt.hashpw(
            nueva_password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE user SET password_hash = %s WHERE email = %s",
            (password_hash, email),
        )

        if cursor.rowcount == 0:
            safe_close(conexion)
            return False, "No se pudo actualizar la contraseña."

        conexion.commit()
        safe_close(conexion)

        # Invalidar el código usado
        _RECOVERY_CODES.pop(email, None)
        return True, "Contraseña actualizada exitosamente."

    except Exception as e:
        print(f"Error cambiando password: {e}")
        return False, str(e)


def enviar_correo_generico(destinatario: str, asunto: str, html_content: str) -> tuple[bool, str]:
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SMTP_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("[SMTP] Advertencia: credenciales SMTP no configuradas en variables de entorno.")
        return False, "Servicio de correo no configurado. Contacta al administrador."

    msg = MIMEMultipart()
    msg["From"] = f"Seguridad Admon <{SENDER_EMAIL}>"
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Correo enviado."
    except Exception as e:
        print(f"[SMTP] Error: {e}")
        return False, str(e)

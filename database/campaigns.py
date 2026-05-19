import os
import re
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database.connection import conectar, safe_close

# Credenciales SMTP centralizadas desde variables de entorno
def _get_smtp_config() -> dict:
    return {
        "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "email": os.getenv("SMTP_EMAIL", " ServicioSoporteCypher@gmail.com"),
        "password": os.getenv("SMTP_PASSWORD", "mamc txrk gyhc lggw"),
    }


_EMAIL_PATTERN = re.compile(r"^[\w\.\+\-]+@[\w\.-]+\.\w{2,}$")

_ATTACK_TYPE_MAP = {
    "Credenciales": "password_reset",
    "Urgencia":     "urgent_request",
    "Incentivo":    "survey_reward",
    "Malware":      "attachment_malware",
}

_SUBJECTS = {
    "password_reset":    "Acción Requerida: Actualización de Contraseña",
    "urgent_request":    "URGENTE: Problema con su cuenta",
    "survey_reward":     "Premio Reclamado: Encuesta de Satisfacción",
    "attachment_malware": "Notificación del sistema",
}


def enviar_correo_phishing(
    destinatario: str,
    attack_type: str,
    campaign_name: str,
    html_template: str | None = None,
    server: smtplib.SMTP | None = None,
) -> bool:
    cfg = _get_smtp_config()

    if not cfg["email"] or not cfg["password"]:
        print("[SMTP] Credenciales no configuradas — simulando envío (modo demo).")
        print(f"[DEMO] Correo phishing a: {destinatario} | Tipo: {attack_type}")
        return True  # Modo demo: no falla, solo imprime

    tracking_url = (
        f"{os.getenv('TRACKING_URL', 'http://localhost:8081')}"
        f"/click?email={destinatario}"
    )

    msg = MIMEMultipart()
    msg["From"] = f"Soporte TI <{cfg['email']}>"
    msg["To"] = destinatario
    msg["Subject"] = _SUBJECTS.get(attack_type, "Notificación del sistema")

    if html_template:
        body_html = (
            html_template
            .replace("{{click_url}}", tracking_url)
            .replace("{{email}}", destinatario)
        )
        msg.attach(MIMEText(body_html, "html"))
    else:
        if attack_type in ("password_reset", "Credenciales"):
            body = (
                f"Estimado usuario,\n\nTu contraseña expira hoy. "
                f"Por favor actualízala en:\n{tracking_url}\n\nCampaña: {campaign_name}"
            )
        elif attack_type in ("urgent_request", "Urgencia"):
            body = (
                f"Hemos detectado actividad inusual. Verifica tu identidad:\n"
                f"{tracking_url}\n\nCampaña: {campaign_name}"
            )
        else:
            body = f"Por favor revisa el enlace:\n{tracking_url}\n\nCampaña: {campaign_name}"
        msg.attach(MIMEText(body, "plain"))

    try:
        if server:
            server.send_message(msg)
            print(f"[SMTP] Enviado a {destinatario} (sesión reutilizada).")
            return True
        else:
            # timeout=10s evita que la UI se cuelgue si el servidor SMTP no responde
            tmp = smtplib.SMTP(cfg["server"], cfg["port"], timeout=10)
            tmp.ehlo()
            tmp.starttls()
            tmp.login(cfg["email"], cfg["password"])
            tmp.send_message(msg)
            tmp.quit()
            print(f"[SMTP] Enviado a {destinatario} (sesión individual).")
            return True
    except Exception as e:
        print(f"[SMTP] Error enviando a {destinatario}: {e}")
        return False


def _crear_usuario_objetivo(cursor, email: str) -> int:
    """
    Crea un registro 'objetivo' en la tabla `user` para un correo nuevo
    y devuelve su id_user.

    El usuario creado:
      - Tiene rol 'analyst' (no admin — sin privilegios elevados)
      - Tiene un hash bcrypt con bytes aleatorios → contraseña imposible de adivinar
        (queda en la DB para satisfacer la FK pero nadie puede hacer login con él)
      - Nombre derivado del correo (ej: 'ana.lopez@empresa.com' → 'Ana Lopez')

    Esto permite que las campañas se ejecuten contra cualquier correo sin requerir
    que el admin pre-registre a cada destinatario.
    """
    import bcrypt
    import secrets

    local_part = email.split("@", 1)[0]
    # Deja un nombre legible: "ana.lopez" → "Ana Lopez"
    name = local_part.replace(".", " ").replace("_", " ").replace("-", " ").strip().title()
    if not name:
        name = "Objetivo de Campaña"
    name = name[:60]

    # Hash bcrypt sobre bytes aleatorios → contraseña efectivamente imposible
    # de adivinar. El usuario nunca podrá iniciar sesión con esta cuenta a menos
    # que un admin se la restablezca explícitamente vía 'recuperar contraseña'.
    random_password = secrets.token_bytes(48)
    placeholder_hash = bcrypt.hashpw(random_password, bcrypt.gensalt(rounds=10)).decode("utf-8")

    cursor.execute(
        "INSERT INTO user (name, email, rol, password_hash) VALUES (%s, %s, %s, %s)",
        (name, email, "analyst", placeholder_hash),
    )
    return cursor.lastrowid


def crear_campana(
    name: str,
    attack_type: str,
    start_date,
    end_date,
    users_emails: str,
    qdate_to_str=None,
    html_template: str | None = None,
    progress_cb=None,
) -> tuple[bool, int | str]:
    """
    Crea una campaña y envía correos de simulación.

    Si se pasa `progress_cb`, se invoca por cada paso con (texto, valor, total)
    para que la UI muestre progreso. Sólo se llama si está definido.
    """
    def _progress(msg: str, value: int, total: int):
        if callable(progress_cb):
            try:
                progress_cb(msg, value, total)
            except Exception:
                pass

    try:
        if not users_emails or not users_emails.strip():
            return False, "La lista de correos está vacía."

        emails_raw = [e.strip() for e in users_emails.split(",") if e.strip()]
        emails_validos = [e for e in emails_raw if _EMAIL_PATTERN.match(e)]

        if not emails_validos:
            return False, "Ningún correo tiene un formato válido."

        total_pasos = len(emails_validos) + 3   # +3: insert campaign + smtp init + finalize
        paso = 0
        _progress("Insertando campaña en base de datos…", paso, total_pasos)

        db_attack_type = _ATTACK_TYPE_MAP.get(attack_type, "password_reset")

        start_str = qdate_to_str(start_date) if callable(qdate_to_str) else start_date
        end_str   = qdate_to_str(end_date)   if callable(qdate_to_str) else end_date

        conexion = conectar()
        cursor = conexion.cursor(buffered=True)

        cursor.execute(
            "INSERT INTO campaign (name, attack_type, start_date, end_date, stauts) "
            "VALUES (%s, %s, %s, %s, 'active')",
            (name, db_attack_type, start_str, end_str),
        )
        id_campaign = cursor.lastrowid
        paso += 1
        _progress("Conectando al servidor SMTP…", paso, total_pasos)

        # Iniciar sesión SMTP una sola vez
        cfg = _get_smtp_config()
        server = None
        if cfg["email"] and cfg["password"]:
            try:
                server = smtplib.SMTP(cfg["server"], cfg["port"], timeout=10)
                server.ehlo()
                server.starttls()
                server.login(cfg["email"], cfg["password"])
                print("[SMTP] Sesión masiva iniciada.")
            except Exception as smtp_err:
                print(f"[SMTP] Error iniciando sesión masiva: {smtp_err}")
                conexion.rollback()
                safe_close(conexion)
                return False, f"No se pudo conectar al servidor de correos: {smtp_err}"
        else:
            print("[SMTP] Modo demo — sin credenciales configuradas.")
        paso += 1

        enviados = 0
        auto_creados = 0
        for email in emails_validos:
            _progress(f"Enviando a {email}…", paso, total_pasos)
            # Buscar el usuario; si no existe, crearlo como "objetivo de simulación".
            # Esto es por la FK del schema (email.id_user → user.id_user) y porque
            # las campañas suelen dirigirse a empleados que no están registrados como
            # operadores del sistema.
            cursor.execute("SELECT id_user FROM user WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row:
                id_user = row[0]
            else:
                id_user = _crear_usuario_objetivo(cursor, email)
                auto_creados += 1

            cursor.execute(
                "INSERT INTO email (id_user, id_campaign) VALUES (%s, %s)",
                (id_user, id_campaign),
            )
            if enviar_correo_phishing(email, db_attack_type, name, html_template, server):
                enviados += 1
            paso += 1

        if auto_creados:
            print(f"[Campaña] {auto_creados} objetivo(s) nuevo(s) registrado(s) automáticamente.")

        _progress("Guardando cambios…", total_pasos - 1, total_pasos)

        if server:
            try:
                server.quit()
            except Exception:
                pass

        conexion.commit()
        safe_close(conexion)
        _progress("Campaña completada.", total_pasos, total_pasos)
        return True, enviados

    except Exception as e:
        print(f"Error creando campaña: {e}")
        traceback.print_exc()
        try:
            if conexion and conexion.is_connected():
                conexion.rollback()
        except Exception:
            pass
        safe_close(conexion)
        return False, str(e)


def obtener_campanas() -> list[dict]:
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "UPDATE campaign SET stauts = 'finished' "
            "WHERE stauts = 'active' AND end_date < CURDATE()"
        )
        conexion.commit()

        cursor.execute("""
            SELECT
                c.id_campaign,
                c.name,
                c.attack_type,
                c.stauts AS estado,
                c.start_date,
                COUNT(DISTINCT e.id_email)  AS usuarios,
                COALESCE(SUM(r.clic), 0)    AS clicks,
                COUNT(r.id_result)          AS aperturas,
                SUM(CASE WHEN r.report IS NOT NULL AND r.report != ''
                    THEN 1 ELSE 0 END)      AS reportes
            FROM campaign c
            LEFT JOIN email  e ON c.id_campaign = e.id_campaign
            LEFT JOIN result r ON e.id_email    = r.id_email
            GROUP BY c.id_campaign, c.name, c.attack_type, c.stauts, c.start_date
            ORDER BY c.start_date ASC
        """)
        campanas = cursor.fetchall()
        safe_close(conexion)
        return campanas
    except Exception as e:
        print(f"Error obteniendo campañas: {e}")
        traceback.print_exc()
        return []


def obtener_usuarios() -> list[dict]:
    """Retorna usuarios registrados para el selector de la IA."""
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_user, name, email, rol FROM user")
        usuarios = cursor.fetchall()
        safe_close(conexion)
        return usuarios
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []


def _find_model() -> str | None:
    """
    Localiza modelo_phishing.pkl de forma robusta. El modelo vive en la raíz
    del proyecto (un nivel arriba de `database/`), pero también se intenta el
    cwd actual y rutas relativas por si la app se lanzó desde otro lugar.
    """
    here = os.path.dirname(os.path.abspath(__file__))     # database/
    parent = os.path.dirname(here)                         # raíz del proyecto

    candidates = [
        os.path.join(parent, "modelo_phishing.pkl"),       # ../ (esperado)
        os.path.join(here,   "modelo_phishing.pkl"),       # ./database/
        os.path.join(os.getcwd(),         "modelo_phishing.pkl"),
        os.path.join(os.getcwd(), "..",   "modelo_phishing.pkl"),
        # Compatibilidad legacy
        os.path.join(parent, "phishing_model.pkl"),
        "modelo_phishing.pkl",
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


# Cache del modelo a nivel módulo — joblib.load es caro (~10ms),
# antes se ejecutaba en cada predicción (200+ veces por análisis).
_MODEL_CACHE: dict[str, object] = {}

# Cache de la duración de la última campaña — se consulta una sola vez por lote
_DURATION_CACHE: dict[str, int] = {}


def _load_model_cached():
    """Carga el modelo desde disco una sola vez por proceso."""
    path = _find_model()
    if not path:
        return None
    if path not in _MODEL_CACHE:
        import joblib
        _MODEL_CACHE[path] = joblib.load(path)
    return _MODEL_CACHE[path]


_ATTACK_DB_MAP = {
    0: "password_reset",
    1: "urgent_request",
    2: "survey_reward",
    3: "attachment_malware",
}


def predecir_riesgo_ia(
    id_user: int,
    attack_type_id: int,
    _conn=None,
    _duracion: int | None = None,
) -> tuple[float | None, int | str]:
    """
    Predice la probabilidad de que un usuario caiga en un ataque.

    Modelo:  modelo_phishing.pkl (LogisticRegression con 4 features en orden:
             attack_type_id, clics_previos_usuario, duracion_dias_campana, rol_usuario_id)

    Parámetros internos para lotes:
        _conn:     Conexión MySQL existente a reutilizar (evita open/close repetidos).
        _duracion: Duración de la última campaña pre-calculada.
    """
    import pandas as pd
    from database.connection import safe_close

    modelo = _load_model_cached()
    if modelo is None:
        return None, "Modelo ML no encontrado (modelo_phishing.pkl)."

    target_at = _ATTACK_DB_MAP.get(attack_type_id, "password_reset")

    own_connection = _conn is None
    conexion = None
    try:
        conexion = _conn if not own_connection else conectar()
        cursor = conexion.cursor(dictionary=True)

        # 1. Clics previos filtrados por tipo de ataque
        cursor.execute("""
            SELECT SUM(r.clic) AS total_clics
            FROM result r
            JOIN email    e ON r.id_email    = e.id_email
            JOIN campaign c ON e.id_campaign = c.id_campaign
            WHERE e.id_user = %s AND c.attack_type = %s
        """, (id_user, target_at))
        res_clics = cursor.fetchone()
        clics_previos = int(res_clics["total_clics"] or 0)

        # 2. Rol del usuario
        cursor.execute("SELECT rol FROM user WHERE id_user = %s", (id_user,))
        res_user = cursor.fetchone()
        if not res_user:
            cursor.close()
            return None, "Usuario no encontrado."

        rol_str = (res_user["rol"] or "analyst").lower()
        rol_id = 1 if "admin" in rol_str else 2

        # 3. Duración de la última campaña (cached o pre-calculado)
        if _duracion is not None:
            duracion_final = _duracion
        else:
            cursor.execute(
                "SELECT DATEDIFF(end_date, start_date) AS duracion "
                "FROM campaign ORDER BY id_campaign DESC LIMIT 1"
            )
            res_dur = cursor.fetchone()
            duracion_final = int(res_dur["duracion"]) if res_dur and res_dur["duracion"] else 7

        cursor.close()

        # 4. Predicción
        X_input = pd.DataFrame(
            [[attack_type_id, clics_previos, duracion_final, rol_id]],
            columns=["attack_type_id", "clics_previos_usuario",
                     "duracion_dias_campana", "rol_usuario_id"],
        )
        probabilidad = float(modelo.predict_proba(X_input)[0][1]) * 100
        return probabilidad, clics_previos

    except Exception as e:
        print(f"Error en predicción IA: {e}")
        return None, str(e)
    finally:
        if own_connection:
            from database.connection import safe_close
            safe_close(conexion)


def predecir_riesgo_lote(
    user_ids: list[int],
    attack_type_id: int,
) -> dict[int, tuple[float | None, int | str]]:
    """
    Versión batch de predecir_riesgo_ia.

    Usa UNA SOLA conexión + modelo cacheado + duración pre-calculada para
    procesar N usuarios sin el overhead de N×3 queries y N×open/close de DB.

    Resuelve el error 2055/WinError 10038 en Windows que aparece al abrir
    cientos de conexiones rápidas (estadísticas, tendencia peligrosa, etc.).

    Returns:
        { id_user: (probabilidad | None, clics_previos | error_str) }
    """
    from database.connection import safe_close

    resultados: dict[int, tuple] = {}
    if not user_ids:
        return resultados

    modelo = _load_model_cached()
    if modelo is None:
        return {uid: (None, "Modelo no encontrado") for uid in user_ids}

    conexion = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        # Pre-calcular la duración una sola vez para todo el lote
        cursor.execute(
            "SELECT DATEDIFF(end_date, start_date) AS duracion "
            "FROM campaign ORDER BY id_campaign DESC LIMIT 1"
        )
        res_dur = cursor.fetchone()
        duracion = int(res_dur["duracion"]) if res_dur and res_dur["duracion"] else 7
        cursor.close()

        for uid in user_ids:
            try:
                prob, clics = predecir_riesgo_ia(
                    uid, attack_type_id,
                    _conn=conexion,
                    _duracion=duracion,
                )
                resultados[uid] = (prob, clics)
            except Exception as ex:
                resultados[uid] = (None, str(ex))

    except Exception as e:
        print(f"Error en lote IA: {e}")
        for uid in user_ids:
            if uid not in resultados:
                resultados[uid] = (None, str(e))
    finally:
        safe_close(conexion)

    return resultados


def obtener_tendencia_peligrosa() -> tuple[str | None, float]:
    """
    Calcula la categoría de ataque con mayor riesgo promedio.

    Optimizado: usa predecir_riesgo_lote (4 conexiones totales en lugar de
    4 × N que es lo que generaba el error 2055 en Windows).
    """
    try:
        usuarios = obtener_usuarios()
        if not usuarios:
            return None, 0.0

        user_ids = [u["id_user"] for u in usuarios]
        mapping_nombres = {0: "Credenciales", 1: "Urgencia", 2: "Incentivo", 3: "Malware"}
        riesgos_promedio: dict[int, float] = {}

        for at_id in range(4):
            lote = predecir_riesgo_lote(user_ids, at_id)
            probs = [prob for prob, _ in lote.values() if prob is not None]
            if probs:
                riesgos_promedio[at_id] = sum(probs) / len(probs)

        if not riesgos_promedio:
            return None, 0.0

        peor_at_id = max(riesgos_promedio, key=riesgos_promedio.get)
        return mapping_nombres[peor_at_id], riesgos_promedio[peor_at_id]

    except Exception as e:
        print(f"Error obteniendo tendencia: {e}")
        return None, 0.0

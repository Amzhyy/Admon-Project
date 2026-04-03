from database.connection import conectar

def enviar_correo_phishing(destinatario, attack_type, campaign_name, html_template=None, server=None):
    """
    Simula o ejecuta el envío de un correo de phishing.
    Permite reutilizar una conexión SMTP existente si se provee el parámetro 'server'.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # IMPORTANTE: Reemplazar con credenciales reales para envío en producción
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "tu-correo@gmail.com"
    SENDER_PASSWORD = "tu-app-password"
    
    msg = MIMEMultipart()
    msg['From'] = f"Soporte TI <{SENDER_EMAIL}>"
    msg['To'] = destinatario
    
    # Asunto simulado según el ataque
    if attack_type == "password_reset" or attack_type == "Credenciales":
        msg['Subject'] = "Acción Requerida: Actualización de Contraseña"
    elif attack_type == "urgent_request" or attack_type == "Urgencia":
        msg['Subject'] = "URGENTE: Problema con su cuenta"
    elif attack_type == "survey_reward" or attack_type == "Incentivo":
         msg['Subject'] = "Premio Reclamado: Encuesta de Satisfacción"
    else:
        msg['Subject'] = "Notificación del sistema"
        
    tracking_url = f"http://localhost:8081/click?email={destinatario}"
    
    if html_template:
        html_template = html_template.replace("{{click_url}}", tracking_url)
        html_template = html_template.replace("{{email}}", destinatario)
        msg.attach(MIMEText(html_template, 'html'))
    else:
        if attack_type in ["password_reset", "Credenciales"]:
            body = f"Estimado usuario,\n\nTu contraseña expira hoy. Por favor actualízala en el siguiente enlace seguro:\n{tracking_url}\n\nCampaña: {campaign_name}"
        elif attack_type in ["urgent_request", "Urgencia"]:
            body = f"Hemos detectado actividad inusual. Verifica tu identidad inmediatamente:\n{tracking_url}\n\nCampaña: {campaign_name}"
        else:
            body = f"Por favor revisa el documento adjunto o enlace:\n{tracking_url}\n\nCampaña: {campaign_name}"
        msg.attach(MIMEText(body, 'plain'))
    
    print(f"\n[ENVIANDO] Procesando correo para {destinatario}...")
    
    try:
        if server:
            server.send_message(msg)
            print(f"Correo enviado exitosamente a {destinatario} (Sesión reutilizada).")
            return True
        else:
            # Si no hay servidor provisto, abrir uno nuevo (fallback)
            temp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            temp_server.starttls()
            temp_server.login(SENDER_EMAIL, SENDER_PASSWORD)
            temp_server.send_message(msg)
            temp_server.quit()
            print(f"Correo enviado exitosamente a {destinatario} (Sesión individual).")
            return True
    except Exception as e:
        print(f"Error enviando correo SMTP a {destinatario}: {e}")
        return False

def crear_campana(name, attack_type, start_date, end_date, users_emails, qdate_to_str=None, html_template=None):
    try:
        import re
        if not users_emails or not users_emails.strip():
            return False, "La lista de correos está vacía."
            
        emails_raw = [e.strip() for e in users_emails.split(",") if e.strip()]
        if not emails_raw:
            return False, "La lista de correos está vacía."
            
        emails_validos = []
        email_pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        for email in emails_raw:
            if email_pattern.match(email):
                emails_validos.append(email)
                
        if not emails_validos:
            return False, "Ningún correo proporcionado tiene un formato válido."

        conexion = conectar()
        # Usamos buffered=True para evitar problemas con múltiples resultados simultáneos
        cursor = conexion.cursor(buffered=True)
        
        # Mapeo de attack_type de la UI al ENUM de la base de datos
        mapping = {
            "Credenciales": "password_reset",
            "Urgencia": "urgent_request",
            "Incentivo": "survey_reward",
            "Malware": "attachment_malware"
        }
        db_attack_type = mapping.get(attack_type, "password_reset")
        
        # Insertar campaña
        query = "INSERT INTO campaign (name, attack_type, start_date, end_date, stauts) VALUES (%s, %s, %s, %s, 'active')"
        
        if callable(qdate_to_str):
            start_str = qdate_to_str(start_date)
            end_str = qdate_to_str(end_date)
        else:
            start_str = start_date
            end_str = end_date
            
        cursor.execute(query, (name, db_attack_type, start_str, end_str))
        id_campaign = cursor.lastrowid
        
        # --- Configurar SMTP ÚNICO ---
        import smtplib
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = "tu-correo@gmail.com"
        SENDER_PASSWORD = "tu-app-password"
        
        server = None
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("[SMTP] Sesión iniciada para envío masivo.")
        except Exception as smtp_err:
            print(f"[SMTP] Error al iniciar sesión masiva: {smtp_err}")
            # Si no se puede iniciar sesión, fallamos la creación de campaña
            conexion.rollback()
            conexion.close()
            return False, f"No se pudo conectar al servidor de correos: {smtp_err}"

        # Enviar correos y guardar en la base de datos
        enviados = 0
        
        for email in emails_validos:
            # Buscar el ID del usuario
            cursor.execute("SELECT id_user FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                id_user = user[0]
                # Insertar registro de correo enviado
                cursor.execute("INSERT INTO email (id_user, id_campaign) VALUES (%s, %s)", (id_user, id_campaign))
                
                # Enviar correo real usando el servidor persistente
                sent_ok = enviar_correo_phishing(email, db_attack_type, name, html_template, server=server)
                if sent_ok:
                    enviados += 1
            else:
                print(f"Advertencia: el correo {email} no pertenece a ningún usuario registrado (omitido).")
                
        # Cerrar servidor SMTP
        if server:
            try:
                server.quit()
                print("[SMTP] Sesión cerrada.")
            except:
                pass
                
        conexion.commit()
        conexion.close()
        return True, enviados
    except Exception as e:
        print(f"Error al crear campaña: {e}")
        import traceback
        traceback.print_exc()
        if 'conexion' in locals() and conexion.is_connected():
            conexion.rollback()
            conexion.close()
        return False, str(e)

def obtener_campanas():
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        
        # --- Actualizar campañas vencidas automáticamente ---
        update_query = "UPDATE campaign SET stauts = 'finished' WHERE stauts = 'active' AND end_date < CURDATE()"
        cursor.execute(update_query)
        conexion.commit()

        # Ajustamos la consulta para contar clics reales de la tabla result
        query = """
            SELECT 
                c.id_campaign, 
                c.name, 
                c.attack_type, 
                c.stauts as estado,
                c.start_date,
                COUNT(DISTINCT e.id_email) as usuarios,
                COALESCE(SUM(r.clic), 0) as clicks,
                COUNT(r.id_result) as aperturas,
                SUM(CASE WHEN r.report IS NOT NULL AND r.report != '' THEN 1 ELSE 0 END) as reportes
            FROM campaign c
            LEFT JOIN email e ON c.id_campaign = e.id_campaign
            LEFT JOIN result r ON e.id_email = r.id_email
            GROUP BY c.id_campaign, c.name, c.attack_type, c.stauts, c.start_date
            ORDER BY c.start_date ASC
        """
        cursor.execute(query)
        campanas = cursor.fetchall()
        conexion.close()
        return campanas
    except Exception as e:
        print(f"Error obteniendo campañas DB: {e}")
        import traceback
        traceback.print_exc()
        return []

def obtener_usuarios():
    """Retorna todos los usuarios registrados para el selector de la IA."""
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_user, name, email, rol FROM user")
        usuarios = cursor.fetchall()
        conexion.close()
        return usuarios
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []

def predecir_riesgo_ia(id_user, attack_type_id):
    """
    Carga el modelo ML y predice la probabilidad de caída.
    attack_type_id: 0: Credenciales, 1: Urgencia, 2: Incentivo, 3: Malware
    """
    import joblib
    import numpy as np
    import os
    import pandas as pd
    
    # Buscar el modelo en el directorio actual o en el padre (raíz del proyecto)
    model_filenames = ['modelo_phishing.pkl', 'phishing_model.pkl']
    model_path = None
    
    for filename in model_filenames:
        if os.path.exists(filename):
            model_path = filename
            break
        # Buscar en el directorio padre (si estamos dentro de admon_project o database)
        parent_path = os.path.join('..', filename)
        if os.path.exists(parent_path):
            model_path = parent_path
            break
            
    if not model_path:
        return None, f"Archivo de modelo '{model_filenames[0]}' no encontrado. Asegúrese de que esté en la raíz del proyecto."

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        
        # Mapeo de IDs a strings de la base de datos
        mapping_db = {0: "password_reset", 1: "urgent_request", 2: "survey_reward", 3: "attachment_malware"}
        target_at = mapping_db.get(attack_type_id, "password_reset")

        # 1. Obtener Clics previos Filtrados por CATEGORÍA DE ATAQUE
        query_clics = """
            SELECT SUM(r.clic) as total_clics 
            FROM result r
            JOIN email e ON r.id_email = e.id_email
            JOIN campaign c ON e.id_campaign = c.id_campaign
            WHERE e.id_user = %s AND c.attack_type = %s
        """
        cursor.execute(query_clics, (id_user, target_at))
        res_clics = cursor.fetchone()
        clics_previos = res_clics['total_clics'] if res_clics['total_clics'] else 0
        
        # 2. Obtener Rol del usuario y mapear a ID
        cursor.execute("SELECT rol FROM user WHERE id_user = %s", (id_user,))
        res_user = cursor.fetchone()
        conexion.close()
        
        if not res_user:
            return None, "Usuario no encontrado."
            
        rol_str = res_user['rol'].lower() if res_user['rol'] else "analista"
        rol_id = 1 if "admin" in rol_str else 2
        
        # 3. Preparar datos para el modelo
        # Se obtiene dinámicamente la duración de la última campaña registrada (ya que es constante)
        cursor.execute("SELECT DATEDIFF(end_date, start_date) as duracion FROM campaign ORDER BY id_campaign DESC LIMIT 1")
        res_dur = cursor.fetchone()
        duracion_final = res_dur['duracion'] if res_dur and res_dur['duracion'] is not None else 7

        X_input = pd.DataFrame([[attack_type_id, clics_previos, duracion_final, rol_id]], 
                               columns=['attack_type_id', 'clics_previos_usuario', 'duracion_dias_campana', 'rol_usuario_id'])
        
        # 4. Cargar modelo y predecir
        modelo = joblib.load(model_path)
        probabilidad = modelo.predict_proba(X_input)[0][1]
        
        return float(probabilidad * 100), clics_previos
        
    except Exception as e:
        print(f"Error en predicción IA: {e}")
        return None, str(e)

def obtener_tendencia_peligrosa():
    """Analiza a todos los usuarios contra todos los ataques y halla la tendencia más factible."""
    try:
        usuarios = obtener_usuarios()
        if not usuarios:
            return None, 0
            
        mapping_nombres = {0: "Credenciales", 1: "Urgencia", 2: "Incentivo", 3: "Malware"}
        riesgos_promedio = {}
        
        for at_id in range(4):
            total_prob = 0
            count = 0
            for u in usuarios:
                prob, _ = predecir_riesgo_ia(u['id_user'], at_id)
                if prob is not None:
                    total_prob += prob
                    count += 1
            if count > 0:
                riesgos_promedio[at_id] = total_prob / count
        
        if not riesgos_promedio:
            return None, 0
            
        # Hallar el ID con mayor riesgo
        peor_at_id = max(riesgos_promedio, key=riesgos_promedio.get)
        return mapping_nombres[peor_at_id], riesgos_promedio[peor_at_id]
        
    except Exception as e:
        print(f"Error obteniendo tendencia: {e}")
        return None, 0

# Manual Operativo: Sistema Inteligente de Simulación de Phishing

Este manual proporciona las instrucciones necesarias para la instalación, configuración, operación y mantenimiento del **Sistema Inteligente de Simulación de Phishing (Admon-Project)**. El sistema está diseñado para evaluar la vulnerabilidad de los usuarios ante ataques de phishing mediante simulaciones controladas y análisis de datos con Inteligencia Artificial.

---

## 1. Procedimientos de Instalación

### Requisitos Previos
*   **Sistema Operativo:** Windows 10/11 (Recomendado).
*   **Lenguaje:** Python 3.10 o superior.
*   **Base de Datos:** MySQL Server 8.0 o superior.
*   **Gestor de Paquetes:** `pip`.

### Pasos de Instalación
1.  **Clonar/Descargar el Proyecto:** Extraer los archivos en una carpeta local (ej. `C:\Proyectos\Admon-Project`).
2.  **Configurar Entorno Virtual (Opcional pero recomendado):**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3.  **Instalar Dependencias:**
    Ejecutar el siguiente comando desde la raíz del proyecto:
    ```powershell
    pip install -r Admon_Project/requirements.txt
    ```
4.  **Configurar la Base de Datos:**
    *   Abrir MySQL Workbench o una terminal de MySQL.
    *   Ejecutar el script `ADMON.sql` ubicado en la raíz del proyecto para crear la base de datos `admon_project` y sus tablas.

---

## 2. Configuración del Sistema

### A. Base de Datos (MySQL)
La conexión se configura en el archivo `database/connection.py`.
```python
# database/connection.py
conexion = mysql.connector.connect(
    host="localhost",
    user="root",        # Cambiar según su usuario
    password="moy123",  # Cambiar según su contraseña
    database="admon_project"
)
```

### B. Servidor de Correo (SMTP)
Para el envío de correos de recuperación y simulaciones, se utiliza el servidor SMTP de Gmail. La configuración se encuentra en `database/restorepassword.py`.
*   **Servidor:** `smtp.gmail.com`
*   **Puerto:** 587 (TLS)
*   **Credenciales:** Debe generar una "Contraseña de Aplicación" en su cuenta de Google.
*   **Archivo:** Modificar `SENDER_EMAIL` y `SENDER_PASSWORD` en la función `enviar_correo_generico`.

### C. Modelo de IA
El sistema utiliza un modelo de **Regresión Logística** entrenado para predecir riesgos.
*   **Archivo del modelo:** `modelo_phishing.pkl`.
*   **Entrenamiento:** Si desea actualizar el modelo con nuevos datos, ejecute:
    ```powershell
    python train.py
    ```
    Esto leerá `phishing_dataset.csv` y generará un nuevo archivo `.pkl`.

---

## 3. Ejecución de Campañas de Phishing

### Inicio de la Aplicación
Ejecute el archivo principal desde la carpeta `Admon_Project`:
```powershell
python Admon_Project/main.py
```

### Pasos para crear una campaña:
1.  **Iniciar Sesión:** Ingrese con sus credenciales de Administrador o Analista.
2.  **Navegar al Simulador:** Seleccione "Simulador de phishing" en el menú lateral.
3.  **Nueva Campaña:** Haga clic en "Nueva Campaña".
4.  **Configurar:**
    *   **Nombre:** Identificador de la campaña.
    *   **Tipo de Ataque:** Seleccione entre Credenciales, Urgencia, Incentivo o Malware.
    *   **Fechas:** Defina el periodo de ejecución.
    *   **Usuarios:** Ingrese los correos corporativos separados por coma.
    *   **Plantilla HTML:** (Opcional) Pegue el código HTML para el cuerpo del correo.
5.  **Enviar:** Al hacer clic en "Crear Campaña", el sistema enviará automáticamente los correos de simulación.

---

## 4. Generación de Reportes e Interfaz Gráfica

La interfaz gráfica permite visualizar los resultados de manera intuitiva:

### Visualización de Resultados
*   **Módulo de Estadísticas:** Muestra gráficos comparativos de aperturas, clics y reportes por campaña.
*   **Tendencia Histórica:** Gráfico de líneas que muestra la evolución de la tasa de clics en el tiempo.
*   **Exportación:** Botón "Exportar PDF" para generar un resumen ejecutivo del estado actual de la seguridad.

### Análisis de Riesgo con IA
*   **Predictor de Vulnerabilidad:** Seleccione un usuario y un tipo de ataque hipotético. El sistema calculará la probabilidad (0-100%) de que el usuario caiga en la trampa basándose en su comportamiento histórico.
*   **Recomendaciones:** El sistema muestra cuadros de texto con consejos preventivos generados automáticamente según las tendencias detectadas.

---

## 5. Mantenimiento Básico del Sistema

### Copias de Seguridad
Se recomienda exportar la base de datos periódicamente:
```powershell
mysqldump -u root -p admon_project > backup_fecha.sql
```

### Actualización del Dataset
A medida que se ejecutan más campañas, los resultados se guardan en la base de datos. Para mejorar la precisión de la IA:
1.  Exportar los nuevos datos de la tabla `campaña_usuario` a `phishing_dataset.csv`.
2.  Ejecutar `train.py` para reentrenar el modelo.

### Soporte de Interfaz
Si la interfaz no carga correctamente:
*   Verificar que `PyQt6` esté instalado correctamente.
*   Asegurarse de que el servidor MySQL esté activo.
*   Revisar que las rutas en `main.py` apunten correctamente a los subdirectorios `components/`, `screens/` y `styles/`.

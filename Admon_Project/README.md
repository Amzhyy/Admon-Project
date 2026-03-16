# Dashboard de simulación de phishing (Escritorio)

Aplicación de escritorio en Python con PyQt6 que muestra un dashboard similar al de la imagen de referencia, con las siguientes secciones:

- Inicio de sesión  
- Sobre nosotros  
- Detector de vulnerabilidades  
- Simulador de phishing  
- Estadísticas  

Todo el diseño usa un tema oscuro azulado con acentos en azul brillante, pensado para un entorno de ciberseguridad.

## Requisitos

- Python 3.10 o superior instalado.

## Instalación

Desde la carpeta del proyecto (`Admon_Pez`), ejecuta:

```bash
pip install -r requirements.txt
```

Si usas PowerShell:

```powershell
pip install -r .\requirements.txt
```

## Ejecución

Desde la misma carpeta:

```bash
python main.py
```

o en PowerShell:

```powershell
python .\main.py
```

Se abrirá una ventana con:

- Menú lateral con: Inicio de sesión, Sobre nosotros, Detector de vulnerabilidades, Simulador de phishing y Estadísticas.  
- Área principal con tarjetas y textos simulando formularios, KPIs y tablas del sistema.

Este proyecto es un punto de partida visual; puedes conectar la lógica real (APIs, base de datos, etc.) a cada sección según tus necesidades.


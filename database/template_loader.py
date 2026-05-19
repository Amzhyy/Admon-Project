"""
Cargador de plantillas HTML — detecta automáticamente los archivos en
`email_templates/` y los expone para los selectores de la UI.

Convenciones:
- Los archivos deben estar en la carpeta `email_templates/` en la raíz del proyecto.
- Solo se cargan archivos con extensión `.html`.
- El nombre del archivo (sin extensión) se usa como nombre visible.
- Los placeholders soportados en cualquier plantilla son:
    {{email}}     → correo del destinatario
    {{click_url}} → URL de rastreo de clic
"""

import os
from dataclasses import dataclass


@dataclass
class EmailTemplate:
    """Plantilla HTML de correo cargada desde disco."""
    name: str          # Nombre visible (ej: "Apple ID Security")
    file_name: str     # Nombre con extensión (ej: "Apple ID Security.html")
    path: str          # Ruta absoluta al archivo
    content: str       # HTML completo
    size_kb: float     # Tamaño aproximado en KB


def _get_templates_dir() -> str:
    """
    Resuelve la ruta absoluta a `email_templates/` probando varias
    ubicaciones para soportar dos layouts:

      LAYOUT A (database/ DENTRO de Admon_Project/):
        project/Admon_Project/database/template_loader.py
        project/Admon_Project/email_templates/

      LAYOUT B (database/ FUERA de Admon_Project/  ← layout actual):
        project/database/template_loader.py
        project/Admon_Project/email_templates/
    """
    here = os.path.dirname(os.path.abspath(__file__))   # database/
    parent = os.path.dirname(here)                       # padre de database/

    candidates = [
        # LAYOUT B (database/ fuera): templates en Admon_Project/
        os.path.join(parent, "Admon_Project", "email_templates"),
        # LAYOUT A (database/ dentro): templates al lado de main.py
        os.path.join(parent, "email_templates"),
        # Como último recurso, dentro de la propia carpeta database/
        os.path.join(here, "email_templates"),
        # cwd-relativos (lanzamientos desde otra carpeta)
        os.path.join(os.getcwd(), "Admon_Project", "email_templates"),
        os.path.join(os.getcwd(), "email_templates"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)

    # Fallback: la ruta donde DEBERÍA estar (para mostrar al usuario en mensajes)
    return os.path.abspath(os.path.join(parent, "Admon_Project", "email_templates"))


def list_templates() -> list[EmailTemplate]:
    """
    Retorna todas las plantillas .html disponibles, ordenadas alfabéticamente.
    Si la carpeta no existe o está vacía, retorna lista vacía.
    """
    folder = _get_templates_dir()
    if not os.path.isdir(folder):
        return []

    templates: list[EmailTemplate] = []
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".html"):
            continue
        full_path = os.path.join(folder, filename)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            templates.append(EmailTemplate(
                name=os.path.splitext(filename)[0],
                file_name=filename,
                path=full_path,
                content=content,
                size_kb=round(len(content) / 1024, 1),
            ))
        except Exception as e:
            print(f"[templates] Error leyendo {filename}: {e}")
            continue

    return templates


def load_template_by_name(name: str) -> EmailTemplate | None:
    """Carga una plantilla por su nombre visible (sin extensión)."""
    for tpl in list_templates():
        if tpl.name == name:
            return tpl
    return None


def get_templates_folder() -> str:
    """Retorna la ruta absoluta de la carpeta de plantillas (para mostrar al usuario)."""
    return _get_templates_dir()

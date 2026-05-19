"""
Wrapper para arrancar el servidor de tracking desde la raíz del proyecto.

La lógica real vive en `database/tracking.py` para que sea el único punto
de mantenimiento. Este archivo solo existe por compatibilidad con la
documentación previa (`python tracking_server.py`).

Equivalente a:
    python database/tracking.py [puerto]
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from database.tracking import _run_server  # noqa: E402

if __name__ == "__main__":
    port = 8081
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    _run_server(port)

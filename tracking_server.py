import http.server
import socketserver
import urllib.parse
import os
import sys

# Asegurar que podemos importar database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.tracking import registrar_click

PORT = 8081

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/click":
            params = urllib.parse.parse_qs(parsed_url.query)
            email = params.get("email", [None])[0]
            
            if email:
                print(f"\n[SERVER] Click detectado de: {email}")
                registrar_click(email)
                
                # Respuesta visual al usuario "fisehado"
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                html_response = f"""
                <html>
                <body style="font-family: sans-serif; text-align: center; padding-top: 100px; background-color: #f8d7da; color: #721c24;">
                    <h1 style="font-size: 50px;">🔴¡HAS SIDO PHISHEADO!</h1>
                    <p style="font-size: 20px;">Esta es una simulación de seguridad de <b>Admon-Project</b>.</p>
                    <p>En un ataque real, tus datos habrían sido comprometidos.</p>
                    <hr style="max-width: 400px;">
                    <p style="font-size: 14px; color: #444;">Tu clic ha sido registrado para fines estadísticos.</p>
                    <div style="margin-top: 30px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/564/564619.png" width="100">
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html_response.encode('utf-8'))
                return
        
        # Respuesta por defecto para otras rutas
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PhishingHandler) as httpd:
        print(f"Servidor de tracking corriendo en http://localhost:{PORT}")
        print("Manten esta terminal abierta para registrar los clics de los correos.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
            httpd.shutdown()

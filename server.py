import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Habilitar CORS y encabezados adecuados
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run():
    # Render asigna dinámicamente el puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 3000))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, CustomHandler)
    print(f"[✓] Servidor web iniciado en el puerto {port} (0.0.0.0:{port})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        sys.exit(0)

if __name__ == "__main__":
    run()

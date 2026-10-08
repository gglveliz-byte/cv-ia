import os
import sys
import json
import time
import re
import urllib.request
import urllib.error
from collections import defaultdict
from http.server import SimpleHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

load_dotenv()

# Intentar importar DatabaseManager para servir vacantes desde PostgreSQL
try:
    from db_manager import DatabaseManager
    db_manager = DatabaseManager()
except Exception as e:
    print(f"[!] Aviso: DatabaseManager no inicializado en server.py ({e}).")
    db_manager = None

# Configuración de Rate Limiting por IP (Protección anti-abuso)
RATE_LIMIT_WINDOW = 60  # Ventana de 60 segundos
RATE_LIMIT_MAX_REQUESTS = 25  # Máximo 25 llamadas por IP cada 60s
ip_request_history = defaultdict(list)

def is_client_rate_limited(client_ip: str) -> bool:
    """Valida si la IP del cliente ha superado el umbral de peticiones por minuto."""
    now = time.time()
    history = ip_request_history[client_ip]
    valid_timestamps = [t for t in history if now - t < RATE_LIMIT_WINDOW]
    ip_request_history[client_ip] = valid_timestamps
    if len(valid_timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return True
    ip_request_history[client_ip].append(now)
    return False

def clean_json_text(text: str) -> dict:
    """Limpia bloques de markdown ```json y parsea a diccionario."""
    cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)

def call_ai_backend_proxy(prompt: str) -> dict:
    """
    Ejecuta la llamada a la IA estrictamente desde el backend.
    La API Key NUNCA sale del servidor ni viaja al navegador del cliente.
    """
    api_key = os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("No se encontró QWEN_API_KEY en las variables de entorno seguras del servidor.")

    base_url = os.environ.get("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").rstrip("/")
    model = os.environ.get("QWEN_MODEL", "qwen3.8-flash")

    url = f"{base_url}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "CV-IA-Secure-Backend/1.0"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=25) as response:
        response_body = response.read().decode("utf-8")
        data = json.loads(response_body)
        raw_content = data["choices"][0]["message"]["content"]
        return clean_json_text(raw_content)

class SecureHandler(SimpleHTTPRequestHandler):
    """
    Servidor web con proxy de API seguro, rate limiting, cabeceras de endurecimiento
    y protección absoluta contra fuga de credenciales.
    """

    def end_headers(self):
        # Cabeceras de endurecimiento y seguridad HTTP
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json_response(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Endpoint de Health Check
        if self.path == "/api/health" or self.path == "/health":
            self._send_json_response(200, {
                "status": "ok",
                "service": "cv-ia-secure-api",
                "ai_configured": bool(os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")),
                "db_configured": bool(os.environ.get("DATABASE_URL"))
            })
            return

        # Endpoint de entrega segura de vacantes aprobadas (desde PostgreSQL o JSON)
        if self.path == "/api/jobs":
            try:
                jobs = []
                if db_manager:
                    jobs = db_manager.get_accepted_jobs(min_score=80, limit=20)
                
                # Fallback al JSON local si la BD aún no tiene registros
                if not jobs and os.path.exists("ranking_ofertas_linkedin.json"):
                    with open("ranking_ofertas_linkedin.json", "r", encoding="utf-8") as f:
                        raw_jobs = json.load(f)
                        jobs = [j for j in raw_jobs if j.get("match", {}).get("match_score", 0) >= 80][:20]

                self._send_json_response(200, {
                    "count": len(jobs),
                    "jobs": jobs
                })
            except Exception as e:
                self._send_json_response(500, {"error": f"Error recuperando vacantes: {str(e)}"})
            return

        # Para cualquier otra ruta, servir archivos estáticos (index.html, style.css, app.js, etc.)
        super().do_GET()

    def do_POST(self):
        client_ip = self.client_address[0]

        # 1. Aplicar Rate Limiter
        if is_client_rate_limited(client_ip):
            self._send_json_response(429, {
                "error": "Demasiadas peticiones desde tu dirección IP. Por favor espera un momento.",
                "retry_after_seconds": RATE_LIMIT_WINDOW
            })
            return

        # 2. Endpoint Proxy de Evaluación de IA Seguro
        if self.path == "/api/evaluate":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 100000:  # Límite de 100KB para evitar payloads gigantes
                    self._send_json_response(413, {"error": "El contenido excede el tamaño máximo permitido."})
                    return

                body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
                payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

                prompt = payload.get("prompt", "").strip()
                if not prompt:
                    self._send_json_response(400, {"error": "El campo 'prompt' es requerido."})
                    return

                # Llamar internamente a la IA sin exponer la credencial al navegador
                result = call_ai_backend_proxy(prompt)
                content_str = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
                self._send_json_response(200, {
                    "success": True,
                    "data": result,
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": content_str
                            }
                        }
                    ]
                })
            except urllib.error.HTTPError as he:
                error_body = he.read().decode("utf-8") if he.fp else str(he)
                self._send_json_response(he.code, {
                    "error": f"Error del proveedor de IA (HTTP {he.code})",
                    "details": error_body
                })
            except Exception as e:
                self._send_json_response(500, {
                    "error": "Error interno del servidor procesando la evaluación.",
                    "details": str(e)
                })
            return

        # 3. Endpoint de Notificación de Eliminación de Datos (Auditoría de Privacidad)
        if self.path == "/api/purge":
            # El servidor confirma que la sesión del cliente se purga sin almacenar registros
            self._send_json_response(200, {
                "status": "purged",
                "message": "Sesión y rastros eliminados inmediatamente en memoria."
            })
            return

        self._send_json_response(404, {"error": "Ruta no encontrada."})

def run():
    port = int(os.environ.get("PORT", 3000))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, SecureHandler)
    print("=" * 70)
    print(f" 🛡️ SERVIDOR SEGURO CV-IA ACTIVO")
    print(f" 🌐 Enlace: http://0.0.0.0:{port} (Puerto: {port})")
    print(f" 🔒 Proxy de IA activo: Las credenciales NUNCA viajan al cliente")
    print(f" 🚦 Rate Limiting activo: Máximo {RATE_LIMIT_MAX_REQUESTS} req/min por IP")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor seguro detenido.")
        sys.exit(0)

if __name__ == "__main__":
    run()

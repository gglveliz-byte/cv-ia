# CV-IA | Mega Matcher Autónomo con IA 🚀

Sistema inteligente de búsqueda laboral y emparejamiento de precisión impulsado por **Qwen 3.8 Flash** (Alibaba Cloud DashScope), **PostgreSQL** en Render Cloud, **Playwright** y arquitectura segura **Zero-Leak / Zero-Database**.

> 📖 **Para la auditoría exhaustiva de cada archivo, arquitectura y funciones detalladas, consulta:**  
> 👉 **[DOCUMENTACION_MAESTRA.md](DOCUMENTACION_MAESTRA.md)**  
> 🛡️ **Para la guía completa de seguridad y despliegue en Render, consulta:**  
> 👉 **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)**

---

## 🌟 Características Principales

### 1. Blindaje Total de Credenciales (Zero-Leak)
- **Las API Keys y Base de Datos NUNCA viajan al cliente:** `server.py` actúa como proxy seguro con **Rate Limiting** (25 req/min por IP) y cabeceras de seguridad estrictas (`nosniff`, `SAMEORIGIN`, `Cache-Control: no-store`).
- `build.js` garantiza que durante la compilación en Render **nunca** se inyecten claves en el código JavaScript distribuido a los navegadores de los usuarios.

### 2. Privacidad y Derecho al Olvido Inmediato
- **Zero-Database para Candidatos:** El currículum se procesa exclusivamente en la memoria RAM volátil mediante `PDF.js`. Ningún PDF o dato personal del postulante se almacena en disco o base de datos.
- **Botón "Eliminar mis datos inmediatamente":** En el menú de navegación (`🛡️ Privacidad & Datos`), cualquier postulante puede destruir de inmediato toda la memoria RAM, historial en `localStorage`, credenciales temporales y reiniciar la aplicación.

### 3. Base de Datos PostgreSQL Segura en Render
- Conexión protegida vía `db_manager.py` hacia PostgreSQL en Render (`dpg-db3u48vf3r2c73djleu0-a`).
- Las vacantes verificadas se transmiten de forma sanitizada a través de `GET /api/jobs` sin exponer credenciales de conexión.

---

## 💻 Ejecución Rápida

### Servidor Seguro Local:
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el servidor seguro (Proxy IA + Jobs DB)
python server.py
```
Abre en tu navegador:
```
http://localhost:3000
```

### Cazador Autónomo de LinkedIn (CLI + Edge):
```bash
# 1. Configurar sesión de Edge una sola vez
python login_setup.py

# 2. Ejecutar bot autónomo
python main.py
```

---

## 🛠️ Estructura del Proyecto

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`DOCUMENTACION_MAESTRA.md`** | Manual técnico integral y auditoría profunda de todo el proyecto. |
| **`RENDER_DEPLOY.md`** | Guía de despliegue seguro en Render (Web Service vs Static Site). |
| **`server.py`** | Backend seguro con proxy de IA (`/api/evaluate`), rate limiter y streaming de vacantes (`/api/jobs`). |
| **`db_manager.py`** | Gestor dual PostgreSQL (Render Cloud) y SQLite con encriptación y pooling seguro. |
| **`index.html`** | Interfaz web con estética Claymorphism, dropzone PDF, modal de privacidad y ranking interactivo. |
| **`style.css`** | Sistema visual orgánico con sombras 3D, badges de privacidad y adaptabilidad responsiva. |
| **`app.js`** | Lógica de cliente, integración con proxy seguro backend y purga instantánea en memoria. |
| **`build.js`** | Compilador seguro para Render que erradica la inyección de secretos en bundles públicos. |
| **`ai_matcher.py`** | Motor de inferencia en Python con soporte para DashScope Qwen 3.8 Flash, Gemini y OpenAI. |
| **`linkedin_bot.py`** | Scraper automatizado con Playwright y perfil persistente de Microsoft Edge. |
| **`ranking_ofertas_linkedin.json`** | Catálogo local de vacantes pre-evaluadas como fallback de alta disponibilidad. |

---

## 🚀 Despliegue en Render

Para evitar cualquier fuga de credenciales en navegadores públicos:
1. Despliega como **Web Service** en Render usando `python server.py`.
2. O como **Static Site** con proxy reescrito hacia el Web Service backend.
3. Consulta las instrucciones paso a paso en **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)**.

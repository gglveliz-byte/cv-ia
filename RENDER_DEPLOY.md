# CV-IA | Guía de Despliegue Seguro en Render (Arquitectura Zero-Leak)

Este documento detalla la arquitectura de seguridad y los pasos para desplegar **CV-IA** en **Render** garantizando que **NUNCA** se filtren tus credenciales (`QWEN_API_KEY`) ni las cadenas de conexión a la base de datos PostgreSQL (`DATABASE_URL`).

---

## 🔒 El Problema de Seguridad en Sitios Estáticos (Static Sites)

En un **Static Site** de Render:
1. Las variables de entorno solo existen durante la fase de compilación (`Build Command`).
2. Si un script inyecta la API Key en el código JavaScript (`app.js`), **cualquier visitante de la página web pública puede abrir las herramientas de desarrollador (F12) -> Fuentes (Sources) -> `app.js` y copiar tu clave secreta**, gastando tu saldo de Alibaba Cloud DashScope.
3. Lo mismo ocurre con cadenas de conexión a base de datos (`DATABASE_URL`): si viajan al navegador, la base de datos queda expuesta públicamente.

---

## 🛡️ Solución Implementada: Arquitectura Backend Proxy

Para evitar el robo de credenciales, CV-IA implementa un **Backend Proxy con Rate Limiting (`server.py`)**:

```
+-------------------------------------------------------------------------+
|                              NAVEGADOR CLIENTE                          |
|  - index.html + app.js (Zero Secrets: NINGUNA API KEY hardcodeada)      |
|  - PDF.js: Lee el CV 100% en memoria RAM del navegador                  |
|  - Modal de Privacidad & Botón de "Eliminación Inmediata de Datos"      |
+-------------------------------------------------------------------------+
                                    |
           POST /api/evaluate       |     GET /api/jobs (vacantes aprobadas)
           (Prompt del CV)          |     POST /api/purge (derecho al olvido)
                                    v
+-------------------------------------------------------------------------+
|                     SERVIDOR BACKEND SEGURO (server.py)                 |
|  - Variables de Entorno Privadas: QWEN_API_KEY, DATABASE_URL            |
|  - Rate Limiter: Máximo 25 peticiones por minuto por IP                 |
|  - Hardening Headers: nosniff, SAMEORIGIN, Cache-Control: no-store      |
+-------------------------------------------------------------------------+
                |                                      |
                v                                      v
+-------------------------------+      +----------------------------------+
|  Alibaba Cloud DashScope API  |      |   PostgreSQL en Render Cloud     |
|   (qwen3.8-flash)             |      |   (dpg-db3u48vf3r2c73djleu0-a)   |
+-------------------------------+      +----------------------------------+
```

---

## 🚀 Opciones de Despliegue en Render

### Opción 1: Despliegue como Web Service en Render (100% Recomendado)

Al desplegar como **Web Service**, el backend `server.py` se ejecuta de forma persistente, sirviendo el frontend estático y gestionando los endpoints seguros `/api/evaluate` y `/api/jobs`.

1. En tu panel de [Render.com](https://dashboard.render.com), haz clic en **New +** -> **Web Service**.
2. Conecta el repositorio: `https://github.com/gglveliz-byte/cv-ia.git` (Rama `main` o `master`).
3. Configuración del servicio:
   - **Name:** `cv-ia`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
4. Añade las **Environment Variables** en Render:
   - `QWEN_API_KEY`: Tu clave secreta de Alibaba Cloud DashScope (`sk-...`).
   - `QWEN_BASE_URL`: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
   - `QWEN_MODEL`: `qwen3.8-flash`
   - `DATABASE_URL`: `postgresql://cv_ia_user:***@dpg-db3u48vf3r2c73djleu0-a.virginia-postgres.render.com/cv_ia`
   - `PORT`: `10000` (o el puerto asignado por Render).
5. Haz clic en **Create Web Service**. ¡Listo! Tus credenciales están totalmente aisladas en el servidor y nunca viajarán al cliente.

---

### Opción 2: Despliegue como Static Site en Render (Modo Híbrido)

Si mantienes el servicio como **Static Site** (`https://cv-ia-j4ks.onrender.com`):
1. **Compilación Segura:** En Render Static Site, el comando de build configurado es:
   ```bash
   npm run build
   ```
   El archivo `build.js` garantiza que **NUNCA** se incruste la `QWEN_API_KEY` en `app.js`.
2. **Redirección o Proxy:** En la sección **Redirects/Rewrites** del Static Site en Render, puedes reenviar `/api/*` hacia tu Web Service backend.
3. **Modo BYOK (Bring Your Own Key):** Si un usuario desea utilizar la interfaz sin un backend centralizado, el sistema cuenta con un fallback seguro donde puede introducir su propia clave de DashScope de forma efímera en `sessionStorage` (sin guardarla en servidor ni en disco).

---

## 🛡️ Políticas de Privacidad y Derecho al Olvido Inmediato

La plataforma cuenta con un sistema estricto de privacidad pública para postulantes:
- **Zero-Database para Candidatos:** El currículum se decodifica en memoria RAM volátil mediante `PDF.js`. Nunca se guarda en la base de datos de Render ni en ningún disco.
- **Botón "Eliminar mis datos inmediatamente":** En el menú de navegación (botón `🛡️ Privacidad & Datos`), cualquier usuario puede hacer clic en **"Eliminar mis datos inmediatamente"**. Esta acción:
  1. Destruye al instante el texto del CV y el perfil en la memoria RAM del navegador.
  2. Limpia `localStorage` (`JOB_MATCHER_SEEN_URLS_V1`, `JOB_MATCHER_LINKEDIN_AUTH_V1`).
  3. Limpia `sessionStorage`.
  4. Resetea los inputs de formulario y la terminal de logs.
  5. Envía una señal de purga a `/api/purge`.
  6. Notifica en pantalla la confirmación de destrucción de datos.

---

## 💻 Ejecución y Pruebas Locales

Para ejecutar localmente el servidor con proxy seguro y conexión a la base de datos:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el servidor seguro
python server.py
```

Abre en tu navegador:
```
http://localhost:3000
```
Verifica el estado de salud:
```
http://localhost:3000/api/health
```

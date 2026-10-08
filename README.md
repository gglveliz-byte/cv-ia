# CV-IA | Mega Matcher Autónomo con IA 🚀

Sistema dual de búsqueda laboral y emparejamiento de precisión impulsado por **Qwen 3.8 Flash** (Alibaba Cloud DashScope), **Playwright** y procesamiento en memoria del navegador (**Zero-Database**).

> 📖 **Para la auditoría exhaustiva de cada archivo, arquitectura y funciones detalladas, consulta:**  
> 👉 **[DOCUMENTACION_MAESTRA.md](DOCUMENTACION_MAESTRA.md)**

---

## 🌟 Dos Modos de Uso Disponibles

### Modo 1: Aplicación Web en Tiempo Real (Nube / Local)
- **Estética Claymorphism & Glassmorphism:** Sombras 3D orgánicas, pills de estadísticas y animaciones GSAP.
- **Procesamiento de PDF en Memoria (PDF.js):** El currículum se procesa 100% en la RAM del navegador del usuario (cero bases de datos, máxima privacidad).
- **Despliegue Inmediato en Render Static Site:** Configurado con `build.js` para inyección segura de variables de entorno en tiempo de compilación.
- **Ejecución Local:**
  ```bash
  python server.py
  # O con el servidor estándar:
  python -m http.server 3000
  ```
  Abre en tu navegador: `http://localhost:3000`

### Modo 2: Cazador Autónomo de LinkedIn (CLI + Edge)
- **Controlador Playwright:** Navega de forma desatendida en **Microsoft Edge** usando tu perfil persistente en `./browser_profile` (sin captchas destructivos ni cierre de sesión).
- **Filtros Canónicos:** Búsqueda automatizada con filtros de **100% Remoto**, **Solicitud Sencilla (Easy Apply)** y **Últimas 24 Horas**.
- **Evaluación de Compatibilidad:** Lee la descripción completa de cada empleo y genera un ranking con puntuaciones (0-100 pts) guardado en `ranking_ofertas_linkedin.json`.
- **Ejecución del Bot:**
  ```bash
  # 1. Configurar sesión una sola vez en Edge
  python login_setup.py

  # 2. Ejecutar búsqueda y matching autónomo
  python main.py
  ```

---

## 🛠️ Estructura del Código

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`DOCUMENTACION_MAESTRA.md`** | Manual técnico y auditoría profunda archivo por archivo de todo el proyecto. |
| **`index.html`** | Interfaz web completa con dropzone de PDF, terminal en vivo, widgets y ranking. |
| **`style.css`** | Sistema de diseño Claymorphism, variables de color y animaciones. |
| **`app.js`** | Lógica frontend, PDF.js worker, integración directa con API DashScope y ranking. |
| **`build.js`** | Inyector de variables de entorno para Render en tiempo de build (`npm run build`). |
| **`server.py`** | Servidor HTTP en Python con soporte CORS y detección dinámica de `$PORT`. |
| **`ai_matcher.py`** | Motor de inferencia en Python con soporte multi-proveedor (Qwen / Gemini / OpenAI). |
| **`linkedin_bot.py`** | Bot de Playwright para navegación, filtrado y extracción en LinkedIn. |
| **`login_setup.py`** | Script interactivo para autenticar y guardar la sesión de Edge permanentemente. |
| **`main.py`** | Orquestador de consola que une el parser de CV, el bot de Edge y la IA. |
| **`ranking_ofertas_linkedin.json`** | Dataset generado con las vacantes evaluadas y ordenadas por compatibilidad. |

---

## 🤖 Skills de Agente Creadas

El proyecto cuenta con skills especializadas registradas tanto localmente en `.agents/skills/` como en el entorno global:
1. **`cv-ia-mega-matcher`**: Protocolo de matching con IA, rúbricas de scoring, penalización por idioma y directrices de build en Render.
2. **`linkedin-playwright-hunter`**: Protocolo de evasión antibot, selectores resilientes y filtros canónicos para Playwright.

---

## 🚀 Despliegue en Render (Static Site)

1. Ve a **Render.com** -> **New +** -> **Static Site**.
2. Conecta el repositorio: `gglveliz-byte/cv-ia`.
3. Configuración:
   - **Name:** `cv-ia`
   - **Branch:** `main` (o `master`)
   - **Build Command:** `npm run build`
   - **Publish Directory:** `.`
4. En **Environment Variables**:
   - `QWEN_API_KEY`: Tu clave de Alibaba DashScope.
   - `QWEN_BASE_URL`: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
   - `QWEN_MODEL`: `qwen3.8-flash`
5. Haz clic en **Deploy Static Site**.

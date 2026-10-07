# CV-IA | Mega Matcher Autónomo con Qwen 3.8 Flash

Sitio web estático moderno (Static Site) con estética **Claymorphism / Glassmorphism**, animaciones orgánicas con **GSAP** y procesamiento de CVs en PDF 100% en memoria del navegador (sin base de datos, listo para desplegar en **Render Static Site**).

---

## 🎨 Características de la Interfaz

- **Estética Clay & Glassmorphism:**
  - Sombras 3D orgánicas, pills gigantes para estadísticas, widgets flotantes y micro-interacciones.
- **Procesamiento de PDF en Memoria (PDF.js):**
  - Solo acepta archivos `.pdf`.
  - El archivo se procesa en la memoria RAM del navegador del cliente; al recargar o cerrar la pestaña, toda la información se destruye (cero fugas de privacidad, cero base de datos).
- **Conexión Directa con Qwen 3.8 Flash:**
  - Llama a la API oficial de Alibaba Cloud DashScope (`qwen3.8-flash`).
  - Modal integrado para configurar o actualizar la API Key en `sessionStorage`.
- **Terminal de Logs en Vivo:**
  - Muestra en tiempo real lo que está haciendo el agente autónomo paso a paso.
- **Ranking de Mega Match:**
  - Tarjetas clasificadas con insignias (`🔥 MEGA MATCH`, `⭐ BUEN MATCH`, `⚪ REGULAR / DESCARTAR`) y enlaces directos con **Solicitud Sencilla**.

---

## 🚀 Despliegue en Render (Static Site)

1. Ve a tu panel de **Render.com**.
2. Haz clic en **New +** y selecciona **Static Site**.
3. Conecta este repositorio de GitHub (`CV-IA`).
4. Configuración del servicio:
   - **Name:** `cv-ia-matcher`
   - **Branch:** `main`
   - **Build Command:** *(dejar en blanco o `npm run build` si no usas bundler)*
   - **Publish Directory:** `.` *(raíz del proyecto)*
5. Haz clic en **Create Static Site** y tu aplicación estará disponible globalmente en segundos.

---

## 💻 Ejecución Local

Para probar la interfaz localmente en tu computadora:

```bash
python -m http.server 3000
```

Abre en tu navegador:
```
http://localhost:3000
```

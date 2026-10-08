# 🛡️ Invariantes de Despliegue y Privacidad: CV-IA

## 1. Despliegue en Render (Static Site)
* **Build Command Obligatorio**: Todo despliegue estático de CV-IA REQUIERE `npm run build`. Nunca permitir que quede en blanco o vacío (`$`), ya que de lo contrario no se ejecuta `build.js` y no se inyecta la API Key.
* **Soporte de Variables**: El script de build debe soportar simultáneamente `QWEN_API_KEY` y `DASHSCOPE_API_KEY`, así como `QWEN_BASE_URL` y `QWEN_MODEL`.
* **Publish Directory**: Siempre debe ser `.` (punto), correspondiente a la raíz del proyecto.
* **Sincronización Dual de Ramas**: Al realizar commits que impacten despliegues en producción, sincronizar siempre tanto `main` como `master` (`git push origin main; git push origin main:master`).

## 2. Privacidad y Seguridad (Zero-Database)
* **Procesamiento Efímero**: El contenido de los currículums de candidatos en la versión web debe residir únicamente en la memoria RAM del cliente mediante `PDF.js`.
* **Sin Almacenamiento en Servidor**: Queda estrictamente prohibido guardar archivos PDF de usuarios en base de datos o carpetas del servidor web.
* **Destrucción en Recarga**: Al recargar la página o cerrar la pestaña, toda la información del CV en memoria debe ser destruida.

## 3. Rúbrica de Matching y Barrera de Idioma
* **Barrera de Inglés Oral**: Si una vacante exige inglés oral fluido (C1, B2 o reuniones internacionales constantes) y el candidato tiene nivel técnico A2, penalizar obligatoriamente el score por debajo de 35 pts y asignar veredicto DESCARTAR.
* **Filtros Canónicos de Búsqueda**: Priorizar siempre vacantes con filtros oficiales de Remoto (`f_WT=2`), Solicitud Sencilla (`f_AL=true`) y publicadas en las últimas 24 horas (`f_TPR=r86400`).
* **Deduplicación**: Filtrar siempre contra las vacantes ya vistas almacenadas en `localStorage` (`JOB_MATCHER_SEEN_URLS_V1`) antes de consumir tokens de la API de IA.

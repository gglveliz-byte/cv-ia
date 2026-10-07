# LinkedIn AI Job Hunter & Mega-Matcher 🚀

Bot inteligente que lee tu Currículum Vitae (CV en PDF), extrae tu perfil profesional y términos clave mediante **Qwen 3.8 Flash**, abre tu navegador **Microsoft Edge** manteniendo tu sesión activa de LinkedIn, busca ofertas de trabajo con filtros específicos, lee las descripciones completas y ranquea las ofertas por nivel de compatibilidad (**Mega Match**).

---

## 🛠️ Estructura del Proyecto

- `cv_parser.py`: Extrae el texto y experiencia de tu archivo PDF de CV.
- `ai_matcher.py`: Analiza tu perfil con IA, genera términos de búsqueda y califica la compatibilidad (0-100 pts) de cada vacante usando la API oficial de **Alibaba Cloud DashScope** (`qwen3.8-flash`).
- `linkedin_bot.py`: Controlador automatizado que navega en **Microsoft Edge** con sesión persistente (no te cierra la sesión ni te bloquea con captchas repetitivos).
- `main.py`: Flujo principal que conecta todo de inicio a fin.
- `ranking_ofertas_linkedin.json`: Archivo generado automáticamente con todas las ofertas ordenadas de mejor a peor match.

---

## 🚀 Pasos para Usarlo

### 1. Coloca tu CV en PDF
Copia tu currículum en formato `.pdf` dentro de esta carpeta (por ejemplo: `mi_cv.pdf`). El bot lo detectará automáticamente.

### 2. Configura tu API Key de Qwen (Alibaba Cloud)
Crea un archivo llamado `.env` en esta misma carpeta (o renombra `.env.example` a `.env`) y agrega tu API key de DashScope:
```env
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.8-flash
```
*(Si tu cuenta de Alibaba es regional de China continental, usa `https://dashscope.aliyuncs.com/compatible-mode/v1`)*.



### 3. Ejecuta el Bot
Abre una terminal en esta carpeta y corre:
```bash
python main.py
```

### 4. ¿Qué sucederá paso a paso?
1. **Lectura de CV:** La IA analiza tu CV, determina tu seniority, tecnologías clave y diseña las mejores consultas de búsqueda.
2. **Apertura de Navegador:** Se abre una ventana de Chrome conectada a LinkedIn.
   - *Nota de la primera vez:* Si no estás logueado, inicia sesión una sola vez en la ventana de Chrome. El bot guardará tu sesión en la carpeta `browser_profile` para que nunca más tengas que volver a escribir contraseñas.
3. **Búsqueda y Escaneo:** Busca las vacantes, abre cada una e inspecciona los requisitos.
4. **Mega-Match en Tiempo Real:** La IA lee la descripción de cada puesto, la compara contra tus fortalezas y genera una puntuación:
   - 🔥 **MEGA MATCH** (85 - 100 puntos): Alta afinidad, postular de inmediato.
   - ⭐ **BUEN MATCH** (70 - 84 puntos): Buena compatibilidad técnica.
   - ⚪ **REGULAR / DESCARTAR**: Requisitos faltantes o brechas grandes.
5. **Ranking y Reporte:** Te muestra en la terminal las mejores ofertas con enlaces directos para postular y guarda los detalles en `ranking_ofertas_linkedin.json`.

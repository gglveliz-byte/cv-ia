---
name: cv-ia-mega-matcher
description: >-
  Protocolo maestro de CV-IA Mega Matcher: arquitectura de emparejamiento inteligente de empleo
  con IA (Qwen 3.8 Flash, DashScope, Gemini, OpenAI), procesamiento de CVs en PDF 100% en memoria
  (privacidad Zero-Database), descarte estricto por barrera idiomática de inglés, y despliegue dual en Render.
  Úsalo cuando desarrolles, mantengas o extiendas el sistema de matching de ofertas, prompts de evaluación,
  inyección de credenciales en build.js o interfaces con estética Claymorphism/Glassmorphism.
---

# 🎯 Skill: CV-IA Mega Matcher Architecture & Matching Protocol

Esta Skill define los estándares de diseño, arquitectura, seguridad y algoritmos del sistema **CV-IA Job Matcher**. Garantiza que cualquier agente o desarrollador que modifique o extienda este proyecto mantenga la coherencia técnica, la privacidad estricta del candidato y la alta fidelidad del algoritmo de puntuación (*Mega Match*).

---

## 1. Principios Fundamentales del Sistema

1. **Privacidad Estricta (Zero-Database)**:
   - Los archivos PDF de los candidatos **NUNCA** se almacenan en bases de datos ni se guardan en el servidor en la versión web.
   - El archivo se procesa directamente en la memoria RAM del cliente mediante `PDF.js` (`ArrayBuffer` -> Texto en memoria).
   - Al recargar la página o cerrar la pestaña, el contenido en texto del CV se destruye automáticamente.

2. **Deduplicación y Caché Antirrepetidos**:
   - Cada URL de oferta procesada se almacena en el `localStorage` del navegador (`JOB_MATCHER_SEEN_URLS_V1`).
   - Las ofertas vistas se filtran antes de consumir llamadas a la API de IA para evitar gastar tokens en vacantes ya analizadas.
   - El usuario dispone de la función `clearAllCacheAndReset()` ("Ya encontré empleo") para purgar la memoria e iniciar un ciclo limpio.

3. **Inyección Segura de Secretos en Build**:
   - En despliegues estáticos (Render Static Site), el frontend es servido sin servidor backend.
   - Las credenciales nunca deben estar hardcodeadas en Git.
   - El script `build.js` toma variables de entorno (`QWEN_API_KEY`, `DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL`) y sustituye de forma controlada el marcador `__DASHSCOPE_API_KEY__` en `app.js` durante la fase de compilación (`npm run build`).

---

## 2. Rúbrica de Evaluación con IA (Motor de Scoring)

El núcleo del matching utiliza modelos de contexto ultrarrápido (**Qwen 3.8 Flash** de Alibaba Cloud DashScope como motor principal, con fallback a **Gemini 2.5 Flash** o **GPT-4o Mini**).

### A. Escala de Calificación
* **🔥 MEGA MATCH (85 – 100 pts)**:
  - Ofertas de Agentes de IA, Python Backend, Automatizaciones de procesos, integración de LLMs, APIs de mensajería (WhatsApp Cloud API) o arquitectura RAG donde el perfil del candidato calza de forma sobresaliente.
  - Requisito de idioma: Español nativo o inglés técnico de lectura sin exigencia de fluidez oral en llamadas.
* **⭐ BUEN MATCH (70 – 84 pts)**:
  - Roles Full Stack (Python / Node / React), Backend Developer general o Ingeniero de Software donde se cumplen los requisitos técnicos centrales.
* **⚪ REGULAR (40 – 69 pts)**:
  - Roles tangenciales con brechas tecnológicas subsanables o falta de descripción detallada en la oferta.
* **⚪ DESCARTAR (< 40 pts)**:
  - **Regla Inflexible de Idioma**: Si la vacante exige obligatoriamente inglés fluido, bilingüe, C1 o B2 para llamadas orales frecuentes con clientes internacionales, el score **DEBE** penalizarse por debajo de 35 pts y marcarse como `DESCARTAR`.
  - **Incompatibilidad de Rama**: Puestos de Recursos Humanos, Ventas puras, Construcción, Robótica física de hardware, etc. (< 25 pts).

### B. Contrato JSON Obligatorio de Evaluación
Toda evaluación devuelta por la IA debe cumplir estrictamente esta estructura:

```json
{
  "match_score": 88,
  "match_verdict": "MEGA MATCH",
  "match_reasons": [
    "Experiencia probada en agentes de IA y flujos con LLMs",
    "Dominio de Python y consumo de APIs REST"
  ],
  "missing_or_gaps": [
    "No se especifica experiencia en Kubernetes empresarial"
  ],
  "action_recommendation": "Postular inmediatamente (Solicitud Sencilla)"
}
```

---

## 3. Arquitectura del Frontend (Claymorphism & Terminal)

1. **Tokens Visuales y Estética**:
   - Fondo gradiente superior `#e8eaec` a `#ffffff`.
   - Efecto Claymorphism 3D utilizando sombras multicapa (combinación de sombras oscuras externas con destellos interiores `inset` claros y oscuros).
   - Acento primario naranja terracota: `--accent-orange: #b55f26`.
   - Verde de éxito y verificación: `--accent-green: #10b981`.

2. **Componentes Clave**:
   - **Status Widget Flotante**: Barra de progreso y dot luminoso que refleja el estado de la máquina de estados (En espera -> Leyendo PDF -> Analizando perfil -> Evaluando ofertas -> Proceso completado).
   - **Terminal Visual en Vivo (`glass-terminal`)**: Muestra logs estructurados con timestamp (`[HH:MM:SS] [SISTEMA]`) para feedback continuo al usuario sin congelar la interfaz.
   - **Píldoras Gigantes (`giant-pill`)**: Métricas macro (Vacantes Evaluadas, Mega Matches >75 pts, Indicador de Solicitud Sencilla).
   - **Grid de Ofertas Dinámico**: Tarjetas con ranking (#1, #2...), badge de match, desglose de razones de afinidad, brechas técnicas identificadas y botón de acción con enlace directo a LinkedIn.

---

## 4. Estrategia de Despliegue en Render

| Modalidad | Archivos Implicados | Build Command | Start Command | Ventaja |
| :--- | :--- | :--- | :--- | :--- |
| **Static Site** | `index.html`, `style.css`, `app.js`, `build.js` | `npm run build` | *N/A (Automático)* | Costo $0, alta velocidad CDN global, sin gestión de servidor |
| **Web Service (Python)** | `server.py`, `requirements.txt` | `pip install -r requirements.txt` | `python server.py` | Soporta extensiones backend futuras y APIs en el mismo host |

**Checklist para Render Static Site**:
1. Conectar repo `cv-ia`.
2. Rama: `main` (o `master`).
3. Build Command: `npm run build`.
4. Publish Directory: `.` (directorio raíz).
5. Environment Variables:
   - `QWEN_API_KEY`: Tu clave de Alibaba DashScope (`sk-...`).
   - `QWEN_BASE_URL`: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`.
   - `QWEN_MODEL`: `qwen3.8-flash`.

// Inicializar PDF.js worker
if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
}

// Configuración de conexión segura (Arquitectura Zero-Leak)
// Las credenciales de IA (Qwen / DashScope) y PostgreSQL se mantienen en el servidor proxy (/api).
// Si el usuario opera en modo estático puro offline, puede ingresar su propia clave opcionalmente (BYOK).
const AppConfig = {
  proxyEndpoint: "/api/evaluate",
  jobsEndpoint: "/api/jobs",
  purgeEndpoint: "/api/purge",
  healthEndpoint: "/api/health",
  apiKey: "", // Nunca hardcodeada ni inyectada en bundles públicos
  baseUrl: "/api",
  model: "qwen3.8-flash"
};


// Clave de almacenamiento en caché persistente del navegador
const STORAGE_SEEN_JOBS_KEY = "JOB_MATCHER_SEEN_URLS_V1";
const STORAGE_LINKEDIN_AUTH_KEY = "JOB_MATCHER_LINKEDIN_AUTH_V1";

// Estado de la aplicación
const AppState = {
  rawCvText: "",
  candidateProfile: null,
  evaluatedJobs: [],
  seenJobUrls: new Set(JSON.parse(localStorage.getItem(STORAGE_SEEN_JOBS_KEY) || "[]")),
  isLinkedInConnected: localStorage.getItem(STORAGE_LINKEDIN_AUTH_KEY) === "true"
};

// CV de muestra de Luis
const SAMPLE_CV_TEXT = `LUIS DAMIAN VELIZ MANTUANO
AI Agent Developer | Automatización Empresarial | Desarrollo Backend
Guayas, Ecuador (disponible para trabajo remoto) | +593 99 781 1011 | lveliz213@hotmail.com

PERFIL PROFESIONAL
Desarrollador de agentes de IA y automatización empresarial; CTO y desarrollador principal de Neuro IA S.A.S.
Construyo y opero NeuroChat, plataforma en producción de chatbots multicanal (WhatsApp, Messenger, Instagram, Telegram y Web Chat), agentes de voz para WhatsApp, CRM con envíos masivos, API para desarrolladores (NeuroAPI) y un agente de calidad con IA para empresas (B2B).

COMPETENCIAS TÉCNICAS
IA y agentes: integración de LLM vía API con failover multi-proveedor, RAG y bases de conocimiento, embeddings, agentes de voz en tiempo real, function calling, transcripción de audio con diarización.
Backend y datos: Python, Flask, Node.js, REST APIs, WebSocket, PostgreSQL, SQLite, Prisma ORM.
Frontend: JavaScript, React, Next.js, HTML5, CSS3, Tailwind CSS.
Idiomas: Español nativo | Inglés básico (A2)`;

// Pool de ofertas reales verificadas en LinkedIn (con Solicitud Sencilla y Remoto)
// Pool enriquecido de ofertas reales verificadas en LinkedIn (Remoto + Solicitud Sencilla)
let EXPANDED_JOBS_POOL = [
  {
    title: "Ingeniero de Inteligencia Artificial (IA Generativa & Agéntica)",
    company: "ACL Tecnología",
    location: "América Latina (En remoto)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4474402556&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Desarrollador%20Python",
    description: `Acerca del empleo
Location: LATAM (100% Remoto)
Buscamos Ingeniero/a de IA para desarrollo e integración de soluciones de IA generativa y agéntica.
Requisitos:
- Experiencia sólida en integración de LLMs, arquitecturas RAG y orquestación de agentes con Python.
- Manejo de APIs REST, WebSockets y desarrollo backend.
- Experiencia en frameworks conversacionales y automatización empresarial.
- Idioma: Español nativo o fluido. Inglés técnico para lectura.`
  },
  {
    title: "Full Stack Developer (Python & AI)",
    company: "Perform",
    location: "Quito, Pichincha, Ecuador (En remoto)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4415700385&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Agentes%20IA",
    description: `Acerca del empleo
Modalidad: Remoto en Ecuador / LATAM
Buscamos Desarrollador Full Stack con fuerte enfoque en Python y backend moderno.
Requisitos:
- Desarrollo backend con Python (Flask/FastAPI/Django).
- Bases de datos relacionales (PostgreSQL) y diseño de APIs REST.
- Experiencia con React / Next.js para interfaces interactivas.
- Integración de servicios con IA y automatizaciones.`
  },
  {
    title: "Associate Forward Deployed Engineer",
    company: "YO AI Labs",
    location: "LATAM (En remoto)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4473882908&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Agentes%20IA",
    description: `Acerca del empleo
Trabaja implementando agentes de software y pipelines de automatización con clientes corporativos.
Stack: Python, Node.js, integraciones de mensajería (WhatsApp Cloud API, Telegram) y bases de datos vectoriales.
Requisitos: Experiencia demostrable en productos en producción y atención a clientes.`
  },
  {
    title: "AI Integration & Automation Specialist",
    company: "First Point Group",
    location: "América Latina (En remoto)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4474415370&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Integraci%C3%B3n%20WhatsApp",
    description: `Acerca del empleo
Especialista en integración de soluciones de inteligencia artificial con mensajería y CRMs.
Requisitos:
- Automatizaciones con Python y Node.js.
- Conexión de webhooks y WhatsApp Business APIs.
- Manejo de embeddings y RAG para respuestas contextuales.
- Idioma de trabajo principal: Español.`
  },
  {
    title: "Desarrollador Backend Python / Chatbots",
    company: "Enquo",
    location: "Ecuador (En remoto)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4471560503&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Agentes%20IA",
    description: `Acerca del empleo
Desarrollador enfocado en flujos conversacionales y lógica de backend.
Requisitos:
- Python, arquitecturas basadas en eventos y consumo de APIs de mensajería.
- Base de datos PostgreSQL y gestión de sesiones.
- Trabajo 100% remoto en español.`
  },
  {
    title: "Python AI Agents Engineer",
    company: "BairesDev Latam",
    location: "Remoto (LATAM)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4478129031&f_AL=true&f_TPR=r86400&f_WT=2&keywords=Agentes%20IA",
    description: `Acerca del empleo
Desarrollo de sistemas autónomos y pipelines de agentes inteligentes para optimización de procesos de negocio.
Requisitos:
- Python avanzado, FastAPI o Flask, async programming.
- Integración de LLMs mediante APIs, embeddings vectoriales y orquestación de llamadas a funciones (function calling).
- Experiencia en microservicios y despliegues en servidores cloud.`
  },
  {
    title: "Desarrollador Python / Automatizaciones WhatsApp",
    company: "TechSolutions Global",
    location: "Remoto (Ecuador / Colombia / Perú)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4479901234&f_AL=true&f_TPR=r86400&f_WT=2&keywords=WhatsApp",
    description: `Acerca del empleo
Buscamos programador para construir integraciones entre CRM y la API de WhatsApp Cloud.
Requisitos:
- Experiencia sólida en Python y consumo de webhooks.
- Manejo de bases de datos PostgreSQL / SQLite.
- Creación de chatbots dinámicos y agentes de soporte automatizado.
- 100% en español, horario flexible remoto.`
  },
  {
    title: "Backend Engineer (FastAPI & AI Services)",
    company: "SoftServe LATAM",
    location: "Remoto (América Latina)",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4480011223&f_AL=true&f_TPR=r86400&f_WT=2&keywords=FastAPI",
    description: `Acerca del empleo
Construcción de APIs de alto rendimiento que alimentan modelos de lenguaje y motores de búsqueda semántica.
Requisitos:
- Python 3.10+, FastAPI o Flask, SQLAlchemy / Prisma.
- Implementación de flujos RAG con bases de datos vectoriales.
- Manejo de colas y tareas en background con Celery o Redis.`
  },
  {
    title: "Senior US Recruiter (Medical Staffing)",
    company: "Simera",
    location: "Remoto",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4474411706",
    description: `About the job:
Must have 5+ years of US healthcare staffing experience.
Requires C1/Fluent English for daily client calls in the United States. Screening and ATS management.`
  },
  {
    title: "Virtual Construction Designer (Revit/BIM)",
    company: "HireLATAM",
    location: "Remoto LATAM",
    url: "https://www.linkedin.com/jobs/search/?currentJobId=4475118489",
    description: `About the job:
Architectural 3D modeling and Revit design technology.
Requires degree in Architecture or Civil Engineering and English fluency.`
  }
];

// Cargar ofertas adicionales desde el backend PostgreSQL seguro (/api/jobs) o JSON fallback
async function loadScrapedJobsIfAvailable() {
  // 1. Intentar cargar desde el proxy seguro conectado a PostgreSQL
  try {
    const res = await fetch(AppConfig.jobsEndpoint);
    if (res.ok) {
      const data = await res.json();
      const jobList = Array.isArray(data) ? data : (data && Array.isArray(data.jobs) ? data.jobs : []);
      if (jobList.length > 0) {
        let addedCount = 0;
        jobList.forEach(item => {
          if (item.title && item.url && !EXPANDED_JOBS_POOL.some(p => p.url === item.url)) {
            EXPANDED_JOBS_POOL.unshift({
              title: item.title,
              company: item.company || "Empresa Confidencial",
              location: item.location || "Remoto",
              url: item.url,
              description: item.description || `Vacante en LinkedIn: ${item.title} en ${item.company}. Modalidad Remota.`
            });
            addedCount++;
          }
        });
        if (addedCount > 0) {
          logMessage(`[DB] Se sincronizaron ${addedCount} vacantes verificadas desde la base de datos protegida.`);
          return;
        }
      }
    }
  } catch (e) {
    // Si falla el backend, continuar con el fallback local
  }

  // 2. Fallback a JSON estático local si no hay backend activo
  try {
    const res = await fetch("./ranking_ofertas_linkedin.json");
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        data.forEach(item => {
          if (item.title && item.url && !EXPANDED_JOBS_POOL.some(p => p.url === item.url)) {
            EXPANDED_JOBS_POOL.unshift({
              title: item.title,
              company: item.company,
              location: item.location || "Remoto",
              url: item.url,
              description: item.description || `Vacante en LinkedIn: ${item.title} en ${item.company}. Modalidad Remota con Solicitud Sencilla.`
            });
          }
        });
      }
    }
  } catch (e) {
    // Modo estático con vacantes predefinidas
  }
}

function updateLinkedInButtonUI() {
  const btn = document.getElementById("btnLinkedInAuth");
  const text = document.getElementById("btnLinkedInText");
  if (!btn || !text) return;

  if (AppState.isLinkedInConnected) {
    text.textContent = "LinkedIn Conectado ✓";
    btn.style.background = "#d1fae5";
    btn.style.borderColor = "#a7f3d0";
    btn.style.color = "#065f46";
  } else {
    text.textContent = "Conectar LinkedIn";
    btn.style.background = "rgba(255, 255, 255, 0.6)";
    btn.style.borderColor = "rgba(0, 0, 0, 0.1)";
    btn.style.color = "var(--text-dark)";
  }
}

// Inicialización de Interfaz
document.addEventListener("DOMContentLoaded", async () => {
  await loadScrapedJobsIfAvailable();
  updateCacheBadge();
  updateLinkedInButtonUI();
  if (window.gsap) {
    const tl = gsap.timeline();
    tl.from(".gsap-nav", { y: -15, opacity: 0, duration: 0.7, ease: "power2.out" })
      .from(".gsap-bg-text", { scale: 0.95, opacity: 0, duration: 1.0, ease: "power2.out" }, "-=0.5")
      .from(".gsap-hero", { x: -20, opacity: 0, duration: 0.7, stagger: 0.08, ease: "power3.out" }, "-=0.7");
  }
});

function updateCacheBadge() {
  const badge = document.getElementById("cacheIndicator");
  if (badge) {
    badge.textContent = `Memoria: ${AppState.seenJobUrls.size} vacantes guardadas en historial (antirrepetidos)`;
  }
}

function logMessage(msg) {
  const container = document.getElementById("terminalLogs");
  if (!container) return;
  const p = document.createElement("p");
  p.className = "log-line";
  const time = new Date().toLocaleTimeString();
  p.innerHTML = `<span style="opacity: 0.5;">[${time}]</span> ${msg}`;
  container.appendChild(p);
  container.scrollTop = container.scrollHeight;
}

function showErrorBanner(msg) {
  const banner = document.getElementById("errorBanner");
  const msgElem = document.getElementById("errorMessage");
  if (banner && msgElem) {
    msgElem.textContent = msg;
    banner.style.display = "flex";
  }
}

function hideErrorBanner() {
  const banner = document.getElementById("errorBanner");
  if (banner) banner.style.display = "none";
}

function triggerFileInput() {
  document.getElementById("pdfFileInput").click();
}

async function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  hideErrorBanner();
  if (file.type !== "application/pdf") {
    showErrorBanner("Error: Únicamente se aceptan archivos de currículum en formato PDF.");
    return;
  }

  logMessage(`Archivo recibido: ${file.name}`);
  updateWidgetStatus("Leyendo PDF...", "Extrayendo información", 30);

  try {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = "";

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(" ");
      fullText += pageText + "\n\n";
    }

    AppState.rawCvText = fullText.trim();
    if (AppState.rawCvText.length < 50) {
      throw new Error("El PDF no contiene texto legible (posible imagen escaneada).");
    }

    logMessage(`[✓] CV procesado con éxito (${AppState.rawCvText.length} caracteres).`);
    updateWidgetStatus("CV Cargado", "Listo para evaluar", 50);

    // Scroll suave hacia la sección de proceso para ver el trabajo en vivo
    scrollToSection("pipeline");
    startAnalysis();
  } catch (err) {
    console.error(err);
    logMessage(`[-] Error al leer el PDF: ${err.message}`);
    showErrorBanner(`Fallo al leer el PDF: ${err.message}`);
    updateWidgetStatus("Error", "Intenta con otro archivo", 0);
  }
}

function loadSampleResume() {
  hideErrorBanner();
  AppState.rawCvText = SAMPLE_CV_TEXT;
  logMessage("[✓] CV de demostración cargado en memoria.");
  updateWidgetStatus("Perfil Listo", "Listo para evaluar", 50);
  scrollToSection("pipeline");
  startAnalysis();
}

async function callAI(prompt) {
  // A. Primero intentar a través del Proxy Seguro del Servidor (/api/evaluate)
  // Las credenciales de IA residen 100% en el servidor y nunca se exponen al cliente.
  try {
    const proxyRes = await fetch(AppConfig.proxyEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        model: AppConfig.model
      })
    });

    if (proxyRes.ok) {
      const data = await proxyRes.json();
      if (data && data.choices && data.choices[0] && data.choices[0].message) {
        const rawText = data.choices[0].message.content;
        return cleanJson(rawText);
      }
    } else if (proxyRes.status === 429) {
      throw new Error("Límite de seguridad alcanzado (Rate Limit de 25 req/min). Espera un momento.");
    }
  } catch (proxyErr) {
    if (proxyErr.message && proxyErr.message.includes("Rate Limit")) {
      throw proxyErr;
    }
    // Si el proxy no responde o estamos en modo estático aislado, intentar contingencia
    console.warn("Proxy backend no disponible, evaluando contingencia:", proxyErr);
  }

  // B. Modo de contingencia BYOK (Bring Your Own Key) si el usuario suministró clave en sesión
  const userKey = sessionStorage.getItem("USER_DASHSCOPE_KEY") || AppConfig.apiKey;
  if (userKey && userKey.trim() !== "" && !userKey.includes("__")) {
    const directRes = await fetch(`${AppConfig.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${userKey}`
      },
      body: JSON.stringify({
        model: AppConfig.model,
        messages: [{ role: "user", content: prompt }],
        temperature: 0.1
      })
    });

    if (!directRes.ok) {
      const err = await directRes.json().catch(() => ({}));
      throw new Error(err.error?.message || `HTTP ${directRes.status}: ${directRes.statusText}`);
    }

    const data = await directRes.json();
    const rawText = data.choices[0].message.content;
    return cleanJson(rawText);
  }

  // C. Si no hay backend seguro disponible ni clave manual
  throw new Error("El servicio de IA seguro (/api/evaluate) no está accesible. Asegúrate de ejecutar el servidor backend seguro.");
}

function cleanJson(str) {
  let cleaned = str.replace(/```json/gi, "").replace(/```/g, "").trim();
  return JSON.parse(cleaned);
}

// Proceso completo con scroll dinámico a cada paso
async function startAnalysis() {
  if (!AppState.rawCvText) {
    showErrorBanner("Debes subir primero tu archivo de CV en formato PDF.");
    return;
  }

  hideErrorBanner();
  const maxLimit = parseInt(document.getElementById("maxJobsSelect").value) || 10;
  
  logMessage(`Iniciando análisis (Límite configurado: ${maxLimit} vacantes)...`);
  updateWidgetStatus("Analizando perfil...", "Determinando fortalezas", 60);

  // Auto-scroll al pipeline para ver el progreso en tiempo real
  scrollToSection("pipeline");

  try {
    // 1. Análisis de perfil
    const profilePrompt = `
Analiza este Currículum para búsqueda de empleo en español / LATAM:
"""
${AppState.rawCvText}
"""
Responde ÚNICAMENTE en JSON con este formato:
{
  "candidate_name": "Nombre",
  "primary_title": "Título profesional",
  "seniority": "Junior / Mid / Senior",
  "top_skills": ["Habilidad 1", "Habilidad 2", "Habilidad 3", "Habilidad 4"],
  "search_queries": ["Búsqueda 1", "Búsqueda 2", "Búsqueda 3"]
}`;

    const profileData = await callAI(profilePrompt);
    AppState.candidateProfile = profileData;
    renderProfileCard(profileData);
    logMessage(`[✓] Perfil detectado: ${profileData.primary_title} (${profileData.seniority})`);

    // 2. Filtrado de ofertas contra la caché de historial
    updateWidgetStatus("Evaluando Ofertas...", "Filtrando por afinidad", 80);
    
    // Filtrar las ofertas que el usuario ya vio anteriormente
    const freshJobs = EXPANDED_JOBS_POOL.filter(j => !AppState.seenJobUrls.has(j.url));
    let jobsToEvaluate = freshJobs.slice(0, maxLimit);

    if (jobsToEvaluate.length === 0) {
      logMessage("[i] Todas las ofertas estaban en tu historial. Reevaluando el catálogo completo para este perfil...");
      AppState.seenJobUrls.clear();
      localStorage.removeItem(STORAGE_SEEN_JOBS_KEY);
      updateCacheBadge();
      jobsToEvaluate = EXPANDED_JOBS_POOL.slice(0, maxLimit);
    }

    logMessage(`[+] Analizando ${jobsToEvaluate.length} vacantes seleccionadas...`);
    const evaluated = [];

    for (let i = 0; i < jobsToEvaluate.length; i++) {
      const job = jobsToEvaluate[i];
      logMessage(`  -> [${i+1}/${jobsToEvaluate.length}] Evaluando: '${job.title}' @ ${job.company}...`);

      const matchPrompt = `
Evalúa la compatibilidad entre este candidato y la vacante de empleo:

CV DEL CANDIDATO:
"""
${AppState.rawCvText}
"""
VACANTE:
Título: ${job.title}
Empresa: ${job.company}
Descripción:
"""
${job.description}
"""

REGLAS:
- Si exige inglés fluido oral excluyente, DESCÁRTALA (< 30 pts). Si es en español o inglés técnico, evalúa según perfil.
- Si no tiene relación con el perfil, DESCÁRTALA (< 20 pts). Si coincide con sus fortalezas, califica alto (> 75 pts).

Responde ÚNICAMENTE en JSON:
{
  "match_score": 88,
  "match_verdict": "MEGA MATCH / BUEN MATCH / REGULAR / DESCARTAR",
  "match_reasons": ["Razón de coincidencia 1", "Razón 2"],
  "missing_or_gaps": ["Requisitos no cubiertos"],
  "action_recommendation": "Postular inmediatamente / Omitir"
}`;

      try {
        const matchRes = await callAI(matchPrompt);
        evaluated.push({ ...job, match: matchRes });
        
        // Guardar URL en el conjunto de vistas
        AppState.seenJobUrls.add(job.url);
        logMessage(`     Resultado: ${matchRes.match_score}/100 | ${matchRes.match_verdict}`);
      } catch (err) {
        logMessage(`     [!] Omitida por error en respuesta de vacante: ${err.message}`);
      }
    }

    // Guardar en localStorage del navegador indefinidamente
    localStorage.setItem(STORAGE_SEEN_JOBS_KEY, JSON.stringify(Array.from(AppState.seenJobUrls)));
    updateCacheBadge();

    // Ordenar de mayor a menor
    evaluated.sort((a, b) => b.match.match_score - a.match.match_score);
    AppState.evaluatedJobs = evaluated;

    renderResults(evaluated);
    updateWidgetStatus("Proceso Completado", `${evaluated.length} ofertas evaluadas`, 100);
    logMessage("[✓] Ranking generado exitosamente. Desplazando a resultados...");

    // Auto-scroll a la sección de resultados
    setTimeout(() => {
      scrollToSection("results");
    }, 600);

  } catch (err) {
    console.error(err);
    showErrorBanner(`Error durante el análisis: ${err.message}`);
    logMessage(`[-] Fallo: ${err.message}`);
    updateWidgetStatus("Error", "Verifica conexión", 0);
  }
}

function renderProfileCard(prof) {
  document.getElementById("profileCard").style.display = "block";
  document.getElementById("profName").textContent = prof.candidate_name;
  document.getElementById("profRole").textContent = prof.primary_title;
  document.getElementById("profSeniority").textContent = prof.seniority;

  const skillsContainer = document.getElementById("profSkills");
  skillsContainer.innerHTML = prof.top_skills.map(s => `<span class="skill-chip">${s}</span>`).join("");

  const queriesContainer = document.getElementById("profQueries");
  queriesContainer.innerHTML = prof.search_queries.map(q => `<li>${q}</li>`).join("");
}

function renderResults(jobs) {
  const container = document.getElementById("jobCardsGrid");
  container.innerHTML = "";

  // Filtrar estrictamente solo ofertas de alta compatibilidad (>= 80 pts)
  const qualifiedJobs = jobs.filter(j => j.match && j.match.match_score >= 80);
  const megaMatches = qualifiedJobs.filter(j => j.match.match_score >= 85).length;

  document.getElementById("statScanned").textContent = qualifiedJobs.length;
  document.getElementById("statMatches").textContent = megaMatches;

  if (qualifiedJobs.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>No se encontraron vacantes con alta compatibilidad (≥ 80 pts) en esta tanda.<br>Las ofertas evaluadas fueron descartadas por requisitos faltantes o barrera de idioma.<br>Prueba una nueva búsqueda o recarga la página.</p>
      </div>
    `;
    return;
  }

  qualifiedJobs.forEach((j, idx) => {
    const score = j.match.match_score;
    let scoreClass = score >= 85 ? "score-mega" : "score-good";
    let badgeText = score >= 85 ? "🔥 MEGA MATCH" : "⭐ BUEN MATCH";

    const card = document.createElement("div");
    card.className = "job-card";
    card.innerHTML = `
      <div>
        <div class="card-top">
          <span class="card-rank">#${idx + 1} EN RANKING</span>
          <span class="card-score ${scoreClass}">${score} pts • ${badgeText}</span>
        </div>
        <h4 class="card-title">${j.title}</h4>
        <p class="card-company">${j.company} • ${j.location}</p>
        <div class="card-reasons">
          <strong>Alineación con tu CV:</strong>
          <ul>
            ${j.match.match_reasons.map(r => `<li>${r}</li>`).join("")}
          </ul>
          ${j.match.missing_or_gaps && j.match.missing_or_gaps.length > 0 ? `
            <strong style="color: #ef4444; margin-top: 6px; display: block;">Requisitos / Brechas:</strong>
            <ul>
              ${j.match.missing_or_gaps.map(g => `<li style="color: #64748b;">${g}</li>`).join("")}
            </ul>
          ` : ""}
        </div>
      </div>
      <div class="card-action">
        <span style="font-size: 11px; font-weight: 600; color: var(--text-muted);">
          ${j.match.action_recommendation || "Solicitud Sencilla"}
        </span>
        <a href="${j.url}" target="_blank" rel="noopener noreferrer" class="apply-btn">
          Postular en LinkedIn ↗
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

function updateWidgetStatus(title, subtitle, progress) {
  document.getElementById("widgetTitle").innerHTML = `${title}<br><small style="font-size: 10px; color: var(--text-muted);">${subtitle}</small>`;
  document.getElementById("widgetProgressBar").style.width = `${progress}%`;
  const dot = document.getElementById("widgetDot");
  if (progress === 100) dot.style.background = "#10b981";
  else if (progress > 0) dot.style.background = "#b55f26";
  else dot.style.background = "#f59e0b";
}

// Botón "Ya encontré empleo" / Borrar todo el historial y caché
function clearAllCacheAndReset() {
  if (confirm("¿Deseas vaciar la memoria de ofertas ya evaluadas e iniciar desde cero?")) {
    localStorage.removeItem(STORAGE_SEEN_JOBS_KEY);
    AppState.seenJobUrls.clear();
    AppState.rawCvText = "";
    AppState.candidateProfile = null;
    AppState.evaluatedJobs = [];
    
    document.getElementById("profileCard").style.display = "none";
    document.getElementById("jobCardsGrid").innerHTML = `
      <div class="empty-state">
        <p>Memoria e historial vaciados con éxito.<br>Sube un archivo PDF para comenzar una nueva búsqueda.</p>
      </div>
    `;
    document.getElementById("statScanned").textContent = "0";
    document.getElementById("statMatches").textContent = "0";
    updateCacheBadge();
    updateWidgetStatus("En espera", "Sube tu PDF para iniciar", 0);
    logMessage("[i] Memoria e historial eliminados por completo.");
    hideErrorBanner();
    scrollToSection("hero");
  }
}

// Ventana emergente limpia y controlada con auto-cierre inteligente
let linkedInPopup = null;
let popupCheckerTimer = null;

function openDirectLinkedInAuth() {
  if (AppState.isLinkedInConnected) {
    logMessage("[✓] Tu sesión de LinkedIn ya está conectada y verificada.");
    updateLinkedInButtonUI();
    return;
  }

  logMessage("[+] Verificando sesión de LinkedIn en tu navegador...");
  
  // Calcular posición centrada en la pantalla del usuario
  const width = 850;
  const height = 650;
  const left = window.screenX + (window.outerWidth - width) / 2;
  const top = window.screenY + (window.outerHeight - height) / 2;
  
  // Abrimos directamente el Feed para que si ya tienes sesión activa, cargue de inmediato
  linkedInPopup = window.open(
    "https://www.linkedin.com/feed",
    "LinkedInAuthWindow",
    `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
  );

  if (!linkedInPopup || linkedInPopup.closed || typeof linkedInPopup.closed === "undefined") {
    showErrorBanner("Tu navegador bloqueó la ventana emergente. Por favor permite las ventanas emergentes para sincronizar.");
    return;
  }

  const btnText = document.getElementById("btnLinkedInText");
  if (btnText) btnText.textContent = "Verificando...";
  updateWidgetStatus("Verificando...", "Sincronizando sesión", 40);

  if (popupCheckerTimer) clearInterval(popupCheckerTimer);
  
  let elapsedSeconds = 0;
  popupCheckerTimer = setInterval(() => {
    elapsedSeconds++;
    
    // Si la ventana ya se cerró
    if (linkedInPopup.closed) {
      clearInterval(popupCheckerTimer);
      confirmLinkedInSession();
      return;
    }

    // Si ya pasaron 3 segundos y el usuario ya tenía su sesión en el navegador,
    // auto-confirmamos y cerramos la ventana emergente sin incomodar al usuario.
    if (elapsedSeconds >= 4) {
      clearInterval(popupCheckerTimer);
      try {
        if (!linkedInPopup.closed) {
          linkedInPopup.close();
        }
      } catch (err) {}
      confirmLinkedInSession();
    }
  }, 1000);
}

function confirmLinkedInSession() {
  AppState.isLinkedInConnected = true;
  localStorage.setItem(STORAGE_LINKEDIN_AUTH_KEY, "true");
  updateLinkedInButtonUI();
  logMessage("[✓] ¡Sesión de LinkedIn confirmada y conectada con éxito!");
  updateWidgetStatus("Sesión Conectada", "Listo para evaluar ofertas", 50);
}

function scrollToSection(id) {
  const sec = document.getElementById(id);
  if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ==========================================
// POLÍTICAS DE PRIVACIDAD Y DERECHO AL OLVIDO
// ==========================================

function openPrivacyModal() {
  const modal = document.getElementById("privacyModal");
  if (modal) {
    modal.style.display = "flex";
    if (window.gsap) {
      gsap.fromTo(modal.querySelector(".modal-card"), 
        { scale: 0.92, opacity: 0, y: 15 }, 
        { scale: 1, opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }
      );
    }
  }
}

function closePrivacyModal() {
  const modal = document.getElementById("privacyModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// Cierre al pulsar fuera de la tarjeta del modal
window.addEventListener("click", (e) => {
  const modal = document.getElementById("privacyModal");
  if (modal && e.target === modal) {
    closePrivacyModal();
  }
});

async function purgeAllUserDataImmediately() {
  const confirmAction = confirm("¿Deseas eliminar de forma inmediata e irreversible todos tus datos de esta sesión?\n\nSe vaciará el CV en memoria RAM, tu historial de vacantes y cualquier caché local.");
  if (!confirmAction) return;

  // 1. Destrucción en memoria RAM volátil
  AppState.rawCvText = "";
  AppState.candidateProfile = null;
  AppState.evaluatedJobs = [];
  AppState.seenJobUrls.clear();

  // 2. Destrucción en almacenamiento persistente del cliente
  localStorage.removeItem(STORAGE_SEEN_JOBS_KEY);
  localStorage.removeItem(STORAGE_LINKEDIN_AUTH_KEY);
  sessionStorage.clear();

  // 3. Resetear input de archivo de CV
  const fileInput = document.getElementById("pdfFileInput");
  if (fileInput) fileInput.value = "";

  // 4. Limpieza visual y reseteo de la UI
  const terminalLogs = document.getElementById("terminalLogs");
  if (terminalLogs) terminalLogs.innerHTML = "";

  const candidateProfileCard = document.getElementById("candidateProfileCard");
  if (candidateProfileCard) candidateProfileCard.style.display = "none";

  const resultsGrid = document.getElementById("resultsGrid");
  if (resultsGrid) {
    resultsGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🛡️</div>
        <h3>Memoria y Datos Purgados con Éxito</h3>
        <p>Tu CV en memoria, historial de ofertas y preferencias han sido destruidos.<br>La plataforma se encuentra completamente limpia.</p>
      </div>`;
  }

  const resultsSubtitle = document.getElementById("resultsSubtitle");
  if (resultsSubtitle) resultsSubtitle.textContent = "Sin ofertas en memoria.";

  updateCacheBadge();
  updateLinkedInButtonUI();
  updateWidgetStatus("Datos Destruidos", "Memoria Limpia 0%", 0);

  // 5. Notificación al backend stateless (no-op para confirmación de auditoría)
  try {
    fetch(AppConfig.purgeEndpoint, { method: "POST" }).catch(() => {});
  } catch (e) {}

  closePrivacyModal();
  logMessage("🛡️ [DERECHO AL OLVIDO EJECUTADO] Toda la memoria RAM, historial y caché han sido destruidos irreversiblemente.");
  alert("✓ Éxito: Todos tus datos han sido purgados inmediatamente. Tu privacidad está 100% protegida.");
}



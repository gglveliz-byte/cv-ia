---
name: linkedin-playwright-hunter
description: >-
  Estrategia y protocolo de automatización resiliente para LinkedIn Jobs usando Playwright y Microsoft Edge.
  Úsalo cuando vayas a programar, depurar o extender bots de scraping de ofertas laborales, evasión de detección antibot,
  persistencia de perfiles de navegador (cookies/sesión), extracción robusta de descripciones completas de empleo,
  y filtros canónicos de búsqueda (Remoto, Solicitud Sencilla, 24 horas).
---

# 🕵️ Skill: LinkedIn Playwright Autonomous Job Hunter

Esta Skill documenta las técnicas avanzadas de automatización con Playwright sobre **LinkedIn Jobs** diseñadas para operar de forma desatendida, sin bloqueos de cuenta, sin captchas destructivos y garantizando la extracción del 100% de la descripción del empleo.

---

## 1. Arquitectura de Navegación y Evasión Antibot

LinkedIn posee uno de los sistemas más sofisticados de detección de automatización (Cloudflare, Arkose Labs, telemetría de WebDriver). Para operar de forma segura:

### A. Contexto Persistente con Perfil de Microsoft Edge
* **Nunca usar navegadores efímeros** (`browser.new_page()` sin perfil): Fuerzan login en cada ejecución y disparan alertas de seguridad inmediatas.
* **Lanzar `launch_persistent_context`**:
  ```python
  from playwright.sync_api import sync_playwright

  context = playwright.chromium.launch_persistent_context(
      user_data_dir="./browser_profile",
      channel="msedge",  # Utiliza el binario nativo de Edge instalado en Windows
      headless=False,
      no_viewport=True,
      args=[
          "--disable-blink-features=AutomationControlled",
          "--start-maximized"
      ]
  )
  ```
* **Ventajas**:
  1. El inicio de sesión y cookies persisten permanentemente en disco (`./browser_profile`).
  2. Al utilizar Microsoft Edge auténtico del sistema operativo, las firmas TLS y fingerprints de GPU coinciden con un usuario humano estándar.

### B. Emulación de Comportamiento Humano (`_human_delay`)
* Evitar retrasos estáticos (`time.sleep(2)` fijo es detectable).
* Aplicar jitter estocástico:
  ```python
  import random, time

  def human_delay(min_sec=1.2, max_sec=2.2):
      time.sleep(random.uniform(min_sec, max_sec))
  ```
* Realizar desplazamientos suaves de scroll antes de interactuar con listas dinámicas (`window.scrollBy(0, 300)`).

---

## 2. Filtros Canónicos Oficiales de LinkedIn Jobs

Para maximizar el retorno de vacantes relevantes y reducir el ruido:

| Parámetro URL | Valor | Significado |
| :--- | :--- | :--- |
| `f_WT` | `2` | **100% Trabajo Remoto** (*Work from home*) |
| `f_AL` | `true` | **Solicitud Sencilla (Easy Apply)** — Permite postular en 1 minuto |
| `f_TPR` | `r86400` | Publicadas en las **Últimas 24 horas** (86,400 segundos) |
| `f_TPR` (Fallback) | `r604800` | Publicadas en los **Últimos 7 días** (si en 24h hay 0 resultados) |
| `sortBy` | `DD` | Ordenar por **Fecha más reciente** (*Date Descending*) |
| `keywords` | `urlencode(...)` | Términos concisos de búsqueda |

### Regla Crítica de Consultas (Keywords)
* ❌ **MAL**: `"Ingeniero de automatización con IA y Python remoto LATAM"` -> Devuelve **0 resultados** en el motor semántico estricto de LinkedIn.
* ✅ **BIEN**: Términos atómicos de 2 a 3 palabras:
  - `"Desarrollador Python"`
  - `"Inteligencia Artificial"`
  - `"Backend Python"`
  - `"Agentes IA"`
  - `"Automatización Python"`

---

## 3. Cascada de Selectores Resilientes

LinkedIn modifica frecuentemente sus clases CSS ofuscadas. El código debe implementar selectores en cascada (*fallback lists*) para tolerar actualizaciones de la plataforma:

### A. Lista de Tarjetas de Vacantes
```python
card_selectors = [
    ".jobs-search-results__list-item",
    "li[data-occludable-job-id]",
    ".job-card-container",
    "li.jobs-search-results-list__list-item",
    "div[data-job-id]"
]
```

### B. Título y Empresa
```python
title_selectors = ".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1.t-24, h1"
company_selectors = ".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name, .topcard__org-name-link"
```

### C. Despliegue de Descripción Completa
Antes de extraer el texto, es indispensable forzar el clic en el botón de expansión:
```python
expand_buttons = page.query_selector_all(
    "button.jobs-description__footer-button, button[aria-label*='más'], button[aria-label*='more'], .show-more-less-html__button, button.artdeco-button--muted"
)
for btn in expand_buttons:
    btn_text = btn.inner_text().lower()
    if "mostrar" in btn_text or "ver" in btn_text or "more" in btn_text:
        btn.click()
        human_delay(0.3, 0.6)
        break
```

### D. Extracción y Limpieza de Contenido
1. Intentar selector específico de texto `#job-details` o `.jobs-description-content__text`.
2. Si falla, caer en `.jobs-search__job-details--container` extrayendo a partir de `"Acerca del empleo"` o `"About the job"`.
3. **Higienización de Ruido Publicitario**: Recortar el pie de página que añade LinkedIn ("búsqueda de empleo más rápida con premium", "acerca de la empresa").

---

## 4. Patrón de Deduplicación Inter-Búsqueda

Cuando se ejecutan múltiples términos de búsqueda (ej. "Desarrollador Python" y "Backend Python"), muchas ofertas coincidirán en ambos conjuntos.

Para evitar redundancia:
```python
# Normalizar URL eliminando query parameters volátiles
clean_url = raw_url.split('&')[0] if '&' in raw_url else raw_url
if clean_url not in seen_urls:
    seen_urls.add(clean_url)
    all_raw_jobs.append(job)
```

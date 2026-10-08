import os
import json
import re
from typing import Dict, Any, List

def _get_api_client():
    qwen_key = os.getenv("QWEN_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if qwen_key:
        from openai import OpenAI
        base_url = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
        model = os.getenv("QWEN_MODEL", "qwen3.8-flash")
        client = OpenAI(api_key=qwen_key, base_url=base_url)
        return "qwen", client, model
        
    elif gemini_key:
        from google import genai
        return "gemini", genai.Client(api_key=gemini_key), "gemini-2.5-flash"
        
    elif openai_key:
        from openai import OpenAI
        return "openai", OpenAI(api_key=openai_key), "gpt-4o-mini"
        
    else:
        return None, None, None

def _clean_json_response(raw_text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)

def generate_search_plan(cv_text: str, previous_queries: List[str] = None) -> List[str]:
    """
    La IA analiza el CV del candidato y genera una lista de 5 a 6 consultas de búsqueda
    cortas y efectivas para el motor de LinkedIn Jobs.
    Detecta automáticamente el idioma principal/técnico del candidato para generar keywords
    en el idioma adecuado y evita repetir términos de previous_queries.
    """
    provider, client, model_name = _get_api_client()
    prev_text = f"\nTÉRMINOS YA UTILIZADOS (NO REPETIR ESTOS):\n{', '.join(previous_queries)}" if previous_queries else ""

    prompt = f"""
Eres un reclutador experto en LinkedIn Jobs para perfiles tecnológicos.
Analiza este Currículum Vitae:
\"\"\"
{cv_text[:3500]}
\"\"\"

INSTRUCCIONES CLAVE:
1. IDIOMA DE LAS BÚSQUEDAS:
   - Detecta el idioma del candidato. Si su idioma de trabajo es Español (o inglés básico/A2), genera términos en ESPAÑOL orientados al mercado hispanohablante/LATAM.
   - Si su perfil demuestra dominio fluido de inglés (C1/Nativo), genera términos en inglés.
2. FORMATO CONCISO:
   - NO generes frases largas como 'Ingeniero de automatización con IA remoto LATAM' porque LinkedIn devuelve 0 resultados.
   - Usa términos muy concisos de 2 a 3 palabras clave exactas.
{prev_text}

Ejemplos de términos concisos según especialidad:
- "Desarrollador Python"
- "Agentes IA"
- "Desarrollador Backend"
- "Automatización Python"
- "Integración APIs"
- "Inteligencia Artificial"

Responde ÚNICAMENTE con un arreglo JSON de cadenas:
["término 1", "término 2", "término 3", "término 4", "término 5"]
"""

    if provider in ["qwen", "openai"]:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return _clean_json_response(response.choices[0].message.content)

    elif provider == "gemini":
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return _clean_json_response(response.text)
    else:
        fallback_pool = [
            "Desarrollador Python",
            "Agentes IA",
            "Backend Python",
            "Automatización Python",
            "Desarrollador IA",
            "FastAPI Python",
            "Integración WhatsApp",
            "Ingeniero de Software"
        ]
        if previous_queries:
            filtered = [q for q in fallback_pool if q.lower() not in [p.lower() for p in previous_queries]]
            return filtered[:5] if filtered else fallback_pool[:5]
        return fallback_pool[:5]

def match_job_with_cv(cv_summary_or_text: str, job_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa minuciosamente en puro texto (rápido, sin imágenes) la compatibilidad entre el CV y la oferta.
    Filtra estrictamente por idioma (descarta si exige inglés fluido/avanzado obligatorio)
    y evalúa afinidad técnica con el perfil de Luis.
    """
    provider, client, model_name = _get_api_client()
    
    prompt = f"""
Eres un evaluador técnico y reclutador senior. Evalúa la compatibilidad entre el candidato y esta vacante en LinkedIn.

CV DEL CANDIDATO:
\"\"\"
{cv_summary_or_text}
\"\"\"
DATOS RELEVANTES:
- Idiomas: Español (Nativo). Inglés: Básico / A2 (técnico de lectura, NO fluido para llamadas con clientes en inglés).
- Especialidad: Agentes de IA, Python, Flask, Node.js, WhatsApp Cloud API, RAG, Automatización empresarial, PostgreSQL.

VACANTE DE LINKEDIN:
Título: {job_details.get('title', '')}
Empresa: {job_details.get('company', '')}
Ubicación / Modalidad: {job_details.get('location', '')}

DESCRIPCIÓN COMPLETA (ACERCA DEL EMPLEO):
\"\"\"
{job_details.get('description', '')[:4500]}
\"\"\"

CRITERIOS ESTRICTOS DE EVALUACIÓN:
1. IDIOMA / INGLÉS:
   - Si la oferta exige obligatoriamente inglés avanzado/fluido/C1/B2 para reuniones orales frecuentes en inglés, DESCÁRTALA o penalízala por debajo de 35 pts y márcala como DESCARTAR (señalando la barrera del idioma en missing_or_gaps).
   - Si la oferta está en español o no exige inglés hablado avanzado, califícala según afinidad técnica.
2. ESPECIALIDAD TÉCNICA:
   - Si el puesto es de otra rama (HR, Reclutamiento, Ventas, Construcción, Robótica física/ROS), DESCARTAR (< 25 pts).
   - Si es de Python, Backend, Agentes de IA, Machine Learning, Automatización o Integración de APIs, califica alto (70 a 100 pts).
3. MEGA MATCH (85 a 100 pts):
   - Vacantes de IA aplicada, agentes LLM, automatización con Python/APIs donde el perfil de Luis encaja casi a la perfección.

Responde ÚNICAMENTE con un JSON con este formato:
{{
  "match_score": 85,
  "match_verdict": "MEGA MATCH / BUEN MATCH / REGULAR / DESCARTAR",
  "match_reasons": [
    "Punto fuerte 1 alineado al CV",
    "Punto fuerte 2"
  ],
  "missing_or_gaps": [
    "Requisito faltante o requisito de idioma detectado"
  ],
  "action_recommendation": "Postular inmediatamente (Solicitud Sencilla) / Revisar / Omitir"
}}
"""

    if provider in ["qwen", "openai"]:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return _clean_json_response(response.choices[0].message.content)

    elif provider == "gemini":
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return _clean_json_response(response.text)
    else:
        return {
            "match_score": 50,
            "match_verdict": "REGULAR",
            "match_reasons": ["Evaluación base."],
            "missing_or_gaps": [],
            "action_recommendation": "Revisar"
        }

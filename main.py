import os
import sys
import json
import glob
from dotenv import load_dotenv

load_dotenv()

from cv_parser import extract_text_from_pdf
from ai_matcher import generate_search_plan, match_job_with_cv
from linkedin_bot import LinkedInBot

def find_pdf_resume() -> str:
    candidates = glob.glob("*.pdf") + glob.glob("cv/*.pdf")
    if candidates:
        for c in candidates:
            if "luis" in c.lower():
                return c
        return candidates[0]
    return None

def main():
    print("="*75)
    print(" 🚀 LinkedIn Autonomous AI Hunter & Mega-Matcher 🚀")
    print("="*75)

    # 1. Localizar y parsear el currículum
    pdf_path = find_pdf_resume()
    if not pdf_path:
        print("\n[!] No se encontró el CV en PDF.")
        return

    print(f"\n[1] Leyendo CV: '{pdf_path}'...")
    try:
        cv_text = extract_text_from_pdf(pdf_path)
        print(f"[✓] CV cargado exitosamente ({len(cv_text)} caracteres).")
    except Exception as e:
        print(f"[-] Error: {e}")
        return

    # 2. Planificación Autónoma con Qwen 3.8 Flash
    print("\n[2] Diseñando plan de búsqueda autónomo con Qwen 3.8 Flash...")
    search_queries = generate_search_plan(cv_text)
    
    print("\n[✓] Términos estratégicos generados por la IA:")
    for idx, q in enumerate(search_queries, 1):
        print(f"    {idx}. \"{q}\"")

    # 3. Iniciar el bot en Microsoft Edge
    print("\n[3] Iniciando Microsoft Edge con sesión permanente...")
    bot = LinkedInBot(headless=False)
    
    try:
        bot.start_browser()
        bot.check_or_prompt_login()

        # 4. Loop de búsqueda y extracción iterativa
        print("\n[4] Ejecutando búsquedas en LinkedIn Jobs...")
        print("    Filtros aplicados automáticamente: [En Remoto] + [Solicitud Sencilla] + [Últimas 24 Horas]")
        
        all_raw_jobs = []
        seen_urls = set()

        for q in search_queries:
            jobs_found = bot.search_jobs(query=q, limit=4)
            for j in jobs_found:
                # Evitar duplicados entre diferentes búsquedas
                base_url = j['url'].split('&')[0] if '&' in j['url'] else j['url']
                if base_url not in seen_urls:
                    seen_urls.add(base_url)
                    all_raw_jobs.append(j)

        print(f"\n[✓] Total de vacantes únicas extraídas de LinkedIn: {len(all_raw_jobs)}")
        if not all_raw_jobs:
            print("[!] No se encontraron nuevas vacantes en las últimas 24 horas con solicitud sencilla.")
            return

        # 5. Evaluación de Compatibilidad (Mega Match 100% Texto con IA)
        print(f"\n[5] Evaluando compatibilidad técnica y lingüística con Qwen 3.8 Flash...")
        evaluated_jobs = []

        for idx, job in enumerate(all_raw_jobs, 1):
            print(f"\n[{idx}/{len(all_raw_jobs)}] Evaluando: '{job['title']}' @ '{job['company']}'...")
            match_result = match_job_with_cv(cv_text, job)
            
            score = match_result.get("match_score", 0)
            verdict = match_result.get("match_verdict", "N/A")
            job["match"] = match_result
            evaluated_jobs.append(job)

            badge = "🔥 [MEGA MATCH]" if score >= 85 else ("⭐ [BUEN MATCH]" if score >= 70 else "⚪ [DESCARTAR/REGULAR]")
            print(f"    Score: {score}/100 | {badge} | {verdict}")
            for r in match_result.get("match_reasons", [])[:2]:
                print(f"    + {r}")
            for g in match_result.get("missing_or_gaps", [])[:1]:
                print(f"    - {g}")

        # Ordenar por mejor puntuación
        evaluated_jobs.sort(key=lambda x: x["match"].get("match_score", 0), reverse=True)

        # 6. Guardar resultados y reporte final
        output_file = "ranking_ofertas_linkedin.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(evaluated_jobs, f, indent=2, ensure_ascii=False)

        print("\n" + "="*75)
        print(" 🎯 TOP OFERTAS PARA POSTULAR CON SOLICITUD SENCILLA ")
        print("="*75)
        for rank, j in enumerate(evaluated_jobs, 1):
            score = j['match'].get('match_score', 0)
            print(f"\n#{rank} [{score} pts] {j['title']} @ {j['company']}")
            print(f"   Ubicación: {j['location']}")
            print(f"   Veredicto: {j['match'].get('match_verdict')} | Recomendación: {j['match'].get('action_recommendation')}")
            print(f"   Enlace directo para postular: {j['url']}")

        print(f"\n[✓] Ranking guardado en: '{output_file}'")
        input("\nPresiona Enter en esta terminal para finalizar...")

    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        bot.close()

if __name__ == "__main__":
    main()

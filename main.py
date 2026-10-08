import os
import sys
import json
import glob
from dotenv import load_dotenv

load_dotenv()

from cv_parser import extract_text_from_pdf
from ai_matcher import generate_search_plan, match_job_with_cv
from linkedin_bot import LinkedInBot
from db_manager import DatabaseManager

TARGET_ACCEPTED_MATCHES = 20
MIN_ACCEPT_SCORE = 80

def find_pdf_resume() -> str:
    candidates = glob.glob("*.pdf") + glob.glob("cv/*.pdf")
    if candidates:
        for c in candidates:
            if "luis" in c.lower():
                return c
        return candidates[0]
    return None

def main():
    print("=" * 80)
    print(" 🚀 LinkedIn Autonomous AI Hunter — Cazador Inagotable con PostgreSQL 🚀")
    print("=" * 80)

    # 1. Inicializar Gestor de Base de Datos y Memoria
    db = DatabaseManager()
    stats = db.get_counts()
    print(f"\n📊 Estado de Memoria Persistente:")
    print(f"   • Total vacantes en historial: {stats['total']}")
    print(f"   • Vacantes aprobadas (>= 80 pts): {stats['accepted']}")
    print(f"   • Vacantes descartadas / omitidas: {stats['discarded']}")

    accepted_jobs = db.get_accepted_jobs(min_score=MIN_ACCEPT_SCORE, limit=TARGET_ACCEPTED_MATCHES)
    accepted_count = len(accepted_jobs)

    if accepted_count >= TARGET_ACCEPTED_MATCHES:
        print(f"\n[✓] Ya tienes {accepted_count} ofertas aprobadas de alta calidad en tu base de datos.")
        print(f"    Exportando ranking actualizado...")
        db.export_accepted_to_json("ranking_ofertas_linkedin.json")
        resp = input("\n¿Deseas buscar aún más ofertas nuevas en LinkedIn? (s/n): ").strip().lower()
        if resp not in ["s", "si", "y", "yes"]:
            print("Finalizado por el usuario.")
            return

    # 2. Localizar y parsear el currículum
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

    # 3. Planificación Inicial con IA
    print(f"\n[2] Diseñando plan de búsqueda inteligente según idioma y perfil del CV...")
    search_queries = generate_search_plan(cv_text)
    all_queries_used = list(search_queries)

    print("\n[✓] Términos iniciales generados por la IA:")
    for idx, q in enumerate(search_queries, 1):
        print(f"    {idx}. \"{q}\"")

    # 4. Iniciar Microsoft Edge con sesión persistente
    print("\n[3] Iniciando Microsoft Edge con sesión permanente...")
    bot = LinkedInBot(headless=False)

    try:
        bot.start_browser()
        bot.check_or_prompt_login()

        # 5. Bucle Inagotable de Búsqueda hasta alcanzar la meta
        print("\n[4] 🎯 Iniciando Modo Cazador Inagotable:")
        print(f"    • Meta objetivo: {TARGET_ACCEPTED_MATCHES} vacantes aprobadas con score >= {MIN_ACCEPT_SCORE} pts.")
        print("    • Filtros estrictos: [En Remoto] + [Solicitud Sencilla] + [Últimas 24 Horas].")
        print("    • Memoria activa: Las vacantes repetidas o descartadas se omiten al instante.")

        current_query_idx = 0
        current_offset = 0
        consecutive_empty_batches = 0

        while accepted_count < TARGET_ACCEPTED_MATCHES:
            if current_query_idx >= len(search_queries):
                # Generar nuevo lote de búsquedas cuando se agotan las anteriores
                print("\n" + "-" * 75)
                print(f"[🔄] Lote de consultas agotado. Solicitando nuevas combinaciones a la IA...")
                new_queries = generate_search_plan(cv_text, previous_queries=all_queries_used)
                fresh_queries = [q for q in new_queries if q not in all_queries_used]
                
                if not fresh_queries:
                    consecutive_empty_batches += 1
                    if consecutive_empty_batches >= 3:
                        print("\n[!] No se encontraron más combinaciones viables en las últimas 24 horas.")
                        break
                else:
                    consecutive_empty_batches = 0
                    print(f"[+] Nuevos términos agregados al radar: {', '.join(fresh_queries)}")
                    search_queries.extend(fresh_queries)
                    all_queries_used.extend(fresh_queries)

            active_query = search_queries[current_query_idx]
            jobs_found = bot.search_jobs(query=active_query, limit=5, start_offset=current_offset)

            if not jobs_found:
                # Pasar a la siguiente query
                current_query_idx += 1
                current_offset = 0
                continue

            # Evaluar vacantes encontradas
            for job in jobs_found:
                if accepted_count >= TARGET_ACCEPTED_MATCHES:
                    break

                job_url = job.get("url", "")
                
                # 1. Comprobar memoria persistente en PostgreSQL
                if db.is_job_seen(job_url):
                    print(f"    [⏭️  Ya en Memoria]: {job.get('title', '')} @ {job.get('company', '')} (Omitida)")
                    continue

                # 2. Evaluación con IA
                print(f"\n⚡ [Evaluando con IA]: '{job.get('title', '')}' @ '{job.get('company', '')}'...")
                match_result = match_job_with_cv(cv_text, job)
                score = match_result.get("match_score", 0)
                verdict = match_result.get("match_verdict", "N/A")

                is_accepted = score >= MIN_ACCEPT_SCORE
                status = "accepted" if is_accepted else "discarded"

                # 3. Guardado en streaming inmediato a PostgreSQL
                db.save_job(job, match_result, status=status)

                if is_accepted:
                    accepted_count += 1
                    badge = "🔥 [MEGA MATCH]" if score >= 85 else "⭐ [BUEN MATCH]"
                    print(f"    {badge} APROBADA: {score}/100 | {verdict}")
                    print(f"    🏆 Progreso: [{accepted_count}/{TARGET_ACCEPTED_MATCHES} vacantes aprobadas con >= {MIN_ACCEPT_SCORE} pts]")
                    for r in match_result.get("match_reasons", [])[:2]:
                        print(f"       + {r}")

                    # Exportar inmediatamente a JSON para que la web o el usuario vean el nuevo match
                    db.export_accepted_to_json("ranking_ofertas_linkedin.json")
                else:
                    print(f"    ⚪ DESCARTADA: {score}/100 (< {MIN_ACCEPT_SCORE} pts o barrera de idioma)")
                    for g in match_result.get("missing_or_gaps", [])[:1]:
                        print(f"       - {g}")

            # Avanzar paginación de la consulta activa
            current_offset += 25
            if current_offset >= 50:
                # Tras 2 páginas de la misma consulta, rotar al siguiente término para mayor diversidad
                current_query_idx += 1
                current_offset = 0

        # Reporte final
        print("\n" + "=" * 80)
        print(f" 🎯 RESUMEN FINAL DEL CAZADOR: [{accepted_count}/{TARGET_ACCEPTED_MATCHES} VACANTES]")
        print("=" * 80)
        
        top_jobs = db.get_accepted_jobs(min_score=MIN_ACCEPT_SCORE, limit=TARGET_ACCEPTED_MATCHES)
        for rank, j in enumerate(top_jobs, 1):
            score = j["match"].get("match_score", 0)
            verdict = j["match"].get("match_verdict", "")
            rec = j["match"].get("action_recommendation", "Postular")
            print(f"\n#{rank} [{score} pts • {verdict}] {j['title']} @ {j['company']}")
            print(f"   Ubicación: {j['location']}")
            print(f"   Acción: {rec}")
            print(f"   Enlace directo (Solicitud Sencilla): {j['url']}")

        exported_count = db.export_accepted_to_json("ranking_ofertas_linkedin.json")
        print(f"\n[✓] {exported_count} vacantes exportadas a 'ranking_ofertas_linkedin.json'.")
        print("[✓] Todas las vacantes quedan respaldadas y memorizadas en PostgreSQL.")

    except KeyboardInterrupt:
        print("\n[!] Búsqueda detenida por el usuario. Todos los avances fueron guardados en PostgreSQL.")
    finally:
        bot.close()

if __name__ == "__main__":
    main()

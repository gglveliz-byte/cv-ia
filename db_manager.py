import os
import hashlib
import json
import sqlite3
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """
    Gestor de persistencia híbrido:
    - Conecta prioritariamente a PostgreSQL si DATABASE_URL está configurado.
    - Si falla o no está disponible, utiliza SQLite local ('memoria_vacantes.db') como fallback transparente.
    """
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "").strip()
        self.is_postgres = False
        self.conn = None
        self._init_connection()

    def _init_connection(self):
        if self.db_url and "postgres" in self.db_url:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self.conn = psycopg2.connect(self.db_url, sslmode="require")
                self.conn.autocommit = True
                self.is_postgres = True
                print("[✓] Conexión establecida con PostgreSQL (Render Cloud).")
                self._init_postgres_schema()
                return
            except Exception as e:
                print(f"[!] No se pudo conectar a PostgreSQL ({e}). Usando SQLite local de respaldo...")

        # Fallback a SQLite
        self.is_postgres = False
        self._init_sqlite_schema()
        print("[✓] Memoria persistente activa con SQLite local ('memoria_vacantes.db').")

    def _get_url_hash(self, url: str) -> str:
        # Normalizar URL eliminando query parameters volátiles de tracking
        clean_url = url.split('&')[0] if '&' in url else url
        clean_url = clean_url.split('?')[0] if '?' in clean_url and 'currentJobId' not in clean_url else clean_url
        return hashlib.sha256(clean_url.encode('utf-8')).hexdigest()

    def _init_postgres_schema(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scanned_jobs (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    url_hash VARCHAR(64) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    description TEXT,
                    match_score INTEGER NOT NULL,
                    match_verdict VARCHAR(50) NOT NULL,
                    match_reasons JSONB DEFAULT '[]'::jsonb,
                    missing_or_gaps JSONB DEFAULT '[]'::jsonb,
                    action_recommendation TEXT,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_scanned_jobs_status ON scanned_jobs(status);
                CREATE INDEX IF NOT EXISTS idx_scanned_jobs_score ON scanned_jobs(match_score);
            """)

    def _init_sqlite_schema(self):
        conn = sqlite3.connect("memoria_vacantes.db")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scanned_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                url_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                match_score INTEGER NOT NULL,
                match_verdict TEXT NOT NULL,
                match_reasons TEXT DEFAULT '[]',
                missing_or_gaps TEXT DEFAULT '[]',
                action_recommendation TEXT,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_scanned_jobs_status ON scanned_jobs(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_scanned_jobs_score ON scanned_jobs(match_score)")
        conn.commit()
        conn.close()

    def is_job_seen(self, url: str) -> bool:
        """Verifica si la vacante ya fue procesada anteriormente."""
        url_hash = self._get_url_hash(url)
        clean_url = url.split('&')[0] if '&' in url else url

        if self.is_postgres:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM scanned_jobs WHERE url_hash = %s OR url LIKE %s LIMIT 1",
                        (url_hash, f"{clean_url}%")
                    )
                    return cur.fetchone() is not None
            except Exception as e:
                print(f"[!] Error consultando PostgreSQL ({e}). Reconectando...")
                self._init_connection()
                return False
        else:
            conn = sqlite3.connect("memoria_vacantes.db")
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM scanned_jobs WHERE url_hash = ? OR url LIKE ? LIMIT 1",
                (url_hash, f"{clean_url}%")
            )
            exists = cur.fetchone() is not None
            conn.close()
            return exists

    def save_job(self, job_data: Dict[str, Any], match_result: Dict[str, Any], status: str) -> bool:
        """
        Inserta en streaming la vacante procesada.
        status: 'accepted' (score >= 80) | 'discarded' (score < 80 o barrera de idioma)
        """
        url = job_data.get("url", "")
        url_hash = self._get_url_hash(url)
        title = job_data.get("title", "")
        company = job_data.get("company", "")
        location = job_data.get("location", "")
        description = job_data.get("description", "")
        
        score = int(match_result.get("match_score", 0))
        verdict = str(match_result.get("match_verdict", "DESCARTAR"))
        reasons = match_result.get("match_reasons", [])
        gaps = match_result.get("missing_or_gaps", [])
        action = str(match_result.get("action_recommendation", ""))

        if self.is_postgres:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO scanned_jobs 
                        (url, url_hash, title, company, location, description, match_score, match_verdict, match_reasons, missing_or_gaps, action_recommendation, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (url_hash) DO UPDATE SET
                            match_score = EXCLUDED.match_score,
                            match_verdict = EXCLUDED.match_verdict,
                            status = EXCLUDED.status
                    """, (
                        url, url_hash, title, company, location, description,
                        score, verdict, json.dumps(reasons), json.dumps(gaps), action, status
                    ))
                return True
            except Exception as e:
                print(f"[-] Error guardando en PostgreSQL: {e}")
                return False
        else:
            try:
                conn = sqlite3.connect("memoria_vacantes.db")
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO scanned_jobs 
                    (url, url_hash, title, company, location, description, match_score, match_verdict, match_reasons, missing_or_gaps, action_recommendation, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    url, url_hash, title, company, location, description,
                    score, verdict, json.dumps(reasons), json.dumps(gaps), action, status
                ))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"[-] Error guardando en SQLite: {e}")
                return False

    def get_accepted_jobs(self, min_score: int = 80, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtiene las mejores vacantes aceptadas ordenadas por puntuación."""
        if self.is_postgres:
            try:
                from psycopg2.extras import RealDictCursor
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT title, company, location, url, description, match_score, match_verdict, match_reasons, missing_or_gaps, action_recommendation
                        FROM scanned_jobs
                        WHERE status = 'accepted' AND match_score >= %s
                        ORDER BY match_score DESC, created_at DESC
                        LIMIT %s
                    """, (min_score, limit))
                    rows = cur.fetchall()
                    result = []
                    for r in rows:
                        result.append({
                            "title": r["title"],
                            "company": r["company"],
                            "location": r["location"],
                            "url": r["url"],
                            "description": r["description"],
                            "match": {
                                "match_score": r["match_score"],
                                "match_verdict": r["match_verdict"],
                                "match_reasons": r["match_reasons"] if isinstance(r["match_reasons"], list) else json.loads(r["match_reasons"] or "[]"),
                                "missing_or_gaps": r["missing_or_gaps"] if isinstance(r["missing_or_gaps"], list) else json.loads(r["missing_or_gaps"] or "[]"),
                                "action_recommendation": r["action_recommendation"]
                            }
                        })
                    return result
            except Exception as e:
                print(f"[-] Error leyendo de PostgreSQL: {e}")
                return []
        else:
            conn = sqlite3.connect("memoria_vacantes.db")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT title, company, location, url, description, match_score, match_verdict, match_reasons, missing_or_gaps, action_recommendation
                FROM scanned_jobs
                WHERE status = 'accepted' AND match_score >= ?
                ORDER BY match_score DESC, created_at DESC
                LIMIT ?
            """, (min_score, limit))
            rows = cur.fetchall()
            result = []
            for r in rows:
                result.append({
                    "title": r["title"],
                    "company": r["company"],
                    "location": r["location"],
                    "url": r["url"],
                    "description": r["description"],
                    "match": {
                        "match_score": r["match_score"],
                        "match_verdict": r["match_verdict"],
                        "match_reasons": json.loads(r["match_reasons"] or "[]"),
                        "missing_or_gaps": json.loads(r["missing_or_gaps"] or "[]"),
                        "action_recommendation": r["action_recommendation"]
                    }
                })
            conn.close()
            return result

    def get_counts(self) -> Dict[str, int]:
        """Retorna estadísticas de vacantes vistas y aceptadas."""
        if self.is_postgres:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM scanned_jobs")
                    total = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM scanned_jobs WHERE status = 'accepted'")
                    accepted = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM scanned_jobs WHERE status = 'discarded'")
                    discarded = cur.fetchone()[0]
                    return {"total": total, "accepted": accepted, "discarded": discarded}
            except Exception:
                return {"total": 0, "accepted": 0, "discarded": 0}
        else:
            conn = sqlite3.connect("memoria_vacantes.db")
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM scanned_jobs")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM scanned_jobs WHERE status = 'accepted'")
            accepted = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM scanned_jobs WHERE status = 'discarded'")
            discarded = cur.fetchone()[0]
            conn.close()
            return {"total": total, "accepted": accepted, "discarded": discarded}

    def export_accepted_to_json(self, output_file: str = "ranking_ofertas_linkedin.json") -> int:
        """Exporta las ofertas aceptadas para consumo directo de la web."""
        jobs = self.get_accepted_jobs(min_score=80, limit=20)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        return len(jobs)

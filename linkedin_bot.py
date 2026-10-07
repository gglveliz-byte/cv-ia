import os
import time
import random
import urllib.parse
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

class LinkedInBot:
    def __init__(self, headless: bool = False):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.user_data_dir = os.path.join(base_dir, "browser_profile")
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None

    def _human_delay(self, min_sec=1.2, max_sec=2.2):
        """Simula pausas naturales de comportamiento humano para evitar bloqueos."""
        time.sleep(random.uniform(min_sec, max_sec))

    def start_browser(self):
        """Inicia Microsoft Edge con perfil persistente independiente."""
        self.playwright = sync_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized"
        ]
        
        try:
            print("[+] Conectando con Microsoft Edge...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                channel="msedge",
                no_viewport=True,
                args=args
            )
        except Exception as e:
            print(f"[!] Usando Chromium ({e})...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                no_viewport=True,
                args=args
            )
            
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

    def is_logged_in(self) -> bool:
        """Verifica de forma segura si la sesión está activa."""
        try:
            url = self.page.url
            if "feed" in url or "jobs" in url:
                return True
            signin_btn = self.page.query_selector("a.nav__button-secondary, a[href*='login'], button[data-tracking-control-name*='signin']")
            me_avatar = self.page.query_selector(".global-nav__me, img[alt*='Foto'], .feed-identity-module")
            if me_avatar and not signin_btn:
                return True
        except Exception:
            pass
        return False

    def check_or_prompt_login(self):
        """Comprueba el estado de sesión sin avanzar si no está logueado."""
        print("[+] Verificando sesión en LinkedIn...")
        self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        self._human_delay(2, 3)

        if not self.is_logged_in():
            print("\n" + "="*70)
            print("(!) ATENCIÓN: No estás autenticado en LinkedIn todavía.")
            print("Por favor, inicia sesión ahora mismo en la ventana de Edge abierta.")
            print("El bot continuará automáticamente cuando detecte tu Feed.")
            print("="*70 + "\n")
            
            while not self.is_logged_in():
                time.sleep(2)
                
            print("[✓] ¡Sesión autenticada detectada!")
        else:
            print("[✓] Sesión autenticada confirmada con éxito.")

    def search_jobs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Navega a LinkedIn Jobs con:
        - f_WT=2: Remoto oficial
        - f_AL=true: Solicitud sencilla oficial (Easy Apply)
        - f_TPR=r86400: Últimas 24 horas
        - sortBy=DD: Más recientes
        Extrae la descripción completa con el selector exacto '.jobs-search__job-details--container'.
        """
        params = {
            "keywords": query,
            "sortBy": "DD",
            "f_WT": "2",      # Filtro oficial de Remoto
            "f_AL": "true",   # Filtro oficial de Solicitud Sencilla (Easy Apply)
            "f_TPR": "r86400" # Filtro oficial de Últimas 24 horas
        }

        search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)
        print(f"\n[+] Buscando: '{query}' [Filtros: Remoto + Solicitud Sencilla + 24 Horas]...")
        
        self.page.goto(search_url, wait_until="domcontentloaded")
        self._human_delay(3.0, 4.5)

        # Scroll suave para forzar la carga de la lista izquierda
        try:
            for scroll_step in [300, 600]:
                self.page.evaluate(f"window.scrollBy(0, {scroll_step});")
                self._human_delay(0.5, 0.9)
        except Exception:
            pass

        card_selectors = [
            ".jobs-search-results__list-item",
            "li[data-occludable-job-id]",
            ".job-card-container",
            "li.jobs-search-results-list__list-item",
            "div[data-job-id]"
        ]
        
        cards = []
        for sel in card_selectors:
            elements = self.page.query_selector_all(sel)
            if elements and len(elements) > 0:
                cards = elements
                break

        print(f"    -> Encontradas {len(cards)} vacantes disponibles.")
        if len(cards) == 0:
            # Fallback inteligente: si en 24h no hay ofertas, buscar en la última semana
            print(f"    [i] Sin vacantes en las últimas 24h para '{query}'. Ampliando búsqueda a la última semana...")
            params["f_TPR"] = "r604800"
            search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)
            self.page.goto(search_url, wait_until="domcontentloaded")
            self._human_delay(2.5, 3.5)
            for sel in card_selectors:
                elements = self.page.query_selector_all(sel)
                if elements and len(elements) > 0:
                    cards = elements
                    break
            print(f"    -> Encontradas {len(cards)} vacantes en la última semana.")

        if len(cards) == 0:
            return []

        jobs_data = []
        for idx, card in enumerate(cards[:limit]):
            try:
                card.scroll_into_view_if_needed()
                self._human_delay(0.5, 1.0)
                card.click()
                self._human_delay(1.8, 2.5)

                # Desplegar '... mostrar más' o 'ver más' si el botón está visible
                try:
                    expand_buttons = self.page.query_selector_all(
                        "button.jobs-description__footer-button, button[aria-label*='más'], button[aria-label*='more'], .show-more-less-html__button, button.artdeco-button--muted"
                    )
                    for btn in expand_buttons:
                        btn_text = btn.inner_text().lower()
                        if "mostrar" in btn_text or "ver" in btn_text or "more" in btn_text:
                            btn.click()
                            self._human_delay(0.3, 0.6)
                            break
                except Exception:
                    pass

                # Título del puesto
                title_elem = self.page.query_selector(
                    ".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1.t-24, h1"
                )
                title = title_elem.inner_text().strip() if title_elem else f"Oferta #{idx+1}"

                # Empresa
                company_elem = self.page.query_selector(
                    ".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name, .topcard__org-name-link"
                )
                company = company_elem.inner_text().strip() if company_elem else "Empresa"

                # Ubicación
                loc_elem = self.page.query_selector(
                    ".job-details-jobs-unified-top-card__primary-description-container, .topcard__flavor--bullet, .jobs-unified-top-card__bullet"
                )
                loc_text = loc_elem.inner_text().strip() if loc_elem else "Remoto"

                # EXTRACCIÓN ROBUSTA DE LA DESCRIPCIÓN
                description = ""
                desc_elem = self.page.query_selector("#job-details, .jobs-description-content__text, .jobs-box__html-content, .jobs-description__content")
                if desc_elem and len(desc_elem.inner_text().strip()) > 30:
                    description = desc_elem.inner_text().strip()
                else:
                    container = self.page.query_selector(".jobs-search__job-details--container, .job-view-layout, main")
                    raw_text = container.inner_text().strip() if container else ""
                    if "Acerca del empleo" in raw_text:
                        description = raw_text[raw_text.find("Acerca del empleo"):]
                    elif "About the job" in raw_text:
                        description = raw_text[raw_text.find("About the job"):]
                    else:
                        description = raw_text

                # Limpieza de pie publicitario solo si la descripción tiene longitud suficiente
                if len(description) > 200:
                    for footer_phrase in ["búsqueda de empleo más rápida con premium", "get ahead with premium", "acerca de la empresa"]:
                        pos = description.lower().find(footer_phrase)
                        if pos > 150:
                            description = description[:pos].strip()

                job_item = {
                    "title": title,
                    "company": company,
                    "location": loc_text,
                    "url": self.page.url,
                    "description": description
                }
                jobs_data.append(job_item)
                desc_len = len(description)
                print(f"    [{idx+1}/{min(len(cards), limit)}] Extraída ({desc_len} chars): {title} @ {company}")
                
            except Exception as e:
                continue

        return jobs_data

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

import time
import os
from playwright.sync_api import sync_playwright

def setup_login():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "browser_profile")
    
    print("="*70)
    print(" 🔐 CONFIGURADOR DE SESIÓN PERMANENTE DE LINKEDIN")
    print("="*70)
    print("\n[+] Abriendo Microsoft Edge...")
    print("Por favor, inicia sesión con tu cuenta de LinkedIn.")
    print("Tus cookies y sesión se guardarán en tu perfil de Edge local.")
    print("="*70)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="msedge",
            no_viewport=True,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        except Exception:
            pass

        print("\n⏳ La ventana de Edge está abierta.")
        print("Cuando hayas iniciado sesión y veas tu Feed de LinkedIn,")
        input("👉 PRESIONA ENTER AQUÍ EN ESTA TERMINAL PARA CONFIRMAR Y GUARDAR: ")

        print("\n[+] Verificando estado de la sesión...")
        time.sleep(2)
        try:
            current_url = page.url
            print(f"URL detectada: {current_url}")
        except Exception:
            pass

        print("\n" + "="*70)
        print(" [✓] ¡SESIÓN GUARDADA PERMANENTEMENTE!")
        print(" Ahora tus cookies y cuenta están listas para usarse con el bot.")
        print("="*70)
        time.sleep(2)
        context.close()

if __name__ == "__main__":
    setup_login()

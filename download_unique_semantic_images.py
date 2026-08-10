import sys
import os
import requests
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.landing_theme_engine import THEMES_POR_CATEGORIA

BASE_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(BASE_DIR, "frontend", "img", "services")
NEWS_DIR = os.path.join(BASE_DIR, "frontend", "img", "news")

os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(NEWS_DIR, exist_ok=True)

# Mapeo específico 1 a 1 de cada image_key a palabras clave únicas en inglés
SPECIFIC_KEYWORDS = {
    # LOGISTICA
    "log_fletes": "moving-van,moving-truck",
    "log_monitoreo": "gps-tracking,satellite-dashboard",
    "log_puntualidad": "delivery-clock,punctual-courier",
    "log_cotizacion": "calculator-clipboard,logistics-quote",
    "log_b2b": "warehouse-forklift,industrial-cargo",
    "log_embalaje": "cardboard-boxes,package-packing",
    "log_news_rutas": "highway-map,gps-route",
    "log_news_mudanza": "moving-home,relocation-boxes",
    "log_news_flota": "truck-fleet,highway-transport",

    # MOTOS
    "motos_service_integral": "motorcycle-mechanic,bike-service",
    "motos_diagnostico": "motorcycle-engine,diagnostic-scan",
    "motos_carburacion": "carburetor,engine-tuning",
    "motos_frenos": "disc-brake,motorcycle-suspension",
    "motos_mecanica": "motorcycle-engine-repair,workshop-tools",
    "motos_repuestos": "chain-sprocket,motorcycle-parts",
    "motos_news_kit": "motorcycle-chain,drive-belt",
    "motos_news_efi": "fuel-injection,engine-control",
    "motos_news_frenado": "motorcycle-brakes,safety-helmet",

    # AUTOMOTRIZ
    "auto_diagnostico_escaneo": "obd-scanner,car-diagnostic",
    "auto_mantenimiento_service": "car-oil-change,car-mechanic",
    "auto_frenos_suspension": "car-brake-disc,car-suspension",
    "auto_mecanica_pesada": "car-engine-repair,lifted-car",
    "auto_repuestos_originales": "car-parts,oil-filter",
    "auto_revision_previaje": "car-inspection,tire-check",
    "auto_news_diagnostico": "car-computer,mechanic-tablet",
    "auto_news_frenos": "brake-pads,automotive-safety",
    "auto_news_herramientas": "mechanic-tools,garage-equipment",

    # SALUD Y BELLEZA
    "salud_atencion": "medical-consultation,doctor-patient",
    "salud_equipamiento": "laser-dermatology,spa-equipment",
    "salud_estetica_facial": "facial-massage,skincare-treatment",
    "salud_especialistas": "dentist-doctor,medical-team",
    "salud_turnos": "reception-desk,appointment-calendar",
    "salud_ambiente_relax": "spa-wellness,relaxing-room",
    "salud_news_faciales": "facial-mask,beauty-spa",
    "salud_news_multidisciplinaria": "medical-clinic,doctors-meeting",
    "salud_news_preventivo": "healthy-lifestyle,wellness-care",

    # GASTRONOMIA
    "gastro_platos_autor": "gourmet-dish,chef-plating",
    "gastro_menu_qr": "qr-code-menu,smartphone-restaurant",
    "gastro_reservas": "reserved-table,fine-dining",
    "gastro_catering": "catering-buffet,event-food",
    "gastro_delivery": "delivery-food-box,takeaway-bag",
    "gastro_promos": "executive-lunch,restaurant-special",
    "gastro_news_carta": "fresh-menu,seasonal-dish",
    "gastro_news_calidad": "fresh-ingredients,chef-cooking",
    "gastro_news_maridaje": "wine-tasting,wine-glass",

    # INMOBILIARIA
    "inmo_propiedades": "modern-house,luxury-apartment",
    "inmo_tasaciones": "house-appraisal,real-estate-agent",
    "inmo_legal": "contract-signing,keys-handover",
    "inmo_inversiones": "architectural-blueprint,building-construction",
    "inmo_gestion": "property-management,tenant-keys",
    "inmo_tours": "virtual-tour-vr,house-showing",
    "inmo_news_inversion": "skyline-buildings,real-estate-chart",
    "inmo_news_guia": "first-home,house-keys",
    "inmo_news_tendencias": "modern-architecture,interior-design",

    # TECNOLOGIA
    "tech_desarrollo": "web-developer,coding-laptop",
    "tech_seguridad": "cybersecurity,shield-lock-code",
    "tech_cloud": "cloud-server,data-center",
    "tech_integraciones": "api-network,software-connect",
    "tech_soporte": "it-support,headset-computer",
    "tech_consultoria": "tech-consultant,scrum-board",
    "tech_news_ia": "artificial-intelligence,chip-brain",
    "tech_news_seguridad": "network-security,hacker-defense",
    "tech_news_cloud": "cloud-infrastructure,server-rack",

    # RETAIL
    "retail_productos": "store-shelf,product-display",
    "retail_envios": "express-shipping,delivery-box",
    "retail_atencion": "customer-service,retail-clerk",
    "retail_garantia": "quality-guarantee,warranty-card",
    "retail_promos": "discount-tag,sale-shopping",
    "retail_pagos": "pos-terminal,credit-card-pay",
    "retail_news_coleccion": "fashion-collection,clothing-rack",
    "retail_news_talles": "measuring-tape,clothes-fitting",
    "retail_news_beneficios": "shopping-bags,happy-customer",

    # SERVICIOS HOGAR
    "hogar_urgencias": "plumber-wrench,emergency-repair",
    "hogar_tecnicos": "electrician-tools,technician-work",
    "hogar_presupuesto": "plumbing-estimate,repair-invoice",
    "hogar_garantia": "signed-guarantee,workmanship",
    "hogar_reformas": "home-renovation,painting-wall",
    "hogar_calidad": "quality-materials,hardware-tools",
    "hogar_news_prevention": "pipe-inspection,home-maintenance",
    "hogar_news_aire": "air-conditioner-repair,hvac",
    "hogar_news_seguridad": "electrical-panel,circuit-breaker",

    # EDUCACION
    "edu_cursos": "classroom-lecture,students-learning",
    "edu_modalidad": "online-learning,laptop-study",
    "edu_docentes": "teacher-blackboard,professor",
    "edu_certificacion": "diploma-certificate,graduation",
    "edu_empleo": "job-interview,internship",
    "edu_tutoria": "tutoring-session,student-mentor",
    "edu_news_inscripciones": "enrollment-form,university-desk",
    "edu_news_demandadas": "skills-workshop,coding-bootcamp",
    "edu_news_workshops": "workshop-presentation,seminar",

    # CORPORATIVO
    "corp_calidad": "corporate-office,executive-meeting",
    "corp_atencion": "business-handshake,client-consultation",
    "corp_trayectoria": "company-trophy,business-growth",
    "corp_soluciones": "custom-solutions,brainstorming",
    "corp_asesoria": "business-advisor,financial-chart",
    "corp_compromiso": "team-trust,business-partnership",
    "corp_news_infraestructura": "modern-office-building,glass-tower",
    "corp_news_tendencias": "business-trends,strategy-meeting",
    "corp_news_satisfaccion": "happy-client,customer-feedback"
}

def download_unique_image(image_key, keywords, filepath, seed_index):
    # Forzar la re-descarga de la imagen para asegurar variedad 100%
    url = f"https://loremflickr.com/800/600/{keywords}?random={seed_index}"
    try:
        r = requests.get(url, allow_redirects=True, timeout=15)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(r.content)
        print(f"[{seed_index}] Downloaded {image_key} -> {keywords}")
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"Failed to download {image_key}: {e}")
        return False

def main():
    total = 0
    success = 0
    seed = 100
    
    for category_name, theme in THEMES_POR_CATEGORIA.items():
        print(f"\n--- Category: {category_name} ---")
        
        for feature in theme.get("features", []):
            image_key = feature.get("image_key")
            if not image_key: continue
            
            keywords = SPECIFIC_KEYWORDS.get(image_key, f"{category_name},service")
            filepath = os.path.join(SERVICES_DIR, f"{image_key}.jpg")
            total += 1
            seed += 1
            if download_unique_image(image_key, keywords, filepath, seed):
                success += 1

        for news_item in theme.get("news", []):
            image_key = news_item.get("image_key")
            if not image_key: continue
            
            keywords = SPECIFIC_KEYWORDS.get(image_key, f"{category_name},news")
            filepath = os.path.join(NEWS_DIR, f"{image_key}.jpg")
            total += 1
            seed += 1
            if download_unique_image(image_key, keywords, filepath, seed):
                success += 1
                
    print(f"\nDone! Successfully updated {success}/{total} images with unique semantic queries.")

if __name__ == "__main__":
    main()

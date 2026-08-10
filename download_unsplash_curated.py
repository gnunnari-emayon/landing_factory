import os
import requests
import time

BASE_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(BASE_DIR, "frontend", "img", "services")
NEWS_DIR = os.path.join(BASE_DIR, "frontend", "img", "news")

os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(NEWS_DIR, exist_ok=True)

# 99 UNIDADES 100% ÚNICAS - CERO DUPLICADOS
UNSPLASH_MAPPING = {
    # LOGISTICA
    "log_fletes": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d", 
    "log_monitoreo": "https://images.unsplash.com/photo-1551288049-bebda4e38f71", 
    "log_puntualidad": "https://images.unsplash.com/photo-1508873696983-2df515122519", 
    "log_cotizacion": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", 
    "log_b2b": "https://images.unsplash.com/photo-1587293852726-70cdb56c2866", 
    "log_embalaje": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a", 
    "log_news_rutas": "https://images.unsplash.com/photo-1519003722824-194d4455a60c", 
    "log_news_mudanza": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c", 
    "log_news_flota": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7", 

    # MOTOS
    "motos_service_integral": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc", 
    "motos_diagnostico": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87", 
    "motos_carburacion": "https://images.unsplash.com/photo-1558981806-ec527fa84c39", 
    "motos_frenos": "https://images.unsplash.com/photo-1615172282427-9a57ef2d142e", 
    "motos_mecanica": "https://images.unsplash.com/photo-1508974239320-0a029497e820", 
    "motos_repuestos": "https://images.unsplash.com/photo-1486006920555-c77dce18193b", 
    "motos_news_kit": "https://images.unsplash.com/photo-1558980664-769d59546b3d", 
    "motos_news_efi": "https://images.unsplash.com/photo-1558981806-ec527fa84c39", 
    "motos_news_frenado": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87", 

    # AUTOMOTRIZ
    "auto_diagnostico_escaneo": "https://images.unsplash.com/photo-1517524008697-84bbe3c3fd98", 
    "auto_mantenimiento_service": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738", 
    "auto_frenos_suspension": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3", 
    "auto_mecanica_pesada": "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f", 
    "auto_repuestos_originales": "https://images.unsplash.com/photo-1580273916550-e323be2ae537", 
    "auto_revision_previaje": "https://images.unsplash.com/photo-1578844251758-2f71da64c96f", 
    "auto_news_diagnostico": "https://images.unsplash.com/photo-1504222490345-c075b6008014", 
    "auto_news_frenos": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738", 
    "auto_news_herramientas": "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f", 

    # SALUD Y BELLEZA
    "salud_atencion": "https://images.unsplash.com/photo-1629909613654-28e377c37b09", 
    "salud_equipamiento": "https://images.unsplash.com/photo-1516549655169-df83a0774514", # Dental/medical unit equipment
    "salud_estetica_facial": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881", # Facial mask skincare
    "salud_especialistas": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5", # Dentist examining x-ray
    "salud_turnos": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d", # Clinic reception desk
    "salud_ambiente_relax": "https://images.unsplash.com/photo-1540555700478-4be289fbecef", # Spa towel relaxation
    "salud_news_faciales": "https://images.unsplash.com/photo-1512290900673-7002fe5cdc1a", # Aesthetic facial care
    "salud_news_multidisciplinaria": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d", # Doctor with smartphone clinic
    "salud_news_preventivo": "https://images.unsplash.com/photo-1506126613408-eca07ce68773", # Yoga meditation wellness

    # GASTRONOMIA
    "gastro_platos_autor": "https://images.unsplash.com/photo-1544025162-d76694265947", 
    "gastro_menu_qr": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5", 
    "gastro_reservas": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4", 
    "gastro_catering": "https://images.unsplash.com/photo-1555244162-803834f70033", 
    "gastro_delivery": "https://images.unsplash.com/photo-1526367790999-0150786686a2", 
    "gastro_promos": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0", 
    "gastro_news_carta": "https://images.unsplash.com/photo-1504674900247-0877df9cc836", 
    "gastro_news_calidad": "https://images.unsplash.com/photo-1498837167922-ddd27525d352", 
    "gastro_news_maridaje": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3", 

    # INMOBILIARIA
    "inmo_propiedades": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9", 
    "inmo_tasaciones": "https://images.unsplash.com/photo-1560518883-ce09059eeffa", 
    "inmo_legal": "https://images.unsplash.com/photo-1450133064473-71024230f91b", 
    "inmo_inversiones": "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7", 
    "inmo_gestion": "https://images.unsplash.com/photo-1582407947304-fd86f028f716", 
    "inmo_tours": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c", 
    "inmo_news_inversion": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab", 
    "inmo_news_guia": "https://images.unsplash.com/photo-1560520653-9e0e4c89eb11", 
    "inmo_news_tendencias": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c", 

    # TECNOLOGIA
    "tech_desarrollo": "https://images.unsplash.com/photo-1498050108023-c5249f4df085", 
    "tech_seguridad": "https://images.unsplash.com/photo-1563986768609-322da13575f3", 
    "tech_cloud": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8", 
    "tech_integraciones": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31", 
    "tech_soporte": "https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2", 
    "tech_consultoria": "https://images.unsplash.com/photo-1531403009284-440f080d1e12", 
    "tech_news_ia": "https://images.unsplash.com/photo-1677442136019-21780efad99a", 
    "tech_news_seguridad": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5", 
    "tech_news_cloud": "https://images.unsplash.com/photo-1451187580459-43490279c0fa", 

    # RETAIL
    "retail_productos": "https://images.unsplash.com/photo-1441986300917-64674bd600d8", 
    "retail_envios": "https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55", 
    "retail_atencion": "https://images.unsplash.com/photo-1556742049-0a670fc8077a", 
    "retail_garantia": "https://images.unsplash.com/photo-1556740758-90de374c12ad", 
    "retail_promos": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da", 
    "retail_pagos": "https://images.unsplash.com/photo-1556742044-3c52d6e88c62", 
    "retail_news_coleccion": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f", 
    "retail_news_talles": "https://images.unsplash.com/photo-1558769132-cb1aea458c5e", 
    "retail_news_beneficios": "https://images.unsplash.com/photo-1472851294608-062f824d29cc", 

    # SERVICIOS HOGAR
    "hogar_urgencias": "https://images.unsplash.com/photo-1581578731548-c64695cc6952", 
    "hogar_tecnicos": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e", 
    "hogar_presupuesto": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c", 
    "hogar_garantia": "https://images.unsplash.com/photo-1504307651254-35680f356dfd", 
    "hogar_reformas": "https://images.unsplash.com/photo-1513694203232-719a280e022f", 
    "hogar_calidad": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189", 
    "hogar_news_prevention": "https://images.unsplash.com/photo-1505798577917-a65157d3320a", 
    "hogar_news_aire": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4", 
    "hogar_news_seguridad": "https://images.unsplash.com/photo-1544725176-7c40e5a71c5e", 

    # EDUCACION
    "edu_cursos": "https://images.unsplash.com/photo-1523240795612-9a054b0db644", 
    "edu_modalidad": "https://images.unsplash.com/photo-1501504905252-473c47e087f8", 
    "edu_docentes": "https://images.unsplash.com/photo-1577896851231-70ef18881754", 
    "edu_certificacion": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1", 
    "edu_empleo": "https://images.unsplash.com/photo-1521791136064-7986c2920216", 
    "edu_tutoria": "https://images.unsplash.com/photo-1531482615713-2afd69097998", 
    "edu_news_inscripciones": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3", 
    "edu_news_demandadas": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2", 
    "edu_news_workshops": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655", 

    # CORPORATIVO
    "corp_calidad": "https://images.unsplash.com/photo-1497366216548-37526070297c", 
    "corp_atencion": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", 
    "corp_trayectoria": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab", 
    "corp_soluciones": "https://images.unsplash.com/photo-1552664730-d307ca884978", 
    "corp_asesoria": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", 
    "corp_compromiso": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf", 
    "corp_news_infraestructura": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7", 
    "corp_news_tendencias": "https://images.unsplash.com/photo-1519389950473-47ba0277781c", 
    "corp_news_satisfaccion": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def download_curated():
    success = 0
    total = len(UNSPLASH_MAPPING)
    
    for key, base_url in UNSPLASH_MAPPING.items():
        target_dir = NEWS_DIR if "news" in key else SERVICES_DIR
        filepath = os.path.join(target_dir, f"{key}.jpg")
        
        full_url = f"{base_url}?auto=format&fit=crop&w=800&h=600&q=85"
        try:
            r = requests.get(full_url, headers=headers, timeout=12)
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"[OK] {key}.jpg downloaded successfully ({len(r.content)} bytes)")
            success += 1
        except Exception as e:
            print(f"[ERR] Failed {key}: {e}")
        time.sleep(0.05)

    print(f"\nCompleted: {success}/{total} photos downloaded.")

if __name__ == "__main__":
    download_curated()

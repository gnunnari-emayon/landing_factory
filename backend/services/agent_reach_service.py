from backend.services.domain_checker import es_sitio_web_propio
from backend.services.real_gis_scraper import extraer_leads_reales_geolocalizados
from backend.services.phone_enricher import enriquecer_telefono_google_maps

def ejecutar_prospeccion_agent_reach(rubro: str, ciudad: str, max_results: int = 50):
    """
    Motor de prospección real profunda conectado a la API de geolocalización satelital
    con enriquecimiento secundario de números telefónicos reales desde fichas comerciales.
    """
    leads = extraer_leads_reales_geolocalizados(tipo=rubro, ciudad=ciudad, max_results=max_results)

    # Pase secundario de enriquecimiento de teléfono para prospectos reales
    for lead in leads:
        if not lead.get("telefono"):
            tel_real = enriquecer_telefono_google_maps(lead["nombre"], ciudad)
            if tel_real:
                lead["telefono"] = tel_real

    return leads

from urllib.parse import urlparse

# Lista de dominios que son Redes Sociales, Directorios o Plataformas de terceros (NO sitios institucionales propios)
SOCIAL_AND_DIRECTORY_DOMAINS = {
    "facebook.com", "www.facebook.com", "m.facebook.com",
    "instagram.com", "www.instagram.com",
    "linkedin.com", "www.linkedin.com", "ar.linkedin.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "whatsapp.com", "api.whatsapp.com", "wa.me",
    "mercadolibre.com.ar", "www.mercadolibre.com.ar", "mercadolibre.com",
    "pedidosya.com.ar", "www.pedidosya.com.ar", "pedidosya.com",
    "rappi.com.ar", "www.rappi.com.ar",
    "google.com", "www.google.com", "maps.google.com"
}

# TLDs válidos de sitios web institucionales propios
VALID_INSTITUTIONAL_TLDS = (
    ".com", ".net", ".org", ".io", ".co", ".com.ar", ".ar", 
    ".es", ".cl", ".mx", ".lat", ".info", ".biz", ".dev", ".app", ".site"
)

def es_sitio_web_propio(url: str) -> bool:
    """
    Determina si una URL pertenece a un sitio web institucional propio de la PYME.
    Retorna True si tiene un dominio institucional (.com, .net, .org, .com.ar, etc.).
    Retorna False si la URL es nula/vacía o pertenece a redes sociales/directorios.
    """
    if not url or not isinstance(url, str):
        return False

    url_clean = url.strip().lower()
    if not url_clean.startswith(("http://", "https://")):
        url_clean = "https://" + url_clean

    try:
        parsed = urlparse(url_clean)
        domain = parsed.netloc.split(":")[0]  # Remover puerto si existe

        if not domain:
            return False

        # Si el dominio pertenece a redes sociales o directorios de terceros
        for social_domain in SOCIAL_AND_DIRECTORY_DOMAINS:
            if domain == social_domain or domain.endswith("." + social_domain):
                return False

        # Verificar que posea un TLD institucional válido
        has_valid_tld = any(domain.endswith(tld) for tld in VALID_INSTITUTIONAL_TLDS)
        return has_valid_tld

    except Exception:
        return False

import unittest
from backend.services.phone_enricher import enriquecer_telefono_google_maps
from backend.services.real_gis_scraper import extraer_leads_reales_geolocalizados

class TestPhoneEnrichmentAndStrictFilter(unittest.TestCase):
    def test_strict_category_filtering(self):
        # Buscar metalurgicas en Mendoza
        leads = extraer_leads_reales_geolocalizados("Metalúrgica & Herrería", "Mendoza, Mendoza", max_results=10)
        for l in leads:
            nombre = l["nombre"].lower()
            # Asegurar que no haya cafeterias ni restaurantes en metalurgica
            self.assertNotIn("restó", nombre)
            self.assertNotIn("café", nombre)
            self.assertNotIn("bar", nombre)

    def test_phone_enrichment_service(self):
        # Enriquecer telefono de El Kano Mendoza
        tel = enriquecer_telefono_google_maps("El Kano Restó & Café", "Mendoza")
        # Si se encuentra, debe ser un formato de contacto valido
        if tel:
            self.assertTrue(tel.startswith("+54") or len(tel) >= 8)

if __name__ == "__main__":
    unittest.main()

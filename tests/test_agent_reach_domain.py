import unittest
from backend.services.domain_checker import es_sitio_web_propio

class TestDomainChecker(unittest.TestCase):

    def test_dominios_institucionales_validos(self):
        # .com, .net, .org, .com.ar, .io, etc.
        self.assertTrue(es_sitio_web_propio("https://taller-san-martin.com"))
        self.assertTrue(es_sitio_web_propio("http://volquetescordoba.com.ar"))
        self.assertTrue(es_sitio_web_propio("https://clinicaodontologica.net"))
        self.assertTrue(es_sitio_web_propio("https://fundacionnorte.org"))
        self.assertTrue(es_sitio_web_propio("https://startuptech.io"))
        self.assertTrue(es_sitio_web_propio("empresa.ar"))

    def test_redes_sociales_y_directorios_no_validos(self):
        # Redes sociales y plataformas no se consideran sitio propio
        self.assertFalse(es_sitio_web_propio("https://facebook.com/tallermecanicosanjose"))
        self.assertFalse(es_sitio_web_propio("https://www.instagram.com/cafenorte_ok"))
        self.assertFalse(es_sitio_web_propio("https://ar.linkedin.com/in/fletescordoba"))
        self.assertFalse(es_sitio_web_propio("https://wa.me/543515550000"))
        self.assertFalse(es_sitio_web_propio("https://pedidosya.com.ar/restaurantes/cafe"))
        self.assertFalse(es_sitio_web_propio(None))
        self.assertFalse(es_sitio_web_propio(""))

if __name__ == "__main__":
    unittest.main()

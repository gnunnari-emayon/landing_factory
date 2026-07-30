import unittest
import sys
import os

# Incluir la raíz del proyecto en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.generator import inferir_categoria_por_rubro, generar_landing_page

class TestGeneratorEngine(unittest.TestCase):

    def test_inferir_categoria_gastronomia(self):
        self.assertEqual(inferir_categoria_por_rubro("Café Martínez"), "gastronomia")
        self.assertEqual(inferir_categoria_por_rubro("Panadería y Pizzería San Juan"), "gastronomia")

    def test_inferir_categoria_automotriz(self):
        self.assertEqual(inferir_categoria_por_rubro("Taller Mecánico San José"), "automotriz")
        self.assertEqual(inferir_categoria_por_rubro("Lubricentro y Repuestos Norte"), "automotriz")

    def test_inferir_categoria_salud_belleza(self):
        self.assertEqual(inferir_categoria_por_rubro("Clínica Odontológica Sonrisas"), "salud_belleza")
        self.assertEqual(inferir_categoria_por_rubro("Barbería & Spa Urbano"), "salud_belleza")

    def test_inferir_categoria_logistica(self):
        self.assertEqual(inferir_categoria_por_rubro("Fletes y Transporte Express"), "logistica")
        self.assertEqual(inferir_categoria_por_rubro("Mudanzas e Impulso Logística"), "logistica")

    def test_inferir_categoria_retail(self):
        self.assertEqual(inferir_categoria_por_rubro("Boutique de Ropa & Calzado"), "retail")

    def test_inferir_categoria_tecnologia(self):
        self.assertEqual(inferir_categoria_por_rubro("DevSoftware Cloud & Tech"), "tecnologia")

    def test_inferir_categoria_corporativo_default(self):
        self.assertEqual(inferir_categoria_por_rubro("Empresa Consultora Global XYZ"), "corporativo")
        self.assertEqual(inferir_categoria_por_rubro(""), "corporativo")

    def test_generar_landing_page_fallback(self):
        res = generar_landing_page("Café Central", "Rubro Gastronómico")
        self.assertEqual(res.categoria_visual, "gastronomia")
        self.assertEqual(res.status, "success")

if __name__ == "__main__":
    unittest.main()

import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestAgentReachService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_agent_reach_prospectar_endpoint(self):
        response = self.client.post(
            "/api/v1/agencia/b2b/prospectar-agent-reach",
            json={"rubro": "metalurgica", "ubicacion": "Mendoza, AR"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("guardados", data)

    def test_poka_yoke_sin_sitio_web_propio(self):
        from backend.services.agent_reach_service import ejecutar_prospeccion_agent_reach
        from backend.services.domain_checker import es_sitio_web_propio

        leads = ejecutar_prospeccion_agent_reach(rubro="fletes", ciudad="Córdoba, AR", max_results=5, solo_sin_web=True)
        self.assertIsInstance(leads, list)

        for lead in leads:
            # Poka-Yoke 1: Ningún lead debe poseer sitio web propio institucional (.com, .com.ar, etc.)
            self.assertFalse(
                es_sitio_web_propio(lead.get("sitio_web")),
                f"El lead {lead['nombre']} posee sitio web propio {lead.get('sitio_web')} y no cumple el criterio Poka-Yoke de venta."
            )
            # Poka-Yoke 2: El nombre debe ser una cadena válida no vacía
            self.assertTrue(len(lead["nombre"]) >= 3)

if __name__ == "__main__":
    unittest.main()

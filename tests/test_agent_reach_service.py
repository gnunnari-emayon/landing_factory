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

if __name__ == "__main__":
    unittest.main()

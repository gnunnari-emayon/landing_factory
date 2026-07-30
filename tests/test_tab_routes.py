import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestModularTabRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_prospector_route(self):
        response = self.client.get("/prospector")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Prospector Google Maps", response.text)

    def test_focus_group_route(self):
        response = self.client.get("/focus-group")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Focus Group AI", response.text)

    def test_campanias_route(self):
        response = self.client.get("/campanias")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Campañas", response.text)

if __name__ == "__main__":
    unittest.main()

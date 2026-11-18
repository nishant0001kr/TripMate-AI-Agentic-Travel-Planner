import unittest

from fastapi.testclient import TestClient

from app import app


class AppSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("TripMate", response.text)
        self.assertIn("Nishant Kumar", response.text)

    def test_health_reports_features_without_exposing_secrets(self):
        response = self.client.get("/health")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertIn("supervisor_agent", payload["features"])
        self.assertEqual(
            set(payload["integrations"]),
            {"groq", "tavily", "aviationstack", "openweather"},
        )
        self.assertIn(payload["persistence"], {"memory", "postgresql"})

        serialized = response.text
        self.assertNotIn("GROQ_API_KEY", serialized)
        self.assertNotIn("OPENWEATHER_API_KEY", serialized)


if __name__ == "__main__":
    unittest.main()

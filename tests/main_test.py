import unittest
from fastapi import testclient
from src.app.main import app

client = testclient.TestClient(app)


class MyTestCase(unittest.TestCase):
    def test_main(self):
        main_response = client.get("/healthz")
        self.assertEqual(main_response.json(), {"status": "ok", "status_code": 200})


if __name__ == "__main__":
    unittest.main()

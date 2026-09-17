"""Small dependency-light smoke tests for the CP3 HTTP contract."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


CODEBASE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODEBASE))

from server import app  # noqa: E402
import ai_core  # noqa: E402


class ServerContractTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_health_does_not_expose_api_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "secret-for-test"}, clear=False):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["api_key_configured"])
        self.assertNotIn("secret-for-test", response.get_data(as_text=True))

    def test_empty_student_input_is_rejected(self):
        response = self.client.post("/api/ask", json={"student_text": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("trống", response.get_json()["error"])

    def test_non_string_student_input_is_rejected(self):
        response = self.client.post("/api/ask", json={"student_text": 123})
        self.assertEqual(response.status_code, 400)
        self.assertIn("chuỗi", response.get_json()["error"])

    def test_unsupported_topic_is_rejected(self):
        response = self.client.post(
            "/api/ask",
            json={"student_text": "Em đang giải thích một chủ đề.", "topic_id": "unknown"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("không được hỗ trợ", response.get_json()["error"])

    def test_missing_key_returns_actionable_service_error(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            response = self.client.post("/api/ask", json={"student_text": "Em nghĩ LLM chỉ bịa khi thiếu dữ liệu."})
        self.assertEqual(response.status_code, 503)
        self.assertIn("GEMINI_API_KEY", response.get_json()["error"])

    def test_decision_path_uses_model_output_and_logs_raw_response(self):
        class FakeResponse:
            text = "Dạ, nếu dữ liệu nhiều thì điều gì bảo đảm câu trả lời luôn đúng ạ?"

        class FakeModel:
            def __init__(self):
                self.prompts = []

            def generate_content(self, prompt):
                self.prompts.append(prompt)
                return FakeResponse()

        fake_model = FakeModel()
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-only"}, clear=False):
                with patch.object(ai_core, "_model", return_value=fake_model):
                    with patch.object(ai_core, "LOG_DIR", Path(directory)):
                        output = ai_core.ask_hoc_tro(
                            "LLM có nhiều dữ liệu nên chắc chắn luôn đúng.",
                            topic_id="llm",
                        )

            self.assertEqual(output, FakeResponse.text)
            self.assertEqual(len(fake_model.prompts), 1)
            self.assertIn("LLM có nhiều dữ liệu", fake_model.prompts[0])
            logs = list(Path(directory).glob("call_*.json"))
            self.assertEqual(len(logs), 1)
            log_text = logs[0].read_text(encoding="utf-8")
            self.assertIn("prompt_sent", log_text)
            self.assertIn(FakeResponse.text, log_text)


if __name__ == "__main__":
    unittest.main()
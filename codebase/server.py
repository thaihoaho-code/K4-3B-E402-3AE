from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
try:
    from .ai_core import ConfigurationError, TOPIC_TITLES, ask_hoc_tro, runtime_status
except ImportError:  # Supports `python codebase/server.py` from repository root.
    from ai_core import ConfigurationError, TOPIC_TITLES, ask_hoc_tro, runtime_status

STATIC_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
CORS(app)  # cho frontend gọi được


@app.post("/api/ask")
def api_ask():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return jsonify({"error": "JSON request không hợp lệ"}), 400

    student_text = data.get("student_text")
    topic = data.get("topic") or "Vì sao LLM bịa"
    topic_id = data.get("topic_id") or "llm"

    if not isinstance(student_text, str):
        return jsonify({"error": "student_text phải là chuỗi"}), 400
    if not isinstance(topic, str) or not isinstance(topic_id, str):
        return jsonify({"error": "topic và topic_id phải là chuỗi"}), 400
    if topic_id not in TOPIC_TITLES:
        return jsonify({"error": "topic_id không được hỗ trợ"}), 400
    student_text = student_text.strip()

    if not student_text:
        return jsonify({"error": "student_text trống"}), 400

    try:
        reply = ask_hoc_tro(student_text, topic=topic, topic_id=topic_id)
        return jsonify({"reply": reply})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except ConfigurationError as exc:
        # Configuration/dependency failures are actionable for the demo
        # operator, but do not expose a traceback or provider internals.
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Không gọi được mô hình AI lúc này. Hãy xem log kỹ thuật để biết chi tiết."}), 502


@app.get("/health")
def health():
    return jsonify({"ok": True, **runtime_status()})


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
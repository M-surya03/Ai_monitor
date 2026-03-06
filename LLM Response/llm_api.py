"""
llm_api.py
----------
Flask API for the LLM engine — mirrors the static analyzer api.py structure.

Endpoints:
    GET  /health       – service health check
    POST /llm/analyze  – send prompt to Groq, get structured JSON back

Run:
    pip install flask flask-cors groq
    $env:GROQ_API_KEY="gsk_..."      # Windows PowerShell
    export GROQ_API_KEY="gsk_..."    # Linux / Mac
    python llm_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from llm_engine.llm_client import call_llm, health_check
from llm_engine.response_parser import parse_llm_response
from llm_engine.config import MODEL_NAME

app = Flask(__name__)
CORS(app)


# ══════════════════════════════════════════════════════════════
#  Health check
# ══════════════════════════════════════════════════════════════

@app.route("/health", methods=["GET"])
def health():
    groq_available = health_check()
    return jsonify({
        "status":          "ok" if groq_available else "degraded",
        "service":         "llm-engine",
        "model":           MODEL_NAME,
        "groq_available":  groq_available,
    })


# ══════════════════════════════════════════════════════════════
#  LLM analyze
# ══════════════════════════════════════════════════════════════

@app.route("/llm/analyze", methods=["POST"])
def llm_analyze():
    """
    Accepts the exact same payload Spring Boot sends to Ollama:
        {
            "model":  "llama-3.3-70b-versatile",   (optional — uses config default)
            "prompt": "You are a programming mentor...",
            "stream": false                          (ignored — always false)
        }

    Returns structured JSON:
        {
            "algorithm_detected":  "...",
            "time_complexity":     "...",
            "problem":             "...",
            "explanation":         "...",
            "suggested_algorithm": "...",
            "improved_complexity": "...",
            "improved_code":       "..."
        }
    """
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    prompt = data["prompt"]

    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "'prompt' must be a non-empty string"}), 400

    # Call Groq
    raw_response = call_llm(prompt)

    # Parse LLM text → structured JSON
    result = parse_llm_response(raw_response)

    return jsonify(result)


# ══════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
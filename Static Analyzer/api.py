"""
api.py — Static Analyzer Flask API
Port 5000

POST /analyze  accepts { "code": "...", "language": "python|java|js|cpp" }
and returns the exact 5-field Spring Boot contract:
    {
        "algorithm_detected": "...",
        "time_complexity":    "...",
        "issues":             [...],
        "loop_count":         2,
        "pattern":            "..."
    }
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from static_analyzer import analyze_code

app = Flask(__name__)
CORS(app)

# Exact 5-field contract expected by Spring Boot / LLMService
_CONTRACT = ["algorithm_detected", "time_complexity", "issues", "loop_count", "pattern"]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":              "ok",
        "service":             "static-analyzer",
        "version":             "2.0.0",
        "supported_languages": ["python", "java", "javascript", "cpp"],
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code     = data["code"]
    language = data.get("language")   # optional — auto-detected when absent

    result = analyze_code(code, language=language)

    if "error" in result and "algorithm_detected" not in result:
        # Hard error (e.g. empty input, size exceeded)
        return jsonify({"error": result["error"]}), 422

    # Return ONLY the 5-field contract to Spring Boot
    return jsonify({k: result[k] for k in _CONTRACT if k in result}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
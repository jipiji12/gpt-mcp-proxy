# Flask 기반 초간단 "GPT 프록시 + 헬스체크" 서버
# - GET  /healthz : 200 OK (상태 확인용)
# - POST /ask-gpt : {"prompt":"..."} -> OpenAI API 호출 후 답 반환
# - Authorization 헤더에 Bearer <ACCESS_TOKEN> 있어야 함

import os
import requests
from flask import Flask, request, jsonify

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ACCESS_TOKEN   = os.environ.get("ACCESS_TOKEN")  # Claude 커넥터에 줄 접속 토큰

app = Flask(__name__)

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True}), 200

def _auth_ok(req):
    # "Authorization: Bearer <ACCESS_TOKEN>" 확인
    auth = req.headers.get("Authorization", "")
    return auth == f"Bearer {ACCESS_TOKEN}"

@app.post("/ask-gpt")
def ask_gpt():
    if not _auth_ok(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    user_prompt = (data.get("prompt") or "").strip()
    if not user_prompt:
        return jsonify({"error": "prompt is required"}), 400

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": 0.2,
    }
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=60)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": content})
    except requests.HTTPError as e:
        # OpenAI 에러 그대로 노출
        try:
            return jsonify({"error": resp.json()}), resp.status_code
        except Exception:
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 기반 초간단 "GPT 프록시 + 헬스체크" 서버
# - /healthz : 200 OK (Claude 커넥터 연결확인용)
# - /ask-gpt : POST {"prompt": "..."} -> OpenAI에 물어보고 답 반환
# - Authorization 헤더로 Bearer <ACCESS_TOKEN> 검사

import os, requests
from flask import Flask, request, jsonify

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # Claude 쪽에 줄 접속 토큰

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
    user_prompt = data.get("prompt", "").strip()
    if not user_prompt:
        return jsonify({"error": "prompt is required"}), 400

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Be

# gpt-mcp-proxy
Simple HTTPS endpoint for Claude connector:
- GET /healthz -> 200 OK
- POST /ask-gpt with JSON: {"prompt":"..."} and header Authorization: Bearer <ACCESS_TOKEN>

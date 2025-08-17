import { Server, Tool } from "@modelcontextprotocol/sdk";
import { HttpServer } from "@modelcontextprotocol/sdk/http";
import OpenAI from "openai";

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ACCESS_TOKEN   = process.env.ACCESS_TOKEN;

// 0) 필수 환경변수 체크
if (!OPENAI_API_KEY) {
  console.error("Missing OPENAI_API_KEY");
  process.exit(1);
}
if (!ACCESS_TOKEN) {
  console.error("Missing ACCESS_TOKEN");
  process.exit(1);
}

// 1) MCP 서버 생성
const mcp = new Server({
  name: "gpt-mcp",
  version: "1.0.0"
});

// 2) 툴 등록: ask_gpt(prompt:string) -> text
mcp.addTool(new Tool({
  name: "ask_gpt",
  description: "Send a prompt to OpenAI and return text",
  inputSchema: {
    type: "object",
    properties: { prompt: { type: "string" } },
    required: ["prompt"]
  },
  handler: async ({ prompt }) => {
    const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
    const resp = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2
    });
    const text = resp.choices?.[0]?.message?.content ?? "";
    return { content: [{ type: "text", text }] };
  }
}));

// 3) HTTP(SSE) 전송으로 공개. (Claude가 /, /register 등으로 핸드셰이크)
const http = new HttpServer(mcp, {
  // Claude가 보내는 Authorization: Bearer <token> 검사
  token: ACCESS_TOKEN
});

const PORT = process.env.PORT || 10000;
await http.listen({ port: PORT });

console.log(`MCP server ready on :${PORT}`);

"""Local OpenAI-compatible /v1/embeddings service (LocRet-small, Azerbaijani).

Holographic calls the same endpoint for facts and for questions, so both get the
symmetric "query: " prefix (the e5 family's symmetric mode).
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from sentence_transformers import SentenceTransformer

MODEL_NAME = "LocalDoc/LocRet-small"
HOST, PORT = "127.0.0.1", 8765
model = SentenceTransformer(MODEL_NAME, device="cpu")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/") in ("/v1/models", "/health"):
            return self._send(200, {"object": "list", "data": [{"id": MODEL_NAME, "object": "model"}]})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/embeddings":
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            inputs = req["input"]
            if isinstance(inputs, str):
                inputs = [inputs]
            vecs = model.encode(["query: " + t for t in inputs], prompt="", normalize_embeddings=True)
        except Exception as exc:
            return self._send(400, {"error": {"message": str(exc)}})
        self._send(200, {
            "object": "list",
            "model": MODEL_NAME,
            "data": [{"object": "embedding", "index": i, "embedding": v.tolist()} for i, v in enumerate(vecs)],
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        })

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

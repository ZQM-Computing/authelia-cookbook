"""Synthetic protected upstream that echoes only test identity headers."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        identity = {
            name: self.headers.get(name, "")
            for name in ("Remote-User", "Remote-Groups", "Remote-Name", "Remote-Email")
        }
        body = ("PROTECTED_UPSTREAM_MARKER\\n" + json.dumps(identity, sort_keys=True) + "\\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


HTTPServer(("0.0.0.0", 80), Handler).serve_forever()

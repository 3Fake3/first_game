# fake_http_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"I'm alive!")

def run_http_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

import http.server
import os
import socketserver

PORT = int(os.environ.get("PORT", "8000"))
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()

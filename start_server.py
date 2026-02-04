#!/usr/bin/env python3
"""
NEXUS-ON Simple Server for Live2D Testing
Serves static files and Python-rendered HTML pages without FastAPI dependencies
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from nexus_supervisor import public_pages_i18n

class NexusHandler(SimpleHTTPRequestHandler):
    """Custom handler for NEXUS-ON pages"""
    
    def __init__(self, *args, **kwargs):
        # Change to public directory for static files
        super().__init__(*args, directory='public', **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        lang = query.get('lang', ['ko'])[0]
        
        # Route to Python-rendered pages
        if path == '/':
            self.send_html(public_pages_i18n.landing_page(lang))
        elif path == '/intro':
            self.send_html(public_pages_i18n.intro_page(lang))
        elif path == '/modules':
            self.send_html(public_pages_i18n.modules_page(lang))
        elif path == '/pricing':
            self.send_html(public_pages_i18n.pricing_page(lang))
        elif path == '/dashboard-preview':
            self.send_html(public_pages_i18n.dashboard_preview_page(lang))
        elif path == '/canvas-preview':
            self.send_html(public_pages_i18n.canvas_preview_page(lang))
        elif path == '/login':
            self.send_html(public_pages_i18n.login_page(lang))
        else:
            # Serve static files from public/
            super().do_GET()
    
    def send_html(self, html_content):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html_content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[NEXUS] {self.address_string()} - {format % args}")

if __name__ == '__main__':
    PORT = 8000
    HOST = '0.0.0.0'
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  NEXUS-ON Live2D Test Server                            ║
║  Port: {PORT}                                              ║
║  Host: {HOST}                                        ║
║  Static files: public/                                   ║
║  Live2D model: public/live2d/haru_greeter_t05.model3.json║
╚══════════════════════════════════════════════════════════╝
    """)
    
    server = HTTPServer((HOST, PORT), NexusHandler)
    print(f"✅ Server running at http://{HOST}:{PORT}/")
    print(f"📱 Pages: /, /intro, /modules, /pricing, /dashboard-preview, /canvas-preview, /login")
    print(f"🎭 Live2D character should appear on all pages")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        server.shutdown()

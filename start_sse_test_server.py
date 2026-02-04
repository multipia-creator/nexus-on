#!/usr/bin/env python3
"""
Simple SSE Test Server for NEXUS-ON Live2D + TTS Integration
Tests agent_status and TTS events without full backend dependencies
"""
import os
import sys
import json
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from nexus_supervisor import public_pages_i18n

# Simulated event queue
event_queue = []
event_id = 0

def generate_sse_event(event_type, data):
    """Generate SSE formatted event"""
    global event_id
    event_id += 1
    return f"id: {event_id}\nevent: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

def simulate_chat_response(text="안녕하세요! NEXUS-ON입니다."):
    """Simulate a chat response with agent_status and TTS events"""
    events = []
    
    # 1. Listening (received input)
    events.append(('agent_status', {
        'status': 'listening',
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        'context': {'user_message': 'Test message'}
    }))
    
    time.sleep(0.5)
    
    # 2. Thinking (processing)
    events.append(('agent_status', {
        'status': 'thinking',
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        'context': {'processing': True}
    }))
    
    time.sleep(1)
    
    # 3. Speaking (generating response)
    events.append(('agent_status', {
        'status': 'speaking',
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        'context': {'response': text[:80]}
    }))
    
    # 4. TTS Start
    events.append(('tts_start', {
        'text': text,
        'voice': 'ko-KR-Neural2-A',
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }))
    
    time.sleep(2)
    
    # 5. TTS End
    events.append(('tts_end', {
        'duration_ms': 2000,
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }))
    
    # 6. Idle (completed)
    events.append(('agent_status', {
        'status': 'idle',
        'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        'context': {'chat_completed': True}
    }))
    
    return events

class NexusSSEHandler(SimpleHTTPRequestHandler):
    """Custom handler for NEXUS-ON pages with SSE support"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='public', **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        lang = query.get('lang', ['ko'])[0]
        
        # SSE Stream endpoint
        if path == '/agent/reports/stream':
            self.handle_sse_stream()
        # Python-rendered pages
        elif path == '/':
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
        # Trigger test chat
        elif path == '/test/chat':
            self.trigger_test_chat()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_sse_stream(self):
        """Handle SSE stream with simulated events"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Send initial snapshot
        snapshot = {
            'report_id': f'snapshot-{int(time.time()*1000)}',
            'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'asks': [],
            'worklog': [],
            'autopilot': {'state': 'idle', 'blocked_by_red': False}
        }
        self.wfile.write(generate_sse_event('snapshot', snapshot).encode('utf-8'))
        self.wfile.flush()
        
        # Send ping every 15 seconds and check for events
        try:
            last_ping = time.time()
            while True:
                # Check for new events
                if event_queue:
                    event_type, data = event_queue.pop(0)
                    self.wfile.write(generate_sse_event(event_type, data).encode('utf-8'))
                    self.wfile.flush()
                
                # Send ping
                now = time.time()
                if now - last_ping >= 15:
                    ping_data = {'ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    self.wfile.write(generate_sse_event('ping', ping_data).encode('utf-8'))
                    self.wfile.flush()
                    last_ping = now
                
                time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError):
            print('[SSE] Client disconnected')
    
    def trigger_test_chat(self):
        """Trigger a test chat response"""
        # Add simulated events to queue
        events = simulate_chat_response()
        for event_type, data in events:
            event_queue.append((event_type, data))
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'status': 'ok', 'message': 'Test chat triggered', 'events': len(events)}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_html(self, html_content):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html_content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[NEXUS-SSE] {self.address_string()} - {format % args}")

if __name__ == '__main__':
    PORT = 8000
    HOST = '0.0.0.0'
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  NEXUS-ON SSE Test Server                               ║
║  Port: {PORT}                                              ║
║  Host: {HOST}                                        ║
║                                                          ║
║  Features:                                               ║
║  - SSE Stream: /agent/reports/stream                    ║
║  - Test Chat: /test/chat                                ║
║  - Live2D + TTS Integration                             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    server = HTTPServer((HOST, PORT), NexusSSEHandler)
    print(f"✅ Server running at http://{HOST}:{PORT}/")
    print(f"📱 Pages: /, /intro, /modules, /pricing, /dashboard-preview, /canvas-preview, /login")
    print(f"🎭 SSE Stream: /agent/reports/stream")
    print(f"💬 Test Chat: /test/chat (triggers simulated chat response)")
    print(f"\n🧪 Test Instructions:")
    print(f"1. Open http://localhost:{PORT}/ in browser")
    print(f"2. Open browser console (F12)")
    print(f"3. In another tab, visit http://localhost:{PORT}/test/chat")
    print(f"4. Watch Live2D character state changes + TTS audio")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        server.shutdown()

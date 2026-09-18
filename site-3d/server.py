"""
Alternativa em Python ao server.js (sem dependências externas).
    python server.py            -> http://localhost:3000
    python server.py 8080
Observação: neste modo o Three.js vem do CDN (precisa de internet).
Com Node + npm install, o Three.js é servido localmente em /vendor/three.
"""
import http.server, socketserver, sys, os, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
MODELS = os.path.join(ROOT, 'modelos')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if self.path.startswith('/api/modelos'):
            arquivos = [f for f in sorted(os.listdir(MODELS)) if f.lower().endswith('.stl')]
            dados = [{'nome': f, 'url': f'/modelos/{f}',
                      'tamanhoKB': round(os.path.getsize(os.path.join(MODELS, f)) / 1024)}
                     for f in arquivos]
            corpo = json.dumps(dados).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return
        super().do_GET()


Handler.extensions_map['.stl'] = 'model/stl'
Handler.extensions_map['.js'] = 'application/javascript'

with socketserver.ThreadingTCPServer(('', PORT), Handler) as httpd:
    print(f'\n  Guardanapeiro Modular — configurador 3D')
    print(f'  Servidor no ar:  http://localhost:{PORT}')
    print(f'  Modelos STL em:  {MODELS}')
    print('  Ctrl+C para parar.\n')
    httpd.serve_forever()

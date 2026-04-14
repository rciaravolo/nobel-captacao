"""
preview_server.py
Servidor HTTP local para visualizar o preview_email.html gerado pelo pipeline.
Acesse: http://localhost:5500
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 5500
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def do_GET(self):
        # Redireciona raiz para o preview do email
        if self.path in ('/', ''):
            self.path = '/preview_email.html'
        super().do_GET()

    def log_message(self, format, *args):
        # Log limpo no console
        print(f"  [{args[1]}] {args[0]}", flush=True)


if __name__ == '__main__':
    if not os.path.exists(os.path.join(SERVE_DIR, 'preview_email.html')):
        print("AVISO: preview_email.html nao encontrado.")
        print("Execute o pipeline com MODO_TESTE_EMAIL=True para gerar o preview.")

    server = HTTPServer(('localhost', PORT), PreviewHandler)
    print(f"Preview server rodando em: http://localhost:{PORT}")
    print(f"Servindo pasta: {SERVE_DIR}")
    print("Pressione Ctrl+C para parar.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()
        sys.exit(0)

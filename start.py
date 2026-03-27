import http.server
import os
import socketserver
import threading
import time
import webbrowser


ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("AI_DJ_PORT", "8891"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, format, *args):
        pass


class ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def open_browser():
    time.sleep(1.0)
    webbrowser.open(f"http://127.0.0.1:{PORT}/index.html")


def main():
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"YouTube AI DJ running at http://127.0.0.1:{PORT}/index.html")
    print("Press Ctrl+C to stop.")
    with ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()

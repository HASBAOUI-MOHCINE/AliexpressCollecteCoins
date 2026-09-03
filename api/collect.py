import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import collect_coins


class handler(BaseHTTPRequestHandler):
    def _run_collection(self):
        try:
            collect_coins.main()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Coin collection completed")
        except Exception as error:
            print(f"Collection failed: {error}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Coin collection failed")

    def do_POST(self):
        expected_secret = os.getenv("COLLECTOR_SECRET")
        provided_secret = self.headers.get("x-collector-secret")
        if not expected_secret or provided_secret != expected_secret:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        self._run_collection()

    def do_GET(self):
        cron_secret = os.getenv("CRON_SECRET")
        if cron_secret and self.headers.get("authorization") == f"Bearer {cron_secret}":
            self._run_collection()
            return
        self.send_response(405)
        self.end_headers()
        self.wfile.write(b"Use POST")

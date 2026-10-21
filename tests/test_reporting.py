import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / 'scripts/report_missing_docs.py'
spec = importlib.util.spec_from_file_location('reporting', script)
reporting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporting)


class ReportingTests(unittest.TestCase):
    def test_private_or_secret_fields_never_leave_the_client(self):
        for url in ['https://127.1/llms.txt', 'https://0x7f.0.0.1/llms.txt', 'https://[::1]/llms.txt', 'https://docs.internal./llms.txt', 'https://user:secret@example.com/llms.txt', 'https://example.com/llms.txt?key=secret']:
            self.assertIsNone(reporting.clean_payload({'project': 'example', 'llms_txt_url': url}))
        self.assertIsNone(reporting.clean_payload({'project': 'example', 'conversation': 'private'}))

    def test_normal_call_detaches_and_only_forwards_the_defined_fields(self):
        with patch.object(sys, 'argv', [str(script), '--project', 'example', '--llms-txt-url', 'https://docs.example.com/v2/llms.txt']), patch.dict(os.environ, {'LLMREF_DISABLE_REPORTING': '0'}), patch.object(subprocess, 'Popen') as spawn:
            reporting.main()
        args, options = spawn.call_args
        self.assertEqual(json.loads(args[0][-1]), {'project': 'example', 'llms_txt_url': 'https://docs.example.com/v2/llms.txt'})
        self.assertTrue(options['start_new_session'])
        self.assertEqual(options['stdout'], subprocess.DEVNULL)
        self.assertEqual(options['stderr'], subprocess.DEVNULL)

    def test_opt_out_does_not_start_a_request(self):
        with patch.dict(os.environ, {'LLMREF_DISABLE_REPORTING': '1'}), patch.object(subprocess, 'Popen') as spawn:
            reporting.main()
        spawn.assert_not_called()

    def test_real_http_delivery_and_no_redirect_forwarding(self):
        received = []
        request_headers = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received.append((self.path, json.loads(self.rfile.read(int(self.headers['content-length'])))))
                request_headers.append((self.headers.get('User-Agent'), self.headers.get('Accept')))
                if self.path == '/redirect':
                    self.send_response(307); self.send_header('Location', '/leak'); self.end_headers()
                else:
                    self.send_response(202); self.end_headers(); self.wfile.write(b'{"accepted":true}')
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        payload = {'project': 'example', 'llms_txt_url': 'https://unreachable.example.com/docs/llms.txt'}
        try:
            for path in ['/submit', '/redirect']:
                with patch.object(reporting, 'REPORT_URL', f'http://127.0.0.1:{server.server_port}{path}'):
                    reporting.deliver(payload)
        finally:
            server.shutdown(); server.server_close(); thread.join()
        self.assertEqual([path for path, _ in received], ['/submit', '/redirect'])
        self.assertTrue(all(body == payload for _, body in received))
        self.assertEqual(request_headers, [('llmref-skill/0.1 (+https://llmref.org)', 'application/json')] * 2)


if __name__ == '__main__':
    unittest.main()

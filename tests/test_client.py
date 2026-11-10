"""Local client contract tests; no production feedback, orders or credentials."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import urllib.error

CLIENT_PATH = Path(__file__).resolve().parents[1] / 'skills/printrelay-hardware/scripts/printrelay.py'
spec = importlib.util.spec_from_file_location('printrelay_client', CLIENT_PATH)
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
ORDER_ID = 'ord_12345678-1234-1234-1234-123456789abc'

class FeedbackClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'feedback.json'
        self.body = {'category': 'docs', 'message': 'Explain pending review.', 'consent': True, 'context_path': '/docs'}
        self.path.write_text(json.dumps(self.body))

    def run_feedback(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            client.main(['feedback', '--json-file', str(self.path), '--idempotency-key', 'saved-feedback-key'])
        return json.loads(output.getvalue())

    def test_feedback_is_public_and_preserves_body_and_key(self):
        receipt = {'feedback': {'id': 'fbk_local', 'status': 'received'}, 'replayed': False}
        with patch.object(client, 'call', return_value=receipt) as call:
            self.assertEqual(self.run_feedback(), receipt)
        args, kwargs = call.call_args
        self.assertEqual(args[:2], ('/api/feedback', 'POST'))
        self.assertEqual(json.loads(args[2]), self.body)
        self.assertEqual(kwargs, {'idem': 'saved-feedback-key', 'public': True})

    def test_invalid_feedback_never_reaches_network(self):
        cases = [
            {**self.body, 'consent': False}, {**self.body, 'category': 'spam'},
            {**self.body, 'message': ' '}, {**self.body, 'message': 'x' * 4001},
            {**self.body, 'agent_name': ''}, {**self.body, 'extra': 'value'},
            *[{**self.body, 'context_path': path} for path in ('https://other.test', '//other.test', '/docs?secret=x', '/docs#x', '/a/../b', '/./a')],
            {**self.body, 'message': 'Bearer ' + 'x' * 32},
        ]
        with patch.object(client, 'call') as call:
            for body in cases:
                with self.subTest(body=body):
                    self.path.write_text(json.dumps(body))
                    with self.assertRaises(ValueError): self.run_feedback()
            call.assert_not_called()

    def test_optional_fields_can_be_omitted(self):
        self.path.write_text(json.dumps({'category': 'other', 'message': 'One detail.', 'consent': True}))
        with patch.object(client, 'call', return_value={}) as call:
            self.run_feedback()
        self.assertNotIn('agent_name', json.loads(call.call_args.args[2]))

    def test_read_routes(self):
        with patch.object(client, 'call', return_value={}) as call, contextlib.redirect_stdout(io.StringIO()):
            client.main(['production-capabilities'])
            call.assert_called_with('/api/production-capabilities', public=True)
            client.main(['fulfillment', ORDER_ID])
            call.assert_called_with('/api/v1/orders/' + ORDER_ID + '/fulfillment', 'GET')

    def test_uncertain_request_is_not_automatically_retried(self):
        opener = unittest.mock.Mock()
        opener.open.side_effect = urllib.error.URLError('local simulated timeout')
        with patch.object(client.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(RuntimeError, 'SAME key'):
                client.call('/api/feedback', 'POST', b'{}', idem='saved-feedback-key', public=True)
        self.assertEqual(opener.open.call_count, 1)

    def test_local_http_replay_and_no_authorization_header(self):
        seen = []
        saved = {}
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                body = self.rfile.read(int(self.headers['Content-Length']))
                key = self.headers.get('Idempotency-Key')
                seen.append((self.path, dict(self.headers), body))
                replay = key in saved
                if replay and saved[key] != body:
                    self.send_response(409)
                    self.end_headers()
                    self.wfile.write(b'{"error":"conflict"}')
                    return
                saved[key] = body
                self.send_response(200 if replay else 201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'feedback': {'id': 'fbk_local', 'status': 'received'}, 'replayed': replay}).encode())
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(client, 'BASE', 'http://127.0.0.1:' + str(server.server_port)), patch.dict(os.environ, {'PRINTRELAY_API_KEY': 'test-secret-that-must-not-leave', 'PRINTRELAY_API_KEY_FILE': '/nonexistent/key'}, clear=True):
                first = self.run_feedback()
                second = self.run_feedback()
            self.assertFalse(first['replayed'])
            self.assertTrue(second['replayed'])
            self.assertEqual(first['feedback'], second['feedback'])
            self.assertEqual(seen[0][2], seen[1][2])
            for path, headers, body in seen:
                self.assertEqual(path, '/api/feedback')
                self.assertNotIn('Authorization', headers)
                self.assertEqual(headers['Idempotency-Key'], 'saved-feedback-key')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_redirect_refuses_to_forward_credentials(self):
        with self.assertRaisesRegex(RuntimeError, 'credential not forwarded'):
            client.NoRedirect().redirect_request(None, None, 307, 'redirect', {}, 'https://other.test')

class MaterialIntakeClientTests(unittest.TestCase):
    def test_current_material_families_reach_upload_unchanged_without_network(self):
        families = ('PLA', 'PETG', 'ABS', 'ASA', 'PC', 'TPU', 'PET', 'PA', 'PA6', 'PA12', 'PPA', 'PPS', 'RESIN')
        with tempfile.TemporaryDirectory() as temp:
            cad = Path(temp) / 'fixture.stl'
            cad.write_bytes(b'solid local_test\nendsolid local_test\n')
            digest = client.hashlib.sha256(cad.read_bytes()).hexdigest()
            for family in families:
                with self.subTest(material=family), patch.object(client, 'call', return_value={'file_sha256': digest}) as call, contextlib.redirect_stdout(io.StringIO()):
                    client.main(['upload', str(cad), '--email', 'qa@example.test', '--material', family, '--quantity', '1', '--units', 'mm', '--country', 'US', '--postal-code', '60601', '--idempotency-key', 'local-material-key', '--consent'])
                    self.assertEqual(call.call_args.args[:2], ('/api/v1/requests', 'POST'))
                    self.assertIn(('name="material"\r\n\r\n' + family + '\r\n').encode(), call.call_args.args[2])
                    self.assertEqual(call.call_args.args[4], 'local-material-key')
            for family in ('PVA', 'STEEL', 'resin'):
                with self.subTest(rejected_material=family), patch.object(client, 'call') as call, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    client.main(['upload', str(cad), '--email', 'qa@example.test', '--material', family, '--quantity', '1', '--units', 'mm', '--country', 'US', '--postal-code', '60601', '--idempotency-key', 'local-material-key', '--consent'])
                call.assert_not_called()

    def test_sla_null_grade_survives_private_specification_input(self):
        body = {'process': 'SLA', 'material_grade': None, 'finish': 'Supplier standard, customer approved', 'color': 'Supplier standard, customer approved', 'manufacturing_options': {'policy': 'provider_standard'}, 'required_arrival_at': None}
        request_id = 'req_12345678-1234-1234-1234-123456789abc'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'spec.json'
            path.write_text(json.dumps(body))
            with patch.object(client, 'call', return_value={}) as call, contextlib.redirect_stdout(io.StringIO()):
                client.main(['specification', request_id, '--json-file', str(path)])
            self.assertEqual(call.call_args.args[:2], ('/api/v1/requests/' + request_id + '/specification', 'PUT'))
            self.assertEqual(json.loads(call.call_args.args[2]), body)

if __name__ == '__main__': unittest.main()

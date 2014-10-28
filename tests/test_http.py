"""Test HTTP capabilities of the core's frontend."""

from ppp_core.tests import PPPTestCase
from ppp_core import app

class HttpTest(PPPTestCase(app)):
    def testPostOnly(self):
        self.assertEqual(self.app.get('/', status='*').status_int, 405)
        self.assertEqual(self.app.put('/', status='*').status_int, 405)
    def testRootOnly(self):
        self.assertEqual(self.app.post_json('/foo', {}, status='*').status_int, 404)
    def testNotJson(self):
        self.assertEqual(self.app.post('/', 'foobar', status='*').status_int, 400)
    def testWorking(self):
        pass # TODO
    def testNoTree(self):
        q = {'language': 'en'}
        self.assertStatusInt(q, 400)

import sqlite3

import tempfile
from ppp_logger import app
from ppp_libmodule.tests import PPPTestCase


class HttpTest(PPPTestCase(app)):
    config_var = 'PPP_LOGGER_CONFIG'
    def setUp(self):
        self.fd = tempfile.NamedTemporaryFile('w+')
        self.config = '{"database_url": "sqlite:///%s"}' % self.fd.name
        super(HttpTest, self).setUp()
    def tearDown(self):
        super(HttpTest, self).tearDown()
        self.fd.close()
    def testInvalidMethod(self):
        self.assertEqual(self.app.put('/', status='*').status_int, 405)
    def testNotJson(self):
        self.assertEqual(self.app.post('/', 'foobar', status='*').status_int, 400)
    def testWorking(self):
        tree = {'type': 'missing'}
        q = {'id': 'foo', 'question': '42?',
             'responses': [{'tree': tree, 'measures': {}, 'trace': []}]}
        self.assertStatusInt(q, 200)
        conn = sqlite3.connect(self.fd.name)
        with conn:
            r = conn.execute('SELECT request_id, ppp_request_id, request_question FROM requests;')
            self.assertEqual(r.fetchall(), [(1, 'foo', '42?')])
    def testMissingAttribute(self):
        q = {'question': '42?', 'responses': []}
        self.assertStatusInt(q, 400)
    def testBadAttributeType(self):
        q = {'id': 5, 'question': '42?', 'responses': []}
        self.assertStatusInt(q, 400)
    def testMissingResponseAttribute(self):
        q = {'id': 'foo', 'question': '42?', 'responses': [{}]}
        self.assertStatusInt(q, 400)
    def testSentenceResponse(self):
        tree = 'forty-two?'
        q = {'id': 'foo', 'question': '42?',
             'responses': [{'tree': tree, 'measures': {}, 'trace': []}]}
        self.assertStatusInt(q, 200)
    def testBadResponseAttributeType(self):
        tree = []
        q = {'id': 'foo', 'question': '42?',
             'responses': [{'tree': tree, 'measures': {}, 'trace': []}]}
        self.assertStatusInt(q, 400)

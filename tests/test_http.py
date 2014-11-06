"""Test HTTP capabilities of the core's frontend."""

import sqlite3

from ppp_logger.tests import PPPLoggerTestCase

class HttpTest(PPPLoggerTestCase):
    def testPostOnly(self):
        self.assertEqual(self.app.get('/', status='*').status_int, 405)
        self.assertEqual(self.app.put('/', status='*').status_int, 405)
    def testNotJson(self):
        self.assertEqual(self.app.post('/', 'foobar', status='*').status_int, 400)
    def testWorking(self):
        tree = {'type': 'missing'}
        q = {'id': 'foo', 'question': '42?',
             'responses': [{'tree': tree, 'measures': {}, 'trace': []}]}
        self.request(q)
        conn = sqlite3.connect(self.db_file.name)
        with conn:
            r = conn.execute('SELECT * FROM requests;')
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
             'responses': [{'tree': tree, 'measures': {}}]}
        self.assertStatusInt(q, 400)

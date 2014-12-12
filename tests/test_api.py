
import sqlite3

import json
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
    def testEmpty(self):
        r = self.app.get('/')
        self.assertEqual(r.content_type, 'application/json')
        r = json.loads(r.body.decode())
        self.assertEqual(r, [])
    def testNotEmpty(self):
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        r = self.app.get('/')
        self.assertEqual(r.content_type, 'application/json')
        r = json.loads(r.body.decode())
        self.assertEqual(len(r), 2, r)
        self.assertEqual(r[0][0], 'Baz qux?')
        self.assertEqual(r[1][0], 'Foo bar?')

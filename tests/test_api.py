
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

    def testLast(self):
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
    def testLimitLast(self):
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        r = self.app.get('/', params={'limit': 1})
        self.assertEqual(r.content_type, 'application/json')
        r = json.loads(r.body.decode())
        self.assertEqual(len(r), 1, r)
        self.assertEqual(r[0][0], 'Baz qux?')

    def testTop(self):
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'quux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        r = self.app.get('/', {'order': 'top'})
        self.assertEqual(r.content_type, 'application/json')
        r = json.loads(r.body.decode())
        self.assertEqual(len(r), 3, r)
        self.assertEqual(r[0][0], 'Baz qux?', r)
        self.assertEqual(r[1][0], 'Foo bar?', r)
        self.assertEqual(r[2][0], 'quux?', r)

    """
    def testTopAmong(self):
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Baz qux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'quux?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        q = {'id': 'foo', 'question': 'Foo bar?', 'responses': []}
        self.assertStatusInt(q, 200)
        r = self.app.get('/', {'order': 'top', 'among': 6})
        self.assertEqual(r.content_type, 'application/json')
        r = json.loads(r.body.decode())
        self.assertEqual(len(r), 3, r)
        self.assertEqual(r[0][0], 'Foo bar?', r)
        self.assertEqual(r[1][0], 'Baz qux?', r)
        self.assertEqual(r[2][0], 'quux?', r)
        """

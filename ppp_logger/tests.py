import os
import json
import tempfile
from webtest import TestApp
from unittest import TestCase
from ppp_logger import app

base_config = '{"database_url": "sqlite:///%s"}'

class PPPLoggerTestCase(TestCase):
    def setUp(self):
        super(PPPLoggerTestCase, self).setUp()
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        self.db_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_LOGGER_CONFIG'] = self.config_file.name
        self.config_file.write(base_config % self.db_file.name)
        self.config_file.seek(0)
    def tearDown(self):
        self.config_file.close()
        del os.environ['PPP_LOGGER_CONFIG']
        del self.config_file
        del self.db_file
        super(PPPLoggerTestCase, self).tearDown()

    def request(self, obj):
        if isinstance(obj, str):
            obj = json.loads(obj)
        return self.app.post_json('/', obj).json
    def assertResponse(self, request, response):
        self.assertEqual(self.request(request), response)
    def assertStatusInt(self, request, status):
        res = self.app.post_json('/', request, status='*')
        self.assertEqual(res.status_int, status)

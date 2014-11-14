"""Tests what happens if the config file is invalid."""

import os
import tempfile
from ppp_logger import app
from webtest import TestApp
from unittest import TestCase
from ppp_libmodule.exceptions import InvalidConfig


class NoConfFileTestCase(TestCase):
    def testNoConfFile(self):
        self.app = TestApp(app)
        obj = {'id': 'foobar', 'question': '42?', 'responses': []}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

class InvalidConfFileTestCase(TestCase):
    def setUp(self):
        super(InvalidConfFileTestCase, self).setUp()
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_LOGGER_CONFIG'] = self.config_file.name
    def tearDown(self):
        del os.environ['PPP_LOGGER_CONFIG']
        self.config_file.close()
        del self.config_file
        super(InvalidConfFileTestCase, self).tearDown()
    def testEmptyConfFile(self):
        obj = {'id': 'foobar', 'question': '42?', 'responses': []}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

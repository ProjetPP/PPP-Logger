"""Test HTTP capabilities of the logger."""

import json
import sqlite3
import tempfile

from ppp_logger.logger import make_responses_forest, freeze
from ppp_logger import app
from ppp_libmodule.tests import PPPTestCase

R = lambda x:{'type': 'resource', 'value': x}
def to_trace(x): # Copy object and remove trace
    y = x.copy() # Shallow copy
    y['module'] = str(len(y['tree']['value']))
    del y['trace']
    return y
def striptraces(obj):
    if isinstance(obj, list):
        return list(map(striptraces, obj))
    elif isinstance(obj, dict):
        return {x:striptraces(y) for (x,y) in obj.items() if x != 'trace'}
    elif isinstance(obj, tuple):
        return tuple(map(striptraces, obj))
    else:
        return obj
m = lambda x:{'tree': R(x), 'measures': {}}

def build_responses():
    """
    one
    +- two
    |  +- three
    |  |  +- four
    |  +- five
    +- six
    |  +- seven
    eight
    nine
    """
    one   = {'tree': R('one'),   'measures': {}, 'trace': []}
    two   = {'tree': R('two'),   'measures': {}, 'trace': [to_trace(one)]}
    three = {'tree': R('three'), 'measures': {}, 'trace': [to_trace(one), to_trace(two)]}
    four  = {'tree': R('four'),  'measures': {}, 'trace': [to_trace(one), to_trace(two), to_trace(three)]}
    five  = {'tree': R('five'),  'measures': {}, 'trace': [to_trace(one), to_trace(two)]}
    six   = {'tree': R('six'),   'measures': {}, 'trace': [to_trace(one)]}
    seven = {'tree': R('seven'), 'measures': {}, 'trace': [to_trace(one), to_trace(six)]}
    eight = {'tree': R('eight'), 'measures': {}, 'trace': []}
    nine  = {'tree': R('nine'),  'measures': {}, 'trace': []}
    L = [one, two, three, four, five, six, seven, eight, nine]
    for x in L:
        x['trace'].append({'tree': x['tree'], 'measures': x['measures'],
                           'module': str(len(x['tree']['value']))})
    return L

def notrace(obj):
    if isinstance(obj, list) or isinstance(obj, tuple):
        return all(map(notrace, obj))
    elif isinstance(obj, dict):
        return 'trace' not in obj and all(map(notrace, obj))
    else:
        return True

class LoggerTest(PPPTestCase(app)):
    config_var = 'PPP_LOGGER_CONFIG'
    def setUp(self):
        self.fd = tempfile.NamedTemporaryFile('w+')
        self.config = '{"database_url": "sqlite:///%s"}' % self.fd.name
        super(LoggerTest, self).setUp()
    def tearDown(self):
        super(LoggerTest, self).tearDown()
        self.fd.close()
    def testTree(self):
        # Only the last assertEqual would be enough, actually.
        # But the previous assertions makes it easier to debug (more precise
        # informations on was is going wrong).
        tree = make_responses_forest(build_responses())
        tree = striptraces(tree)
        self.assertTrue(notrace(tree), tree)
        self.assertEqual(len(tree), 3, [x['tree']['value'] for (x,y) in tree])
        self.assertEqual(tree, [
            (m('one'), [
                (m('two'), [
                    (m('three'), [
                        (m('four'), [
                        ]),
                    ]),
                    (m('five'), [
                    ]),
                ]),
                (m('six'), [
                    (m('seven'), [
                    ]),
                ]),
            ]),
            (m('eight'), [
            ]),
            (m('nine'), [
            ]),
        ])

    def testLog(self):
        question = 'question?'
        responses = build_responses()
        q = {'id': 'foo', 'question': question,
             'responses': responses}
        self.assertStatusInt(q, 200)
        conn = sqlite3.connect(self.fd.name)
        with conn:
            r = conn.execute('SELECT response_id, parent_response_id, response_tree FROM responses;').fetchall()
            fields = ('id', 'parent', 'tree')
            zipper = lambda x:dict(zip(fields, x))
            r = list(map(zipper, r))
            for x in r:
                if json.loads(x['tree'])['value'] in ('three', 'five'):
                    self.assertNotEqual(x['parent'], None)
                    parent = json.loads(r[x['parent']])
                    self.assertEqual(parent['tree']['value'], 'two')

    def testTraceItemMissingFromResponses(self):
        # This was a bug caused by the WebUI putting the input in the trace
        # without putting it as a response
        i = r'''{"id":"1417024784682-682-12-webui","question":"sqrt(2)","responses":[{"measures":{"accuracy":0.5,"relevance":0.1},"trace":[{"measures":{"accuracy":1,"relevance":0},"module":"input","tree":{"type":"sentence","value":"sqrt(2)"}},{"measures":{"accuracy":0.5,"relevance":0.1},"module":"spell-checker","tree":{"value":"sq rt 2","type":"sentence"}}],"tree":{"value":"sq rt 2","type":"sentence"},"language":"en"}]}'''
        q = json.loads(i)
        self.assertStatusInt(q, 200)

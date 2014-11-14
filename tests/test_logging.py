"""Test HTTP capabilities of the logger."""

import json
import sqlite3

from ppp_logger.logger import make_responses_forest, freeze
from ppp_logger.tests import PPPLoggerTestCase

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

class LoggerTest(PPPLoggerTestCase):
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
        conn = sqlite3.connect(self.db_file.name)
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

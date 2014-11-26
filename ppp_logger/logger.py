import json
import datetime

from . import model
from .config import Config

from ppp_libmodule.exceptions import ClientError

TOPLEVEL_ATTRIBUTES_TYPES = {'id': str,
                             'question': str,
                             'responses': list,
                            }
RESPONSE_ATTRIBUTES_TYPES = {'tree': (dict, str),
                             'measures': dict,
                             'trace': list,
                            }

def freeze(obj):
    # Makes the object suitable for being a dictionnary key.
    if isinstance(obj, list) or isinstance(obj, tuple):
        return tuple(map(freeze, obj))
    elif isinstance(obj, dict):
        return frozenset((x,freeze(y)) for (x,y) in obj.items())
    else:
        return obj

def make_responses_forest(responses):
    parents = {} # Used to insert childs
    tree = [] # The actual tree
    # Make the earliest responses come first
    responses = sorted(responses,
                       key=lambda x:len(x['trace']))
    for response in responses:
        if len(response['trace']) > 1:
            # Build a lookup key for the “parents” dict
            parent = response['trace'][-2]
            parent = parent.copy()
            parent['trace'] = response['trace'][0:-1]
            del parent['module']
            location = parents.get(freeze(parent), tree)
        else:
            location = tree

        # Insert
        childs = []
        location.append((response, childs))
        parents[freeze(response)] = childs
    return tree

class Logger:
    def __init__(self, request):
        self._check_request(request)
        self.request = request
        self.config = Config()

    def _check_request(self, request):
        if not set(TOPLEVEL_ATTRIBUTES_TYPES).issubset(request):
            raise ClientError('Toplevel missing one required attribute.')
        if not all(isinstance(request[x], y)
                   for x, y in TOPLEVEL_ATTRIBUTES_TYPES.items()):
            raise ClientError('One toplevel attribute does not have the '
                              'right type.')
        list(map(self._check_response, request['responses']))
    def _check_response(self, response):
        if not set(RESPONSE_ATTRIBUTES_TYPES).issubset(response):
            raise ClientError('Response missing one required attribute.')
        if not all(isinstance(response[x], y)
                   for x, y in RESPONSE_ATTRIBUTES_TYPES.items()):
            raise ClientError('One response attribute does not have the '
                              'right type.')

    def answer(self):
        conn = model.get_engine(self.config.database_url).connect()
        pk = self.insert_request(conn)
        forest = make_responses_forest(self.request['responses'])
        for tree in forest:
            self.insert_tree(pk, None, tree)

    def insert_request(self, conn):
        ins = model.requests.insert().values(
                ppp_request_id=self.request['id'],
                request_question=self.request['question'],
                request_datetime=datetime.datetime.now())
        res = conn.execute(ins)
        return res.inserted_primary_key[0]

    def insert_tree(self, request_id, parent, tree):
        assert isinstance(tree, tuple), tree
        # TODO: optimize this function by running insertion in batches
        # (layer after layer)
        pk = self.insert_response(request_id, parent, tree[0])
        for subtree in tree[1]:
            self.insert_tree(request_id, pk, subtree)

    def insert_response(self, request_id, parent, response):
        if response['trace']:
            module = response['trace'][-1]['module']
        else:
            module = 'unknown'
        ins = model.responses.insert().values(
                request_id=request_id,
                parent_response_id=parent,
                response_is_final_result=True, # TODO
                response_module=module,
                response_tree=json.dumps(response['tree']),
                response_language=response.get('language', 'unknown'),
                response_measures=json.dumps(response['measures']),
                )

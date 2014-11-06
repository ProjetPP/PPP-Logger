
from . import model
from .config import Config

from ppp_core.exceptions import ClientError

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
def striptraces(obj):
    if isinstance(obj, list):
        return list(map(striptraces, obj))
    elif isinstance(obj, dict):
        return {x:striptraces(y) for (x,y) in obj.items() if x != 'trace'}
    elif isinstance(obj, tuple):
        return tuple(map(striptraces, obj))
    else:
        return obj

def make_responses_tree(responses):
    parents = {} # Used to insert childs
    tree = [] # The actual tree
    # Make the earliest responses come first
    responses = sorted(responses,
                       key=lambda x:len(x['trace']))
    for response in responses:
        if response['trace']:
            # Build a lookup key for the “parents” dict
            parent = response['trace'][-1]
            parent = parent.copy()
            parent['trace'] = response['trace'][0:-1]
            location = parents[freeze(parent)]
        else:
            location = tree

        # Insert
        childs = []
        location.append((response, childs))
        parents[freeze(response)] = childs
    return striptraces(tree)

class Logger:
    def __init__(self, request):
        self._check_request(request)
        self.request = request
        self.config = Config()

    def _check_request(self, request):
        if set(request) != set(TOPLEVEL_ATTRIBUTES_TYPES):
            raise ClientError('Toplevel missing one required attribute.')
        if not all(isinstance(request[x], y)
                   for x, y in TOPLEVEL_ATTRIBUTES_TYPES.items()):
            raise ClientError('One toplevel attribute does not have the '
                              'right type.')
        list(map(self._check_response, request['responses']))
    def _check_response(self, response):
        if set(response) != set(RESPONSE_ATTRIBUTES_TYPES):
            raise ClientError('Response missing one required attribute.')
        if not all(isinstance(response[x], y)
                   for x, y in RESPONSE_ATTRIBUTES_TYPES.items()):
            raise ClientError('One response attribute does not have the '
                              'right type.')

    def answer(self):
        conn = model.get_engine(self.config.database_url).connect()
        pk = self.insert_in_requests(conn)
        tree = make_responses_tree(self.request['responses'])
        self.insert_tree(tree, None)

    def insert_in_requests(self, conn):
        ins = model.requests.insert().values(
                ppp_request_id=self.request['id'],
                request_question=self.request['question'])
        res = conn.execute(ins)
        return res.inserted_primary_key[0]

    def insert_tree(self, tree, parent):
        pass

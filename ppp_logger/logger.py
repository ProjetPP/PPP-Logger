
from . import model
from .config import Config

from ppp_core.exceptions import ClientError

TOPLEVEL_ATTRIBUTES_TYPES = {'id': str,
                             'question': str,
                             'responses': list,
                            }
RESPONSE_ATTRIBUTES_TYPES = {'tree': (dict, str),
                             'measures': dict,
                            }

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

    def insert_in_requests(self, conn):
        ins = model.requests.insert().values(
                ppp_request_id=self.request['id'],
                request_question=self.request['question'])
        res = conn.execute(ins)
        return res.inserted_primary_key[0]

"""Handles the HTTP frontend (ie. answers to requests from a
UI)."""

import cgi
import json
import logging

from ppp_libmodule import HttpRequestHandler as HttpRequestHandler
from ppp_libmodule.exceptions import ClientError, InvalidConfig

from .api import Api
from .logger import Logger

DOC_URL = 'https://github.com/ProjetPP/PPP-Logger#readme'

class RequestHandler(HttpRequestHandler):
    """Handles one request."""

    def on_bad_method(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'Bad method, only POST is supported. See: ' + DOC_URL
        return self.make_response('405 Method Not Allowed',
                                  'text/plain; charset=utf-8',
                                  text
                                 )

    def on_unknown_uri(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'URI not found, only / is supported. See: ' + DOC_URL
        return self.make_response('404 Not Found',
                                  'text/plain; charset=utf-8',
                                  text
                                 )

    def process_request(self, request):
        """Processes a request."""
        try:
            request = json.loads(request.read().decode())
        except ValueError:
            raise ClientError('Data is not valid JSON.')
        answer = self.router_class(request).answer()
        return self.make_response('200 OK',
                                  'application/json',
                                  json.dumps(answer)
                                 )

    def on_get(self):
        form = cgi.FieldStorage(fp=self.environ['wsgi.input'],
                                environ=self.environ.copy())
        try:
            answer = Api(form).answer()
        except ClientError as e:
            return self.make_response('405 Client Error',
                                      'text/plain; charset=utf-8',
                                      e.args[0])
        return self.make_response('200 OK',
                                  'application/json',
                                  json.dumps(answer))


def app(environ, start_response):
    """Function called by the WSGI server."""
    return RequestHandler(environ, start_response, Logger).dispatch()

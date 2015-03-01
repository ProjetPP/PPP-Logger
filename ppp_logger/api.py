from sqlalchemy import desc, func
from sqlalchemy.sql import select

from . import model
from .model import requests
from .config import Config

from ppp_libmodule.exceptions import ClientError

class Api:
    def __init__(self, form):
        self.form = form
        self.config = Config()
        self.extract_form()
        self.validate_form()

    def extract_form(self):
        # https://docs.python.org/3/library/cgi.html#cgi.FieldStorage.getfirst
        self.limit = int(self.form.getfirst('limit', 10))
        self.offset = int(self.form.getfirst('offset', 0))
        self.order = self.form.getfirst('order', 'last')

    def validate_form(self):
        if self.limit > 10000:
            raise ClientError('“limit” is too big (> 10000).')
        if self.order not in ('last', 'top', 'first'):
            raise ClientError('Only orders “first”, “last” and “top” are allowed')

    def get_selector_first(self):
        s = select([requests.c.request_question, requests.c.request_datetime]) \
                .order_by(requests.c.request_datetime) \
                .offset(self.offset) \
                .limit(self.limit)
        return (s, lambda x:(x[0], str(x[1])))

    def get_selector_last(self):
        s = select([requests.c.request_question, requests.c.request_datetime]) \
                .order_by(desc(requests.c.request_datetime)) \
                .offset(self.offset) \
                .limit(self.limit)
        return (s, lambda x:(x[0], str(x[1])))

    def get_selector_top(self):
        s = select([requests.c.request_question.label('question'),
                    func.count(requests.c.request_question).label('num')]) \
                .order_by(desc('num')) \
                .group_by(requests.c.request_question) \
                .offset(self.offset) \
                .limit(self.limit)
        return (s, lambda x:(x[0], x[1]))

    def answer(self):
        method = getattr(self, 'get_selector_' + self.order)
        conn = model.get_engine(self.config.database_url).connect()
        (selector, to_serializable) = method()
        return list(map(to_serializable, conn.execute(selector).fetchall()))

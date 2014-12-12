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
        self.order = self.form.getfirst('order', 'last')
        self.among = int(self.form.getfirst('among', 0))

    def validate_form(self):
        if self.limit > 1000:
            raise ClientError('“limit” is too big (> 1000).')
        if self.order not in ('last', 'top'):
            raise ClientError('Only orders “last” and “top” are allowed')
        if self.among and self.order != 'top':
            raise ClientError('“among” is only allowed with “top” order.')

    def get_selector_last(self):
        s = select([requests.c.request_question, requests.c.request_datetime]) \
                .order_by(desc(requests.c.request_datetime)) \
                .limit(self.limit)
        return (s, lambda x:(x[0], str(x[1])))

    def get_selector_top(self):
        s = select([requests.c.request_question,
                    func.count(requests.c.request_question).label('num')])
        if self.among:
            s = s \
                    .order_by(desc(requests.c.request_datetime)) \
                    .limit(self.among)
        s = s \
                .group_by(requests.c.request_question) \
                .order_by(desc('num')) \
                .limit(self.limit)
        return (s, lambda x:(x[0], x[1]))

    def answer(self):
        method = getattr(self, 'get_selector_' + self.order)
        conn = model.get_engine(self.config.database_url).connect()
        (selector, to_serializable) = method()
        return list(map(to_serializable, conn.execute(selector).fetchall()))

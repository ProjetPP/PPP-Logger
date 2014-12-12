from sqlalchemy import desc
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

    def extract_form(self):
        # https://docs.python.org/3/library/cgi.html#cgi.FieldStorage.getfirst
        self.limit = self.form.getfirst('limit', 10)
        if self.limit > 1000:
            raise ClientError('Limit is too big (> 1000).')

    def answer(self):
        s = select([requests.c.request_question, requests.c.request_datetime]) \
                .order_by(desc(requests.c.request_datetime)) \
                .limit(self.limit)
        to_serializable = lambda x:(x[0], str(x[1]))
        conn = model.get_engine(self.config.database_url).connect()
        return list(map(to_serializable, conn.execute(s).fetchall()))

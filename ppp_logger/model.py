from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy import MetaData, ForeignKey

from .config import Config

metadata = MetaData()

requests = Table('requests', metadata,
                 Column('request_id', Integer, primary_key=True),
                 Column('ppp_request_id', String),
                 Column('request_question', Text)
                )

responses = Table('responses', metadata,
                  Column('response_id', Integer, primary_key=True),
                  Column('request_id', None, ForeignKey('requests.request_id')),
                  Column('parent_response_id', None, ForeignKey('responses.response_id'), nullable=True),
                  Column('response_is_final_result', Boolean),
                  Column('response_module', String),
                  Column('response_tree', Text),
                  Column('response_language', String),
                  Column('response_measures', Text),
                 )

feedback = Table('feedback', metadata,
                 Column('feedback_id', Integer, primary_key=True),
                 Column('request_id', None, ForeignKey('requests.request_id')),
                 Column('response_is_good', Boolean),
                 Column('response_correction', Text),
                )

def get_engine(uri):
    """Asks SQLAlchemy to create an engine to connect to the URI and return it."""
    engine = create_engine(uri, echo=Config().debug)
    metadata.create_all(engine)
    return engine

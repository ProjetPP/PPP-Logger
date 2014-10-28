import os
import json

from ppp_core.exceptions import InvalidConfig

class Config:
    __slots__ = ('debug', 'database_url')
    def __init__(self, data=None):
        self.debug = True
        if not data:
            try:
                with open(self.get_config_path()) as fd:
                    data = json.load(fd)
            except ValueError as exc:
                raise InvalidConfig(*exc.args)
        self.debug = data.get('debug', False)
        self.database_url = data['database_url']

    @staticmethod
    def get_config_path():
        path = os.environ.get('PPP_LOGGER_CONFIG', '')
        if not path:
            raise InvalidConfig('Could not find config file, please set '
                                'environment variable $PPP_LOGGER_CONFIG.')
        return path

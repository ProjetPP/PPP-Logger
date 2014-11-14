import os
import json

from ppp_libmodule.config import Config as BaseConfig
from ppp_libmodule.exceptions import InvalidConfig

class Config(BaseConfig):
    __slots__ = ('debug', 'database_url')
    config_path_variable = 'PPP_LOGGER_CONFIG'

    def parse_config(self, data):
        self.debug = data.get('debug', False)
        self.database_url = data['database_url']

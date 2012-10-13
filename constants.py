"""
constant.Constants - The simple way to deal with environment constants.
"""

import os
import ConfigParser
import warnings
import logging
import functools


logger = logging.getLogger(__name__)

def debug(function):
    """
    logging debug decorator
    """
    @functools.wraps(function)
    def wrapper(*args, **kvargs):
        logger.debug('begin', extra={'method': function.__name__})
        result = function(*args, **kvargs)
        logger.debug('end', extra={'method': function.__name__})
        return result
    return wrapper

VARIABLE = '__CONSTANTS__'
FILENAME = 'constants.ini'

class Constants(object):

    @debug
    def __init__(self, variable=VARIABLE, filename=FILENAME):
        """
        variable is the name of the environment variable to read the
        environment / config section from default to __CONSTANTS__
        filename is the config filename
        """
        self.variable = variable
        self.filename = filename
        self.load()

    @debug
    def load(self):
        """
        load the section self.variable from the config file self.filename
        """
        self.get_environment()
        self.read_config()
        self.load_dict()

    @debug
    def get_environment(self):
        """
        returns the value of the environment variable self.variable
        """
        self.environment = os.environ[self.variable]

    @debug
    def read_config(self):
        """
        returns a ConfigParser instance from self.filename
        """
        self.config = ConfigParser.ConfigParser()
        with open(self.filename) as f:
            self.config.readfp(f)

    @debug
    def load_dict(self):
        """
        load the config items into self.dict
        """
        self.dict = dict (self.config.items(self.environment))
        logger.info('variable: %s, filename: %s, environment: %s, constants: %s',
                    self.variable,
                    self.filename,
                    self.environment,
                    self.dict,
                    extra={'method': 'load'})

    def __getitem__(self, item):
        """
        access to environment specific constants in a dictionary manner
        casts to int, float or keep as string
        """
        return self.cast(self.dict[item])

    def __getattr__(self, item):
        """
        syntactic sugar, .item rather than ['item']
        """
        return self[item]

    @staticmethod
    def cast(string):
        """
        cast string to int, float or keep as string

        >>> Constants.cast('1')
        1
        >>> Constants.cast('3.14')
        3.14
        >>> Constants.cast('a_string')
        'a_string'
        """
        try:
            return int(string)
        except ValueError:
            pass
        try:
            return float(string)
        except ValueError:
            pass
        return string

    def __setitem__(self, item, value):
        """
        dict like assignment - warns when a constant is changed
        """
        if item in self.dict:
            warnings.warn('{} changed to {}'.format(item, value))
        self.dict[item] = value

    def __setattr__(self, name, value):
        """
        attribute assignment - warns when a constant is changed
        """
        if hasattr(self, 'dict') and name in self.dict:
            warnings.warn('{} changed to {}'.format(name, value))
            self.dict[name] = value
        else:
            object.__setattr__(self, name, value)


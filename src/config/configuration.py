"""
Implementation of the configuration housekeeping.
"""
import logging
import json
from pathlib import Path
from typing import Collection, Type

from jsonschema import validate

LOGGER = logging.Logger(__name__)


class ConfigurationError(Exception):
    """
    Super class for configuration Errors.
    """


class ImmutableError(ConfigurationError, NameError):
    """
    Error for attempt to change immutable Data.
    """


class SetupFirstError(ConfigurationError, ValueError):
    """
    Error if trying to access data before setup has been called.
    """


class Config:
    """
    Actual configuration Class.
    """

    __config: dict
    __schema: dict
    __immutable: Collection

    @classmethod
    def setup(cls, config_location: Path, validation_schema_location: Path = None,
              immutable: Collection = None):
        """
        Setup of the configuration, defining type of configuration to store and mutability.
        todo
        """
        # todo: why does this error? im confused!
        # if cls.__config:
        #     LOGGER.warning('Config already exists - overwriting old one...')
        cls.__immutable = immutable or []
        try:
            with open(config_location, mode='r') as configuration:
                configuration_data = json.load(configuration)
            if validation_schema_location:
                with open(validation_schema_location, mode='r') as schema:
                    cls.__schema = json.load(schema)
                    validate(instance=configuration_data, schema=cls.__schema)
            cls.__config = configuration_data

        except (KeyError, json.JSONDecodeError) as error:
            LOGGER.error('Could not parse config file \'%s\'')
            LOGGER.error('Check if it is formatted correctly!')
            raise ConfigurationError from error
        except OSError as error:
            LOGGER.error('Could not open schema or configuration.')
            LOGGER.error('Please ensure they exist and you have the appropriate read rights.')
            raise error

    @classmethod
    def get(cls, name: str):
        """
        Access to the configuration.
        todo
        """
        try:
            return cls.__config[name]  # type: ignore # https://github.com/python/mypy/issues/7178
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except TypeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

    @classmethod
    def set(cls, name: str, value):
        """
        Change the configuration for mutable values.
        Raises ImmutableError if value is immutable.
        todo
        """
        try:
            if name in cls.__immutable:  # type: ignore # https://github.com/python/mypy/issues/7178
                LOGGER.error('Cannot change value of config variable %s as it is immutable!', name)
                raise ImmutableError
            cls.__config[name] = value
            if cls.__schema:
                validate(instance=cls.__config, schema=cls.__schema)
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except TypeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

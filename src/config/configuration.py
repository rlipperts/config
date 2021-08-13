"""
Implementation of the configuration housekeeping.
"""
import logging
import json
from pathlib import Path
from typing import Collection, Optional

import jsonschema.exceptions  # type: ignore
from jsonschema import validate  # type: ignore

from config.exceptions import ImmutableError, SetupFirstError, ConfigExistsError, \
    ConfigDecodeError, ConfigValidationError

LOGGER = logging.Logger(__name__)


class Config:
    """
    Actual configuration Class.
    """

    __config: dict
    __schema: dict
    __immutable: Collection

    @classmethod
    # see https://github.com/PyCQA/pylint/issues/4644
    # pylint: disable=unused-private-member
    def __validate(cls):
        if cls.__schema:
            try:
                validate(instance=cls.__config, schema=cls.__schema)
            except jsonschema.exceptions.ValidationError as error:
                LOGGER.error('Configuration validation failed!')
                raise ConfigValidationError() from error

    @classmethod
    def setup(cls, config_location: Path, validation_schema_location: Optional[Path] = None,
              immutable: Optional[Collection] = None):
        """
        Setup of the configuration, defining type of configuration to store and mutability.
        :param config_location: Path to the configuration JSON file
        :param validation_schema_location: Path to the JSON schema to validate the file with
        :param immutable: Configuration keys whose values are immutable
        """
        if hasattr(cls, '_Config__config'):
            LOGGER.error('Config already exists!')
            LOGGER.error(
                'If you really want to setup a different config, call Config.reset() first!')
            raise ConfigExistsError
        cls.__immutable = immutable or []
        try:
            with open(config_location, mode='r') as configuration:
                configuration_data = json.load(configuration)
            if validation_schema_location:
                with open(validation_schema_location, mode='r') as schema:
                    cls.__schema = json.load(schema)
            else:
                cls.__schema = {}
            cls.__config = configuration_data
            cls.__validate()

        except (KeyError, json.JSONDecodeError) as error:
            LOGGER.error('Could not parse config file \'%s\'')
            LOGGER.error('Check if it is formatted correctly!')
            raise ConfigDecodeError from error
        except OSError as error:
            LOGGER.error('Could not open schema or configuration.')
            LOGGER.error('Please ensure they exist and you have the appropriate read rights.')
            raise error

    @classmethod
    def get(cls, name: str):
        """
        Access to the configuration.
        :param name: Name of the configuration variable to read
        :return: Value of the requested configuration variable
        """
        try:
            return cls.__config[name]  # type: ignore # https://github.com/python/mypy/issues/7178
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except AttributeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

    @classmethod
    def set(cls, name: str, value):
        """
        Change the configuration for mutable values.
        Raises ImmutableError if value is immutable.
        :param name: Name of the configuration variable to change
        :param value: New value for the configuration variable
        """
        try:
            if name in cls.__immutable:  # type: ignore # https://github.com/python/mypy/issues/7178
                LOGGER.error('Cannot change value of config variable %s as it is immutable!', name)
                raise ImmutableError
            cls.__config[name] = value
            cls.__validate()
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except AttributeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

    @classmethod
    def reset(cls):
        """
        Resets the class so it can be setup again.
        """
        try:
            del cls.__config
            del cls.__schema
            del cls.__immutable
        except AttributeError:
            LOGGER.warning('Unnecessary reset call - nothing to reset here.')

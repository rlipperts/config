"""
Implementation of the configuration housekeeping.
"""
import logging
from pathlib import Path
from typing import TypedDict, Container, Type

from template_loader import loader

LOGGER = logging.Logger(__name__)
ENVIRONMENT_VAR_NAME = 'ROUTING_CONFIG_LOCATION'
CONFIG_LOCATION = Path.cwd() / 'data/frontend_dummy/configuration.json'


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

    __config: TypedDict  # type: ignore # there is no way to specify we want a subclass here, right?
    __immutable: Container

    @classmethod
    # see above
    def setup(cls, config_storage_class: Type[TypedDict], immutable: Container,  # type: ignore
              config_location: Path):
        """
        Setup of the configuration, defining type of configuration to store and mutability.
        todo
        """
        cls.__immutable = immutable
        try:
            # see above
            cls.__config = config_storage_class(loader.load_dict(config_location))  # type: ignore
        except (KeyError, loader.BadFormatError) as error:
            LOGGER.error('Could not parse config file \'%s\'')
            LOGGER.error('Check if it is formatted correctly!')
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
            cls.__config[name] = value  # type: ignore # specify subclass?
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except TypeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

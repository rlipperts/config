"""
Implementation of the configuration housekeeping.
"""
import argparse
import distutils.util
import hashlib
import logging
import json
import sys
import typing
from pathlib import Path
from typing import Collection, Optional

import jsonschema.exceptions
from jsonschema import validate

from static_config_class.exceptions import ImmutableError, SetupFirstError, ConfigExistsError, \
    ConfigDecodeError, ConfigValidationError

LOGGER = logging.Logger(__name__)
PrimitiveTypes = typing.Union[str, bool, int, float]
SupportedTypes = typing.Union[PrimitiveTypes, list[PrimitiveTypes], dict[str, PrimitiveTypes]]


class Config:
    """
    Actual configuration Class.
    """

    __config: dict  # type: ignore
    __schema: dict  # type: ignore
    __immutable: Collection[str]

    @classmethod
    # see https://github.com/PyCQA/pylint/issues/4644
    # pylint: disable=unused-private-member
    def __validate(cls) -> None:
        if cls.__schema:
            try:
                validate(instance=cls.__config, schema=cls.__schema)
            except jsonschema.exceptions.ValidationError as error:
                LOGGER.error('Configuration validation failed!')
                raise ConfigValidationError() from error

    @classmethod
    def setup(cls, config_location: Path, validation_schema_location: Optional[Path] = None,
              immutable: Optional[Collection[str]] = None, allow_cmdline_override: bool = True) \
            -> None:
        """
        Setup of the configuration, defining type of configuration to store and mutability.
        :param config_location: Path to the configuration JSON file
        :param validation_schema_location: Path to the JSON schema to validate the file with
        :param immutable: Configuration keys whose values are immutable
        :param allow_cmdline_override: Allows overriding static_config_class file options with commandline
        arguments of same name
        """
        if hasattr(cls, '_Config__config'):
            LOGGER.error('Config already exists!')
            LOGGER.error(
                'If you really want to setup a different static_config_class, call Config.reset() first!')
            raise ConfigExistsError
        cls.__immutable = immutable or []
        try:
            with open(config_location, mode='r', encoding='utf8') as configuration:
                configuration_data = json.load(configuration)
            if validation_schema_location:
                with open(validation_schema_location, mode='r', encoding='utf8') as schema:
                    cls.__schema = json.load(schema)
            else:
                cls.__schema = {}
            cls.__config = configuration_data
            if allow_cmdline_override:
                cls.__apply_cmdline_overrides(sys.argv[1:])
            cls.__validate()

        except (KeyError, json.JSONDecodeError) as error:
            LOGGER.error('Could not parse static_config_class file \'%s\'')
            LOGGER.error('Check if it is formatted correctly!')
            raise ConfigDecodeError from error
        except OSError as error:
            LOGGER.error('Could not open schema or configuration.')
            LOGGER.error('Please ensure they exist and you have the appropriate read rights.')
            raise error

    @classmethod
    def __apply_cmdline_overrides(cls, argv: list[str]) -> None:
        """
        Look for commandline arguments with similar names as loaded static_config_class options. Returns all
        found arguments which can be used to temporarily override information loaded from the
        static_config_class file.
        Careful!! This does not work with multi layer data structures. Only with primitive types
        and lists containing primitive types!
        :return: Dict containing key, value pairs of overrides to apply
        """

        def bool_parse(string: str) -> bool:
            return bool(distutils.util.strtobool(string))

        unsupported_type_message = 'Excluding configuration option %s from command-line overrides '\
                                   'because its type %s is not supported. Command-line overriding' \
                                   ' is supported for primitive types and lists thereof.'

        parser = argparse.ArgumentParser()
        config_option: str
        for config_option, value in cls.__config.items():
            arg_name = '--' + config_option.replace('_', '-')
            if isinstance(value, bool):
                parser.add_argument(arg_name, type=bool_parse, default=value)
            elif isinstance(value, list):
                if len(value) == 0:
                    parser.add_argument(arg_name, nargs='+', type=str, default=value)
                elif isinstance(value[0], bool):
                    parser.add_argument(arg_name, nargs='+', type=bool_parse, default=value)
                elif type(value[0]) in (int, float, str):
                    parser.add_argument(arg_name, nargs='+', type=type(value[0]), default=value)
                else:
                    LOGGER.info(unsupported_type_message, config_option, type(value))
            elif type(value) in (int, float, str):
                parser.add_argument(arg_name, type=type(value), default=value)
            else:
                LOGGER.info(unsupported_type_message, config_option, type(value))
        cls.__config.update(vars(parser.parse_args(argv)))

    @classmethod
    def get(cls, name: str):  # type: ignore
        """
        Access to the configuration.
        :param name: Name of the configuration variable to read
        :return: Value of the requested configuration variable
        """
        try:
            return cls.__config[name]
        except KeyError as error:
            LOGGER.error('There is no configuration variable with name %s!', name)
            raise error
        except AttributeError as error:
            LOGGER.error('The configuration needs to be set up before accessing its members!')
            raise SetupFirstError from error

    @classmethod
    def set(cls, name: str, value: SupportedTypes) -> None:
        """
        Change the configuration for mutable values.
        Raises ImmutableError if value is immutable.
        :param name: Name of the configuration variable to change
        :param value: New value for the configuration variable
        """
        try:
            if name in cls.__immutable:
                LOGGER.error('Cannot change value of static_config_class variable %s as it is immutable!', name)
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
    def reset(cls) -> None:
        """
        Resets the class so it can be setup again.
        """
        try:
            del cls.__config
            del cls.__schema
            del cls.__immutable
        except AttributeError:
            LOGGER.warning('Unnecessary reset call - nothing to reset here.')

    @classmethod
    def string_representation(cls) -> str:
        """
        Returns a human-readable representation of current configuration.
        :return: String representation
        """
        return json.dumps(cls.__config, sort_keys=True, indent=4)

    @classmethod
    def write(cls, path: Path) -> None:
        """
        Persists the current configuration in a JSON file.
        :param path: Path to write the configuration to
        """
        with open(path, mode='w', encoding='utf8') as file:
            json.dump(cls.__config, file, sort_keys=True, indent=4)

    @classmethod
    def identifier(cls, keys: list[str] = None) -> str:
        """
        Computes and returns a hash of the current configuration. The hash only depends on the
        configuration keys and values, not on a schema or immutability settings.

        :param keys: Keys to use for the hashing, if None all keys will be used.
        :return: Hexadecimal md5 hash of the static_config_class
        """
        if keys:
            config = {key: cls.__config[key] for key in keys}
        else:
            config = cls.__config
        return hashlib.md5((json.dumps(config, sort_keys=True)).encode('utf-8')).hexdigest()

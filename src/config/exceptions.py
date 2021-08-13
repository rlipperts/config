"""
Different custom errors for various cases. They mostly inherit the errors that are thrown
"""
import json
import jsonschema  # type: ignore


class ConfigError(Exception):
    """
    Super class for configuration Errors.
    """


class ImmutableError(ConfigError, NameError):
    """
    Error for attempt to change immutable Data.
    """


class SetupFirstError(ConfigError, ValueError):
    """
    Error if trying to access data before setup has been called.
    """


class ConfigExistsError(ConfigError):
    """
    Error if trying to setup a config that already exists.
    If new setup is desired use the reset function first.
    """


class ConfigValidationError(ConfigError, jsonschema.exceptions.ValidationError):
    """
    Error if configuration validation failed.
    """

    def __init__(self):
        jsonschema.exceptions.ValidationError.__init__(self, message='')
        ConfigError.__init__(self)


class ConfigDecodeError(ConfigError, json.JSONDecodeError):
    """
    Error if configuration file is malformatted.
    """

"""
Import the module data, that you want to have externally accessible here.
"""
from static_config_class.configuration import Config
from static_config_class.exceptions import ConfigError, SetupFirstError, ImmutableError, \
    ConfigValidationError, ConfigDecodeError, ConfigExistsError

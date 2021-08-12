"""
Implement tests here (and in other files, one for every python module you want to test).
"""
from pathlib import Path

import jsonschema.exceptions
import pytest

from config import Config


schema_path = Path.cwd() / 'data/tests/schema.json'
config_path = Path.cwd() / 'data/tests/config.json'
invalid_config_path = Path.cwd() / 'data/tests/invalid_config.json'


# todo: test config creation and usage
# pylint: disable=missing-function-docstring
def test_configuration_creation_from_file():
    # check that it does not raise an error when creating correct config
    Config.setup(config_path, schema_path)


# todo: test config creation and usage
# pylint: disable=missing-function-docstring
def test_configuration_creation_errors_if_wrong_file_type():
    # check that it does not raise an error when creating correct config
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_errors_on_wrong_keys():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        Config.setup(invalid_config_path, schema_path)


# pylint: disable=missing-function-docstring
def test_configuration_errors_on_missing_keys():
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_get_returns_correct_data():
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_get_errors_if_not_setup():
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_set_changes_mutable_data():
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_set_does_not_change_immutable_data():
    assert False


# pylint: disable=missing-function-docstring
def test_configuration_set_errors_if_not_setup():
    assert False

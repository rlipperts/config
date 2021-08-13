# pylint: disable=missing-function-docstring,protected-access
"""
Implement tests here (and in other files, one for every python module you want to test).
"""
import json
from pathlib import Path

import pytest

from config import Config, SetupFirstError, ImmutableError, ConfigValidationError, ConfigExistsError

schema_path = Path.cwd() / 'data/tests/schema.json'
config_path = Path.cwd() / 'data/tests/config.json'
minimal_config_path = Path.cwd() / 'data/tests/minimal_config.json'
invalid_config_path = Path.cwd() / 'data/tests/invalid_config.json'
missing_key_path = Path.cwd() / 'data/tests/missing_required_key_config.json'


def test_reset_resets():
    Config._Config__config = {}
    Config._Config__schema = {}
    Config._Config__immutable = []
    Config.reset()
    assert not hasattr(Config, '_Config__config')
    assert not hasattr(Config, '_Config__schema')
    assert not hasattr(Config, '_Config__immutable')


def test_setup_from_file():
    # check that it does not raise an error when creating correct config
    Config.reset()
    Config.setup(config_path, schema_path)
    with open(config_path) as file:
        data = json.load(file)
    for key in data.keys():
        assert Config._Config__config[key] == data[key]


def test_setup_errors_on_unknown_keys():
    Config.reset()
    with pytest.raises(ConfigValidationError):
        Config.setup(invalid_config_path, schema_path)


def test_setup_errors_on_missing_required_keys():
    Config.reset()
    with pytest.raises(ConfigValidationError):
        Config.setup(missing_key_path, schema_path)


def test_setup_missing_non_required_keys():
    Config.reset()
    Config.setup(minimal_config_path)


def test_setup_errors_if_already_setup():
    Config.reset()
    Config.setup(config_path, schema_path)
    with pytest.raises(ConfigExistsError):
        Config.setup(config_path, schema_path)


def test_get_returns_correct_data():
    Config.reset()
    Config.setup(config_path, schema_path)
    with open(config_path) as file:
        data = json.load(file)
    for key in data.keys():
        assert Config.get(key) == data[key]


def test_get_errors_if_not_setup():
    Config.reset()
    with pytest.raises(SetupFirstError):
        Config.get('key')


def test_get_errors_if_key_doesnt_exist():
    Config.reset()
    Config.setup(config_path)
    with pytest.raises(KeyError):
        Config.get('non_existing_key')


def test_set_changes_mutable_data():
    Config.reset()
    Config.setup(config_path)
    Config.set('key', 'new_value')
    assert Config.get('key') == 'new_value'


def test_set_does_not_change_immutable_data():
    Config.reset()
    Config.setup(config_path, immutable=['key'])
    with pytest.raises(ImmutableError):
        Config.set('key', 'new_value')


def test_set_errors_if_not_setup():
    Config.reset()
    with pytest.raises(SetupFirstError):
        Config.set('key', 'new_value')

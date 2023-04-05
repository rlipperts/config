# pylint: disable=missing-function-docstring,protected-access
"""
Implement tests here (and in other files, one for every python module you want to test).
"""
import json
from pathlib import Path

import pytest

from static_config_class import Config, SetupFirstError, ImmutableError, ConfigValidationError, ConfigExistsError

schema_path = Path.cwd() / 'data/tests/schema.json'
config_path = Path.cwd() / 'data/tests/static_config_class.json'
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
    # check that it does not raise an error when creating correct static_config_class
    Config.reset()
    Config.setup(config_path, schema_path)
    with open(config_path, encoding='utf8') as file:
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


@pytest.mark.parametrize('argv, key, expected_value', [
    (['--key', 'new_value'], 'key', 'new_value'),
    (['--bool-key', 'false'], 'bool_key', False),
    (['--int-key', '0'], 'int_key', 0),
    (['--float-key', '0.5'], 'float_key', 0.5),
    (['--list-key', 'test', 'test_a', 'test_2'], 'list_key', ['test', 'test_a', 'test_2']),
    (['--bool-list-key', 'true', '1', 'FALSE'], 'bool_list_key', [True, True, False]),
    (['--int-list-key', '1', '7', '3'], 'int_list_key', [1, 7, 3]),
    (['--float-list-key', '0.5', '6.9', '2.4', '3.3'], 'float_list_key', [0.5, 6.9, 2.4, 3.3]),
])
def test_cmdline_overrides(argv: list[str], key, expected_value):
    Config.reset()
    Config.setup(config_path, schema_path, allow_cmdline_override=False)
    Config._Config__apply_cmdline_overrides(argv)  # type: ignore
    assert Config.get(key) == expected_value


def test_get_returns_correct_data():
    Config.reset()
    Config.setup(config_path, schema_path)
    with open(config_path, encoding='utf8') as file:
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


def test_config_write():
    Config.reset()
    Config.setup(config_path)
    write_path = Path('/tmp/static_config_class.json')
    Config.write(write_path)
    with open(write_path, mode='r', encoding='utf8') as file:
        written_config = json.load(file)
    assert Config._Config__config == written_config


def test_id_is_repeatable():
    Config.reset()
    Config.setup(config_path)
    first_id = Config.identifier()

    Config.reset()
    Config.setup(config_path)
    second_id = Config.identifier()

    assert first_id == second_id


def test_id_of_different_configs_is_different():
    Config.reset()
    Config.setup(config_path)
    first_id = Config.identifier()

    Config.reset()
    Config.setup(minimal_config_path)
    second_id = Config.identifier()

    assert first_id != second_id


def test_id_depends_only_on_config():
    Config.reset()
    Config.setup(config_path)
    first_id = Config.identifier()

    Config.reset()
    Config.setup(config_path, validation_schema_location=schema_path)
    second_id = Config.identifier()

    Config.reset()
    Config.setup(config_path, immutable=['key'])
    third_id = Config.identifier()

    assert first_id == second_id == third_id

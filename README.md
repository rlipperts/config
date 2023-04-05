# Static Config Class
_Configuration manager for medium-sized projects. Maintains a configuration inside a static class. 
Intended for personal use so breaking changes might be introduced at any point._

## installation

The package can simply be installed with pip
```
pip install static-config
```

## usage

To use the configuration manager you have to set it up first by giving it your configuration.

Your configuration has to be provided via a path to a JSON file
```json
{
  "key": "value",
  "bool_key": true,
  "int_key": 1,
  "float_key": 3.14159,
  "list_key": ["one", "two", "three"],
  "dict_key": {
    "key": "value"
  }
}
```
_data/tests/config.json_

The setup function then is called like this

```python
from static_config_class import Config
from pathlib import Path

config_json = Path.cwd() / 'data/tests/static_config_class.json'
Config.setup(config_json)
```
If configuration access is attempted before setup, a `SetupFirstError` is raised.

### reading/writing the configuration
Ater setup you can use the Methods `Config.get()` and `Config.set()` to gain read and write access 
on the configuration.
```python
...
# read the value of configuration key 'key'
some_config_data = Config.get('key')

# write 'value' to configuration key 'key'
Config.set('key', 'value')
```

### using a json schema
Optionally, you can provide a JSON schema to validate the configuration during setup and value 
changes.

The schema is provided as path to a JSON schema
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "Test Config",
  "description": "An example static_config_class to test this package",
  "type": "object",

  "properties": {
    "key": {
      "type": "string"
    },
    "bool_key": {
      "type": "boolean"
    },
    "int_key": {
      "type": "integer"
    },
    "float_key": {
      "type": "number"
    },
    "list_key": {
      "type": "array"
    },
    "dict_key": {
      "type": "object"
    }
  },

  "additionalProperties": false,
  "required": ["key", "bool_key"]
}
```
_data/tests/schema.json_


Setup with schema is straight forward. The schema is used to initially validate the config during 
setup and consecutively each time the config is changed. Raises a `ConfigValidationError` if the 
config is not conforming to the schema.

```python
from static_config_class import Config
from pathlib import Path

config_json = Path.cwd() / 'data/tests/static_config_class.json'
schema_json = Path.cwd() / 'data/tests/schema.json'
Config.setup(config_json)
```
Using a schema allows to allow/prohibit the later extensions of known configuration keys and 
specification of keys that require a value during setup. Furthermore, the `type` keyword can be 
used to enforce runtime typechecking.

### immutable values
During setup, you can pass a Collection containing all the configuration keys whose values are not 
allowed to be changed.

```python
from static_config_class import Config
from pathlib import Path

config_json = Path.cwd() / 'data/tests/static_config_class.json'
Config.setup(config_json, immutable=['key', 'bool_key'])
```
If the `Config.set()` method is used to update these, an `ImmutableError` is raised.

### persisting the configuration
If you changed your configuration during runtime and want to persist it as json file you can use 
the `Config.write()` function. 
```python
Config.write('out/updated_configuration.json')
```

### identifying the configuration
If you need to have a short reference of the current configuration state, you can calculate the 
configurations MD5-hash with the `Config.identifier()` function.
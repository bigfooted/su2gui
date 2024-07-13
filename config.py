# imports for json schema
import json
import jsonschema
from jsonschema import validate

# functions to update GUI after user enters a new key-value pair in jsonData
from fileio import set_json_fileio
from initialization import set_json_initialization
from materials import set_json_materials
from numerics import set_json_numerics
from physics import set_json_physics
from solver import set_json_solver
from su2_json import updateBCDictListfromJSON


from uicard import server
from logger import log


# Extract state and controller from the server
state, ctrl = server.state, server.controller

state.cofig_str = ""

def add_new_property():
    # prepare a valid schema for using the function given below
    # validate_dict_against_schema()
    if state.new_config_key==None or state.new_config_value==None:
        return
    value = state.new_config_value
    # trying to convert new_config_value to a bool or float
    try:
        value =  float(value)
    except:
        if value.lower() in ("yes", "true", "no", "false"):
            value =  value.lower() == "yes" or value.lower() == "true"
        elif (value.startswith('(') and value.endswith(')') or value.startswith('[') and value.endswith(']')) or ',' in value or ' ' in value:
            # Remove parentheses and split by comma
            if value[0]=='(' or value[-1]==')' or value[0]=='[' or value[-1]==']':
               value = value[1:-1]
            if ',' in value:
               value =  value.split(',')
            else:
               value = value.split()
            # Convert each item to an appropriate type
            value = [v.strip() for v in value]
            value = [int(v) if v.isdigit() else v for v in value]
    state.new_config_key = state.new_config_key.upper().strip()
    state.jsonData[state.new_config_key] = value
    state.dirty('jsonData')
    update_config_str()
    set_json_physics()
    set_json_initialization()
    set_json_numerics()
    set_json_solver()
    set_json_fileio()
    set_json_materials()
    updateBCDictListfromJSON()
    log("info", f"Added {state.new_config_key} : {state.new_config_value}({type(state.new_config_value)})")

def update_config_str():
    max_key_len = max(len(key) for key in state.jsonData.keys())  
    state.config_str = "  \n".join([f"\t{key:{max_key_len}} : {value}" for key, value in state.jsonData.items()])

@state.change("key")
def update_new_config_key(key, **kwargs):
    state.new_config_key = key

@state.change("value")
def update_new_config_value(value, **kwargs):
    state.new_config_value = value


def validate_dict_against_schema():
    log("info", state.jsonData)
    # Load the JSON schema from the file
    try:
        with open("./user/JsonSchema.json", 'r') as file:
            schema = json.load(file)
    except FileNotFoundError:
        log("error", "Schema file not found.")
        return False
    except json.JSONDecodeError:
        log("error", "Invalid JSON schema file.")
        return False

    # Validate the dictionary against the schema
    try:
        validate(instance=state.jsonData, schema=schema)
        log("info", "The dictionary is valid.")
        return True
    except jsonschema.exceptions.ValidationError as ve:
        log("error", f"Validation error: {ve.message}")
        return False
    except jsonschema.exceptions.SchemaError as se:
        log("error", f"Schema error: {se.message}")
        return False
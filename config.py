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
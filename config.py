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
    
    # trying to convert new_config_value to a bool or float
    try:
        state.new_config_value =  float(state.new_config_value)
    except:
        if state.new_config_value.lower() in ("yes", "true", "no", "false"):
            state.new_config_value =  state.new_config_value.lower() == "yes" or state.new_config_value.lower() == "true"
    state.new_config_key = state.new_config_key.upper().strip()
    state.jsonData[state.new_config_key] = state.new_config_value
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
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
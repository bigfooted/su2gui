
# ##################################### JSON ##############################
from uicard import ui_card, ui_subcard, server

import json,jsonschema
from jsonschema import validate, ValidationError, SchemaError

from pathlib import Path
BASE = Path(__file__).parent

state, ctrl = server.state, server.controller

# ##################################### JSON ##############################

#class jsonManager:
#    def __init__(self, state, name):
#        """ initialize the pipeline """
#        self._state = state
#        self._name = name
#        self._next_id = 1
#        self._nodes = {}
#        self._children_map = defaultdict(set)

# ##################################### JSON ##############################
# Opening JSON file, which is a python dictionary
def read_json_data(filenam):
  print("jsondata::opening json file and reading data")
  with open(filenam,"r") as jsonFile:
    state.jsonData = json.load(jsonFile)
  return state.jsonData
# ##################################### JSON ##############################

# Read the default values for the SU2 configuration.
# this is done at startup
state.jsonData = read_json_data(BASE / "user" / "config.json")

# Q:we now have to add all mandatory fields that were not found in the json file?
# A:nijso: actually, they are added automatically when we add an item for the first time

# get the "json" name from the dictionary
def GetJsonName(value,List):
  print("value=",value)
  print("list=",List)
  entry = [item for item in List if item["value"] == value]
  print("entry=",entry)
  return(entry[0]["json"])

# get the "value" from the dictionary
def GetJsonIndex(value,List):
  entry = [item for item in List if item["json"] == value]
  return(int(entry[0]["value"]))

def GetBCName(value,List):
  entry = [item for item in List if item["bcName"] == value]
  return(entry[0])


def SetGUIStateWithJson():
  print("setting GUI state with Json variable")
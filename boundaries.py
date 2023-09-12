# boundaries gittree menu

# note that in the main menu, we need to call/add the following:
# 1) from boundaries import *
# 2) call boundaries_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline)
# 4) define any global state variables that might be needed

# definition of ui_card
from uicard import ui_card, ui_subcard, ui_card_children_only,ui_card_parent_only, server
from trame.widgets import vuetify
from su2_json import *
from materials import *
import copy
state, ctrl = server.state, server.controller

state.boundaries_main_idx = 0

############################################################################
# Boundaries models - list options #
############################################################################

# List: boundaries model: Main boundary selection
# note that we have to set this for each of the boundaries
LBoundariesMain= [
  {"text": "Inlet", "value": 0},
  {"text": "Outlet", "value": 1},
  {"text": "Wall", "value": 2},
  {"text": "Symmetry", "value": 3},
  {"text": "Far-field", "value": 4},
]

LBoundariesInletInc= [
  {"text": "Velocity inlet", "value": 0},
  {"text": "Pressure inlet", "value": 1},
]

LBoundariesInletComp= [
  {"text": "Total Conditions", "value": 0},
  {"text": "Mass flow", "value": 1},
]

LBoundariesOutletInc= [
  {"text": "Pressure outlet", "value": 0},
  {"text": "Target mass flow rate", "value": 1},
]

LBoundariesWall= [
  {"text": "Temperature", "value": 0},
  {"text": "Heat flux", "value": 1},
  {"text": "Heat transfer", "value": 2},
]

#search in a list of dictionaries and return the entry based on the value of the key
def get_entry_from_name(val,key,List):
  print("list = ",List)
  print("key = ",key)
  print("val = ",val)
  print(List[0][key])

  entry=None

  # loop over all dict items in the list
  for item in List:
      print(item[key])
      if item[key]==val:
        print("key found!")
        entry=item
  # get the dictionary item in the list based on the value of key
  #entry = (next(item for item in List if item[key] == val),None)
  # return the entry in the list
  return entry

# now get the index in LBoundariesMain using the name
def get_boundaries_main_idx_from_name(bcname):
    # get the entry in the list
    entry = get_entry_from_name(bcname,'bcName',state.BCDictList)
    print("entry = ",entry)

    idx = 0

    if not (entry==None):
      bctype = entry['bcType']
      print("bctype = ",bctype)
      entry = get_entry_from_name(bctype,'text',LBoundariesMain)
      print("entry = ",entry)
      idx = entry['value']

    return(idx)

###############################################################
# PIPELINE CARD : Boundaries
###############################################################
def boundaries_card_parent():
    # note that we want to show the card only for the children of the head/parent node
    with ui_card_parent_only(title="Boundaries", parent_ui_name="Boundaries"):
        print("     ## Boundaries Selection ##")

        #vuetify.VTextField(
        #    #v_model=("idx", 0),
        #    label= "boundaries field",
        #    outlined=True,
        #)


def boundaries_card_children():
    # note that we want to show the card only for the children of the head/parent node
    with ui_card_children_only(title="Boundaries", parent_ui_name="Boundaries"):
        print("     ## Boundaries Selection ##")

        vuetify.VTextField(
            #v_model=("idx", 0),
            label= ("selectedBoundaryName","none"),
            outlined=True,
        )

        vuetify.VTextField(
            #v_model=("idx", 0),
            label= ("selectedBoundaryIndex","none"),
            outlined=True,
        )

        # note that for each boundary we have to keep track of the status of:
        # 1. LBoundariesMain
        #    This is in state.BCDictList
        #    'name' : name of the boundary
        #    'bcType' : type of the boundary, options are in LBoundariesMain
        # so we need BCDictList entry with 'name'
        # and we need to get the corresponding index in LBoundariesMain into boundaries_main_idx
        with vuetify.VRow(classes="pt-2"):
            with vuetify.VCol(cols="6"):
                # first a list selection for the main boundary types
                vuetify.VSelect(
                    # What to do when something is selected
                    v_model=("boundaries_main_idx", 0),
                    # The items in the list
                    items=("representations_main",LBoundariesMain),
                    # the name of the list box
                    label="Boundary type:",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="mt-0 pt-0",
                )




###############################################################
# UI value update: boundaries model selection #
###############################################################
@state.change("boundaries_main_idx")
def update_boundaries_main(boundaries_main_idx, **kwargs):
    print("     boundary model selection: ",boundaries_main_idx)
    entry = get_entry_from_name(boundaries_main_idx,'value',LBoundariesMain)
    print("entry=",entry)
    bctype = entry['text']
    print("bctype=",bctype)
    print("current selected boundary =",state.selectedBoundaryName)

    # update the BCDictList
    for index in range(len(state.BCDictList)):
      print(state.BCDictList[index])
      if state.BCDictList[index]['bcName']==state.selectedBoundaryName:
        print("change bc of index ",index,"to type ",bctype)
        state.BCDictList[index]['bcType'] = bctype
        break

    print("index = ",index)
    state.selectedBoundaryIndex = str(index)

    #state.jsonData['SST_OPTIONS']= GetJsonName(physics_turb_sst_idx,LPhysicsTurbSSTOptions)

@state.change("selectedBoundaryName")
def update_boundaries_main(selectedBoundaryName, **kwargs):
    print("     boundary name selection: ",selectedBoundaryName)
    state.boundaries_main_idx = get_boundaries_main_idx_from_name(selectedBoundaryName)
    print("boundaries_main_idx = ",state.boundaries_main_idx)
    state.dirty('boundaries_main_idx')

    #state.jsonData['SST_OPTIONS']= GetJsonName(physics_turb_sst_idx,LPhysicsTurbSSTOptions)



###############################################################
# PIPELINE SUBCARD : PHYSICS
###############################################################
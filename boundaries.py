# boundaries gittree menu

# note that in the main menu, we need to call/add the following:
# 1) from boundaries import *
# 2) call boundaries_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline)
# 4) define any global state variables that might be needed

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *
from materials import *
import copy
state, ctrl = server.state, server.controller

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

###############################################################
# PIPELINE CARD : Boundaries
###############################################################
def boundaries_card():
    with ui_card(title="Boundaries", ui_name="Boundaries"):
        print("     ## Boundaries Selection ##")

        # 2 columns, left containing compressible/incompressible
        # right containing energy on/off (for incompressible only)
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
    print("     turbulence model selection: ",boundaries_main_idx)
    #state.jsonData['SST_OPTIONS']= GetJsonName(physics_turb_sst_idx,LPhysicsTurbSSTOptions)

###############################################################
# PIPELINE SUBCARD : PHYSICS
###############################################################
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

# for dialog cards:
#1. define a boolean to show//hide the dialog
#2. define dialog_card
#3. define an update for the boolean to show/hide the dialog
#4. initialize the dialog by calling it in the singlepagewithdrawerlayout
#5. couple to a button in the main ui dialog

# 1. define a boolean to show//hide the dialog
state.show_boundaries_dialog_card_inlet = False
state.show_boundaries_dialog_card_outlet = False
state.show_boundaries_dialog_card_wall = False
state.show_boundaries_dialog_card_farfield = False

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
  {"text": "Far-field", "value": 3},
  {"text": "Symmetry", "value": 4},
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

def update_boundaries_dialog_card(idx):
  print("idx = ",idx)
  if(idx==0):
    update_boundaries_dialog_card_inlet()
  elif(idx==1):
    update_boundaries_dialog_card_outlet()
  elif(idx==2):
    update_boundaries_dialog_card_wall()
  elif(idx==3):
    update_boundaries_dialog_card_farfield()


#2. define dialog_card
######################################################################
# popup window for boundaries model - inlet
def boundaries_dialog_card_inlet():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_boundaries_dialog_card_inlet",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("Inlet",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        #with vuetify.VContainer(fluid=True, v_if=("jsonData['FLUID_MODEL']=='CONSTANT_DENSITY' ")):
        with vuetify.VContainer(fluid=True):

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              # Then a list selection for turbulence submodels
              vuetify.VSelect(
                # What to do when something is selected
                v_model=("boundaries_inlet_inc_idx", 0),
                # The items in the list
                items=("representations_inlet_inc",LBoundariesInletInc),
                # the name of the list box
                label="Inlet type",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="py-0 my-0",
            )

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_velocity_magnitude_idx", 1.0),
                # the name of the list box
                label="Velocity magnitude [m/s]",
              )
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_temperature_idx", 300.0),
                # the name of the list box
                label="Temperature [K]",
              )
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="3", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_nx_idx", 1.0),
                # the name of the list box
                label="n_x",
              )
            with vuetify.VCol(cols="3", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_ny_idx", 0.0),
                # the name of the list box
                label="n_y",
              )
            with vuetify.VCol(cols="3", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_nz_idx", 0.0),
                # the name of the list box
                label="n_z",
              )

          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              # checkbox for energy (can only be deselected for incompressible)
              vuetify.VCheckbox(
                  v_model=("boundary_inc_vel_usenormals_idx", True),
                  label="velocity normal to inlet",
                  # activate or deactivate/disable the checkbox
                  # only active for incompressible flow
                  # else, default is on
                  #disabled=("physics_comp_idx",0),
                  classes="mt-1 pt-1",
                  hide_details=True,
                  dense=True,
              )

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_inlet_damping_idx", 0.1),
                # the name of the list box
                label="inlet damping factor",
              )
        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_boundaries_dialog_card_inlet)

#3. define an update for the boolean to show/hide the dialog
# switch the visibility of the popup window on/off
def update_boundaries_dialog_card_inlet():
    state.show_boundaries_dialog_card_inlet = not state.show_boundaries_dialog_card_inlet

#2. define dialog_card
######################################################################
# popup window for boundaries model - outlet
def boundaries_dialog_card_outlet():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_boundaries_dialog_card_outlet",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("Outlet",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        #with vuetify.VContainer(fluid=True, v_if=("jsonData['FLUID_MODEL']=='CONSTANT_DENSITY' ")):
        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              # Then a list selection for turbulence submodels
              vuetify.VSelect(
                # What to do when something is selected
                v_model=("boundaries_outlet_inc_idx", 0),
                # The items in the list
                items=("representations_outlet_inc",LBoundariesOutletInc),
                # the name of the list box
                label="Outlet type",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="py-0 my-0",
            )

        # pressure outlet
        with vuetify.VContainer(fluid=True,v_if=("boundaries_outlet_inc_idx==0"),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_outlet_P_idx", 300.0),
                # the name of the list box
                label="Pressure [Pa]",
                #    label= ("selectedBoundaryIndex","none"),
              )
        # target massflow
        with vuetify.VContainer(fluid=True,v_if=("boundaries_outlet_inc_idx==1"),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_outlet_m_idx", 0.0),
                # the name of the list box
                label="Target mass-flow [kg/s]",
                #    label= ("selectedBoundaryIndex","none"),
              )
        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_boundaries_dialog_card_outlet)

#3. define an update for the boolean to show/hide the dialog
# switch the visibility of the popup window on/off
def update_boundaries_dialog_card_outlet():
    state.show_boundaries_dialog_card_outlet = not state.show_boundaries_dialog_card_outlet


#2. define dialog_card
######################################################################
# popup window for boundaries model - wall
def boundaries_dialog_card_wall():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_boundaries_dialog_card_wall",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("Wall",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        #with vuetify.VContainer(fluid=True, v_if=("jsonData['FLUID_MODEL']=='CONSTANT_DENSITY' ")):
        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              # Then a list selection for turbulence submodels
              vuetify.VSelect(
                # What to do when something is selected
                v_model=("boundaries_wall_idx", 0),
                # The items in the list
                items=("representations_wall",LBoundariesWall),
                # the name of the list box
                label="Wall type",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="py-0 my-0",
            )
        # temperature
        with vuetify.VContainer(fluid=True,v_if=("boundaries_wall_idx==0"),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_temperature_idx", 300.0),
                # the name of the list box
                label="Temperature [K]",
                #    label= ("selectedBoundaryIndex","none"),
              )
        # heat flux
        with vuetify.VContainer(fluid=True,v_if=("boundaries_wall_idx==1"),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_heatflux_idx", 0.0),
                # the name of the list box
                label="Heat flux [J/m^2]",
                #    label= ("selectedBoundaryIndex","none"),
              )
        # heat transfer
        with vuetify.VContainer(fluid=True,v_if=("boundaries_wall_idx==2"),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_heattransfer_h_idx", 1000.0),
                # the name of the list box
                label="Heat Transfer Coefficient [J/K.m^2]",
                #    label= ("selectedBoundaryIndex","none"),
              )
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_inc_heattransfer_T_idx", 300.0),
                # the name of the list box
                label="Far-field temperature [K]",
                #    label= ("selectedBoundaryIndex","none"),
              )

        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_boundaries_dialog_card_wall)

#3. define an update for the boolean to show/hide the dialog
# switch the visibility of the popup window on/off
def update_boundaries_dialog_card_wall():
    state.show_boundaries_dialog_card_wall = not state.show_boundaries_dialog_card_wall

#2. define dialog_card
######################################################################
# popup window for boundaries model - farfield
def boundaries_dialog_card_farfield():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_boundaries_dialog_card_farfield",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("Far-field",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        with vuetify.VContainer(fluid=True):

          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_farfield_V_idx", 1.0),
                # the name of the list box
                label="Far-field Velocity [m/s]",
              )

          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_farfield_P_idx", 101325.0),
                # the name of the list box
                label="Far-field pressure [Pa]",
              )

          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_farfield_T_idx", 300.0),
                # the name of the list box
                label="Far-field temperature [K]",
              )

          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("boundaries_farfield_rho_idx", 1.2),
                # the name of the list box
                label="Far-field density [kg/m^3]",
              )


        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_boundaries_dialog_card_farfield)

#3. define an update for the boolean to show/hide the dialog
# switch the visibility of the popup window on/off
def update_boundaries_dialog_card_farfield():
    state.show_boundaries_dialog_card_farfield = not state.show_boundaries_dialog_card_farfield



# search in a list of dictionaries and return the entry based on the value of the key
def get_entry_from_name(val,key,List):
  #print(List[0][key])
  entry=None
  # loop over all dict items in the list
  for item in List:
      #print(item[key])
      if item[key]==val:
        entry=item
  return entry

# now get the index in LBoundariesMain using the name
def get_boundaries_main_idx_from_name(bcname):
    # get the entry in the list
    entry = get_entry_from_name(bcname,'bcName',state.BCDictList)

    idx = 0

    if not (entry==None):
      bctype = entry['bcType']
      entry = get_entry_from_name(bctype,'text',LBoundariesMain)
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

        # we show the boundary options only if the boundary is not internal
        with vuetify.VContainer(fluid=True, v_if=("selectedBoundaryName!='internal' ")):

          vuetify.VTextField(
            #v_model=("idx", 0),
            label= ("selectedBoundaryName","none"),
            outlined=True,
          )

          #vuetify.VTextField(
          #    #v_model=("idx", 0),
          #    label= ("selectedBoundaryIndex","none"),
          #    outlined=True,
          #)

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
            with vuetify.VCol(cols="4", classes=""):
              with vuetify.VBtn(classes="mx-0 py-0 mt-0 mb-0",elevation=1,variant="text",color="white", click=(update_boundaries_dialog_card,"[boundaries_main_idx]"), icon="mdi-dots-vertical"):
                vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")



###############################################################
# UI value update: boundaries model selection #
###############################################################
@state.change("boundaries_main_idx")
def update_boundaries_main(boundaries_main_idx, **kwargs):
    entry = get_entry_from_name(boundaries_main_idx,'value',LBoundariesMain)
    bctype = entry['text']

    # update the BCDictList
    for index in range(len(state.BCDictList)):
      if state.BCDictList[index]['bcName']==state.selectedBoundaryName:
        state.BCDictList[index]['bcType'] = bctype
        break

    state.selectedBoundaryIndex = str(index)


# when the boundary selection changes, we go here
# we then update the boundary_main_index
# when the state of boundary index changes, we get the actual boundary condition name
# and type that we stored for the boundary
@state.change("selectedBoundaryName")
def update_boundaries_main(selectedBoundaryName, **kwargs):
    # get the index from the boundary name
    state.boundaries_main_idx = get_boundaries_main_idx_from_name(selectedBoundaryName)
    state.dirty('boundaries_main_idx')




###############################################################
# PIPELINE SUBCARD : PHYSICS
###############################################################
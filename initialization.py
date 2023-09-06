# initialization gittree menu

# note that in the main menu, we need to call/add the following:
# 1) from initialization import *
# 2) call initialization_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline)
# 4) define any global state variables that might be needed

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *

state, ctrl = server.state, server.controller

############################################################################
# Initialization models - list options #
############################################################################

# option: use restart file or initialize
# when a restart file is loaded, we automatically use it unless we overwrite it in the
# initial setup
# the solver cannot start unless we define an initial solution somehow


# option: initialization pull-down: {from file, uniform}
# option: patch: {cube, cylinder, sphere}
#         selection of variables{U,V,etc} + constant value


############################################################################
# Initialization models - list options #
############################################################################

# List: initialization model: options
LInitializationOption= [
  {"text": "From file (Restart)", "value": 0},
  {"text": "Uniform", "value": 1},
]

LInitializationPatch= [
  {"text": "Cube", "value": 0},
  {"text": "Cylinder", "value": 1},
  {"text": "Sphere", "value": 2},
]

###############################################################
# PIPELINE CARD : Initialization
###############################################################
def initialization_card():
    with ui_card(title="Initialization", ui_name="Initialization"):
        print("def initialization_card ")

        # 1 row of option lists
        with vuetify.VRow(classes="pt-2"):
          with vuetify.VCol(cols="10"):

            # Then a list selection for initialization submodels
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("initial_option_idx", 0),
                # The items in the list
                items=("representations_initial",LInitializationOption),
                # the name of the list box
                label="Initialize from:",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 mt-1",
            )
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("initial_patch_idx", 0),
                # The items in the list
                items=("representations_init_patch",LInitializationPatch),
                # the name of the list box
                label="Patch:",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 mt-1",
                disabled = True,
            )

            # restart file input inside the toolbar
            # note that this should be moved elsewhere
            vuetify.VFileInput(
              # single file only
              multiple=False,
              background_color="white",
              # the icon in front of the file input
              prepend_icon="mdi-file",
              show_size=True,
              small_chips=True,
              truncate_length=25,
              v_model=("restartFile", None),
              dense=True,
              hide_details=True,
              style="max-width: 300px;",
              accept=".dat",
              __properties=["accept"],
            )

            vuetify.VTextField(
              # What to do when something is selected
              v_model=("initialization_state_idx", 1.0),
              # the name of the list box
              label=state.field_state_name,
            )

            #with vuetify.VBtn(icon=True, click=su2_play, disabled=("export_disabled",False)):
            with vuetify.VBtn("Initialize",click=su2_initialize):
                vuetify.VIcon("{{solver_icon}}",color="purple")

    # update the initial option to recompute based on upstream changes
    # this makes sure that the incompressible vs compressible subui
    # is changed when comp/incomp is changed in the physics solver
    state.dirty('initial_option_idx')
    state.dirty('state.field_state_name')

###############################################################
# Initialize - method
###############################################################
@state.change("initialization_state_idx")
def update_initial_option(initialization_state_idx, **kwargs):
    print("initialization state selection: ",state.initialization_state_idx)
    # but for compressible or incompressible?


@state.change("initial_option_idx")
def update_initial_option(initial_option_idx, **kwargs):
    print("initialization selection: ",state.initial_option_idx)
    print("restart_sol= ",not bool (state.initial_option_idx))

    # option=0 : restart from file
    # option=1 : uniform values
    if (state.initial_option_idx==0):
      print("no initialization")
      if state.active_ui=="Initialization":
        state.active_sub_ui = "subinitialization_none"
    else:
      # uniform (constant) initialization
      print("state.jsonData solve = ",state.jsonData["SOLVER"])
      if "INC" in (state.jsonData["SOLVER"]):
        print("initialization for incompressible")
        if state.active_ui=="Initialization":
          state.active_sub_ui = "subinitialization_inc"
      else:
        print("initialization for compressible")
        if state.active_ui=="Initialization":
          state.active_sub_ui = "subinitialization_comp"

    # note that RESTART is the first option in LInitializationOption, so its value is 0.
    state.jsonData['RESTART_SOL']= not bool (state.initial_option_idx)

@state.change("initial_patch_idx")
def update_initial_patch(initial_patch_idx, **kwargs):
    print("patch selection: ",initial_patch_idx)


def su2_initialize():
    print("Initialize SU2 fields!"),



###############################################################
# PIPELINE SUBCARD : INITIALIZATION
###############################################################
# secondary card
def initialization_subcard():
    print("initialization_subcard:: set the ui_subcard")

    energy = bool(state.jsonData['INC_ENERGY_EQUATION'])
    print("energy equation=",energy)
    # for the card to be visible, we have to set state.active_sub_ui = subinitialization_inc
    with ui_subcard(title="initialization (incompressible)", sub_ui_name="subinitialization_inc"):
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Pressure", 1.0),
            # the name of the list box
            label="pressure",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Velocity_x", 1.0),
            # the name of the list box
            label="Velocity X",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Velocity_y", 1.0),
            # the name of the list box
            label="Velocity_Y",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Temperature", 1.0),
            # the name of the list box
            label="temperature",
            # is temperature disabled?
            disabled= ("energy",0)
        )

    # for the card to be visible, we have to set state.active_sub_ui = subinitialization
    with ui_subcard(title="initialization (compressible)", sub_ui_name="subinitialization_comp"):
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Density", 1.2),
            # the name of the list box
            label="density",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Velocity_x", 1.0),
            # the name of the list box
            label="Velocity X",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Velocity_y", 1.0),
            # the name of the list box
            label="Velocity_Y",
        )
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("Energy", 1.0),
            # the name of the list box
            label="energy",
        )


    # for the card to be visible, we have to set state.active_sub_ui = "subinitialization_none"
    with ui_subcard(title="no subinitialization", sub_ui_name="subinitialization_none"):
       vuetify.VTextarea(
                label="no subinitialization:",
                rows="5",
                v_model=("subinitializationtext", state.subinitializationtext),
        )

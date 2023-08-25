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
# PIPELINE CARD : Numerics
###############################################################
def initialization_card():
    with ui_card(title="Initialization", ui_name="Initialization"):
        print("## Initialization Selection ##")

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

            #with vuetify.VBtn(icon=True, click=su2_play, disabled=("export_disabled",False)):
            with vuetify.VBtn("Initialize",click=su2_initialize):
                vuetify.VIcon("{{solver_icon}}",color="purple")

###############################################################
# Initialize - method
###############################################################
@state.change("initial_option_idx")
def update_initial_option(initial_option_idx, **kwargs):
    print("initialization selection: ",initial_option_idx)
    print("restart_sol= ",not bool (initial_option_idx))
    # note that RESTART is the first option in LInitializationOption, so its value is 0.
    jsonData['RESTART_SOL']= not bool (initial_option_idx)

@state.change("initial_patch_idx")
def update_initial_patch(initial_patch_idx, **kwargs):
    print("patch selection: ",initial_patch_idx)


def su2_initialize():
    print("Initialize SU2 fields!"),
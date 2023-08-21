# solver gittree menu

# note that in the main menu, we need to call add the following:
# 1) from solver import *
# 2) call solver_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline)
# 4) define any global state variables that might be needed

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *

state, ctrl = server.state, server.controller
############################################################################
# Solver models - list options #
############################################################################

###############################################################
# PIPELINE CARD : Solver
###############################################################
def solver_card():
    with ui_card(title="Solver", ui_name="Solver"):
        print("## Solver Selection ##")

        # 1 row of option lists
        with vuetify.VRow(classes="pt-2"):
          with vuetify.VCol(cols="10"):

            vuetify.VTextField(
                # What to do when something is selected
                v_model=("Iter_idx", 100),
                # the name of the list box
                label="Iterations",
            )
        #with vuetify.VBtn(icon=True, click=su2_play, disabled=("export_disabled",False)):
        with vuetify.VBtn("Solve",click=su2_play):
            vuetify.VIcon("{{solver_icon}}",color="purple")


###############################################################
# Solver - state changes
###############################################################
@state.change("Iter_idx")
def update_material(Iter_idx, **kwargs):
    #
    print("ITER value: ",Iter_idx)
    #
    # we want to call a submenu
    #state.active_sub_ui = "submaterials_fluid"
    #
    # update config option value
    jsonData['ITER']= int(Iter_idx)

def su2_play():
    print("Start SU2 solver!"),
    # every time we press the button we switch the state
    state.solver_running = not state.solver_running
    if state.solver_running:
        state.solver_icon="mdi-stop-circle"
        print("SU2 solver started!"),
        # save mesh
        # save config
        # save restart file
        # call su2_cfd
    else:
        state.solver_icon="mdi-play-circle"
        print("SU2 solver stopped!"),

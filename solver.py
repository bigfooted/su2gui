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

import sys, subprocess


state, ctrl = server.state, server.controller
############################################################################
# Solver models - list options #
############################################################################

# list of fields that we could check for convergence
state.convergence_fields=[]
state.convergence_fields_range=[]
# list of booleans stating which of the fields need to be
# included in the convergence criteria
state.convergence_fields_visibility=[]

###############################################################
# PIPELINE CARD : Solver
###############################################################
def solver_card():
    with ui_card(title="Solver", ui_name="Solver"):
        print("## Solver Selection ##")
      # 1 row of option lists
        with vuetify.VRow(classes="pt-2"):
          with vuetify.VCol(cols="8"):

            vuetify.VTextField(
                # What to do when something is selected
                v_model=("convergence_val", -12),
                # the name of the list box
                label="Residual convergence value",
            )
          with vuetify.VCol(cols="4", classes="py-0 my-0"):
            with vuetify.VBtn(classes="mx-0 py-0 mt-2 mb-0",elevation=1,variant="text",color="white", click=update_solver_dialog_card_convergence, icon="mdi-dots-vertical"):
              vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")

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
    state.jsonData['ITER']= int(Iter_idx)

@state.change("convergence_val")
def update_material(convergence_val, **kwargs):
    #
    # update config option value
    state.jsonData['CONV_RESIDUAL_MINVAL']= int(convergence_val)

def su2_play():
    print("Start SU2 solver!"),
    # every time we press the button we switch the state
    state.solver_running = not state.solver_running
    if state.solver_running:
        state.solver_icon="mdi-stop-circle"
        print("SU2 solver started!"),

        # run SU2_CFD with config.cfg
        with open('su2.out', "w") as outfile:
          with open('su2.err', "w") as errfile:
            result = subprocess.run(['SU2_CFD', 'config_new.cfg'],
                                cwd="user/nijso/",
                                text=True,
                                stdout=outfile,
                                stderr=errfile
                                )
        #result = subprocess.run([sys.executable, "-c", "print('ocean')"])
        #result = subprocess.run(['SU2_CFD', 'config_new.cfg'])

        print(result)
        # save mesh
        # save config
        # save restart file
        # call su2_cfd
    else:
        state.solver_icon="mdi-play-circle"
        print("SU2 solver stopped!"),



def update_visibility(index, visibility):
    print("index=",index)
    print("visible=",state.convergence_fields_visibility)
    state.convergence_fields_visibility[index] = visibility
    print("visible=",state.convergence_fields_visibility)
    state.dirty("convergence_fields_visibility")
    print(f"Toggle {index} to {visibility}")


# select which variables to use for convergence. Currently: only residual values of the solver
def solver_dialog_card_convergence():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_solver_dialog_card_convergence",False)):
      with vuetify.VCard():


        vuetify.VCardTitle("Convergence Criteria",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")
        with vuetify.VContainer(fluid=True):

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VCheckbox(
                              # loop over list of convergence fields
                              v_for="id in convergence_fields_range",
                              key="id",
                              # checkbox changes the state of monitorLinesVisibility[id]
                              v_model=("convergence_fields_visibility[id]",),
                              # name of the checkbox
                              label=("`${ convergence_fields[id] }`",),
                              # on each change, immediately go to update_visibility
                              change=(update_visibility,"[id, $event]"),
                              classes="mt-1 pt-1",
                              hide_details=True,
                              dense=True,
              )

        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_solver_dialog_card_convergence)



def update_solver_dialog_card_convergence():
    print("changing state of solver_dialog_Card_convergence to:",state.show_solver_dialog_card_convergence)
    state.show_solver_dialog_card_convergence = not state.show_solver_dialog_card_convergence

    # if we show the card, then also update the fields that we need to show
    if state.show_solver_dialog_card_convergence==True:
      print("updating list of fields")
      # note that Euler and inc_euler can be treated as compressible / incompressible as well
      print(state.jsonData['SOLVER'])
      print(state.jsonData['INC_ENERGY_EQUATION'])

      if ("INC" in str(state.jsonData['SOLVER'])):
        compressible = False
      else:
        compressible = True

      # if incompressible, we check if temperature is on
      if (compressible==False):
        if (state.jsonData['INC_ENERGY_EQUATION']==True):
           energy=True
        else:
           energy=False

        # INC_RANS: [PRESSURE VELOCITY-X VELOCITY-Y] [VELOCITY-Z] [TEMPERATURE]
        # SA: [NU_TILDE]
        # SST: [TKE, DISSIPATION]
        # RANS: [DENSITY MOMENTUM-X MOMENTUM-Y] [ENERGY] [MOMENTUM-Z]

      if (compressible==True):
        state.convergence_fields=["RMS_DENSITY","RMS_MOMENTUM-X","RMS_MOMENTUM-Y"]
        if (state.nDim==3):
          state.convergence_fields.append("RMS_MOMENTUM-Z")
        state.convergence_fields.append("RMS_ENERGY")
      else:
        state.convergence_fields=["RMS_PRESSURE","RMS_VELOCITY-X","RMS_VELOCITY-Y"]
        if (state.nDim==3):
          state.convergence_fields.append("RMS_VELOCITY-Z")
        if (energy==True):
          state.convergence_fields.append("RMS_TEMPERATURE")

      state.convergence_fields_range=list(range(0,len(state.convergence_fields)))

      # get the checkbox states from the jsondata
      state.convergence_fields_visibility = [False for i in state.convergence_fields]
      for field in state.jsonData['CONV_FIELD']:
         print("field=",field)
         for i in range(len(state.convergence_fields)):
            print("i=",i," ",state.convergence_fields[i])
            if (field==state.convergence_fields[i]):
               print("field found")
               state.convergence_fields_visibility[i] = True



      print("convergence fields:",state.convergence_fields)
      state.dirty('convergence_fields')
      state.dirty('convergence_fields_range')
    else:

       # the dialog is closed again: we update the state of CONV_FIELD in jsonData
         state.jsonData['CONV_FIELD']=[]
         for i in range(len(state.convergence_fields_visibility)):
            if (state.convergence_fields_visibility[i]==True):
               state.jsonData['CONV_FIELD'].append(state.convergence_fields[i])


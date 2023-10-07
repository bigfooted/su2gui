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
import pandas as pd

import sys, subprocess

# real-time update, asynchronous io
import asyncio
from trame.app import get_server, asynchronous


# matplotlib
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from trame.widgets import matplotlib as tramematplotlib

# line 'i' has fixed color so the color does not change if a line is deselected
mplColorList=['blue','orange','red','green','purple','brown','pink','gray','olive','cyan',
              'black','gold','yellow','springgreen','thistle','beige','coral','navy','salmon','lightsteelblue']



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




# matplotlib
state.active_figure="mpl_plot_history"
state.graph_update=True
@state.change("active_figure", "figure_size", "countdown","monitorLinesVisibility")
def update_chart(active_figure, **kwargs):
    print("updating figure 1")
    ctrl.update_figure(globals()[active_figure]())
    #ctrl.update_figure2(globals()[active_figure]())

#matplotlib
def update_visibility(index, visibility):
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)
    state.monitorLinesVisibility[index] = visibility
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)
    state.dirty("monitorLinesVisibility")
    print(f"Toggle {index} to {visibility}")
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)

#matplotlib
def dialog_card():
    print("dialog card, lines=",state.monitorLinesNames)
    # show_dialog2 determines if the entire dialog is shown or not
    with vuetify.VDialog(width=200,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_dialog",False)):
      #with vuetify.VCard(color="light-gray"):
      with vuetify.VCard():
        vuetify.VCardTitle("Line visibility", classes="grey lighten-1 grey--text text--darken-3")

        #with vuetify.VListGroup(value=("true",), sub_group=True):
        #    with vuetify.Template(v_slot_activator=True):
        #            vuetify.VListItemTitle("Bars")
        #    with vuetify.VListItemContent():
        #            #with vuetify.VListItem(v_for="id in monitorLinesRange", key="id"):
        vuetify.VCheckbox(
                              # loop over list monitorLinesRange
                              v_for="id in monitorLinesRange",
                              key="id",
                              # checkbox changes the state of monitorLinesVisibility[id]
                              v_model=("monitorLinesVisibility[id]",),
                              # name of the checkbox
                              label=("`label= ${ monitorLinesNames[id] }`",),
                              # on each change, immediately go to update_visibility
                              change=(update_visibility,"[id, $event]"),
                              classes="mt-1 pt-1",
                              hide_details=True,
                              dense=True,
        )


        # close dialog window button
        #with vuetify.VCardText():
        # right-align the button
        with vuetify.VCol(classes="text-right"):
          vuetify.VBtn("Close", classes="mt-5",click=update_dialog)


# real-time update
@asynchronous.task
async def start_countdown():

    while state.keep_updating:
        with state:
            await asyncio.sleep(1.0)
            print("keep updating = ",state.keep_updating)
            #global history_filename
            readHistory(state.history_filename)
            # we flip-flop the true-false state to keep triggering the state and read the history file
            state.countdown = not state.countdown


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
            result = subprocess.Popen(['SU2_CFD', 'config_new.cfg'],
                                cwd="user/nijso/",
                                text=True,
                                stdout=outfile,
                                stderr=errfile
                                )
        # at this point we have started the simulation
        # we can now start updating the real-time plots
        state.keep_updating = True
        start_countdown()
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



def update_convergence_fields_visibility(index, visibility):
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
                              # on each change, immediately go to update_convergence_fields_visibility
                              change=(update_convergence_fields_visibility,"[id, $event]"),
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






# matplotlib
def update_dialog():
    state.show_dialog = not state.show_dialog
    state.dirty('monitorLinesVisibility')
    state.dirty('monitorLinesNames')
    state.dirty('monitorLinesRange')



# Read the history file
# set the names and visibility
def readHistory(filename):
    print("read_history, filename=",filename)
    skipNrRows=[]
    # read the history file
    dataframe = pd.read_csv(filename,skiprows=skipNrRows)
    # get rid of quotation marks in the column names
    dataframe.columns = dataframe.columns.str.replace('"','')
    # get rid of spaces in the column names
    dataframe.columns = dataframe.columns.str.replace(' ','')

    # limit the columns to the ones containing the strings rms and Res
    dfrms = dataframe.filter(regex='rms|Res')

    # only set the initial state the first time
    if state.monitorLinesNames==[]:
       state.monitorLinesNames = list(dfrms)
       state.monitorLinesRange = list(range(0,len(state.monitorLinesNames)))
       state.monitorLinesVisibility = [True for i in dfrms]
       state.dirty('monitorLinesNames')
       state.dirty('monitorLinesVisibility')
       state.dirty('monitorLinesRange')


    state.x = [i for i in range(len(dfrms.index))]
    print("x = ",state.x)
    state.ylist=[]
    for c in range(len(dfrms.columns)):
        state.ylist.append(dfrms.iloc[:,c].tolist())


    dialog_card()
    return [state.x,state.ylist]



def figure_size():
    if state.figure_size is None:
        return {}


    dpi = state.figure_size.get("dpi")
    rect = state.figure_size.get("size")
    w_inch = rect.get("width") / dpi
    h_inch = rect.get("height") / dpi

    if ((w_inch<=0) or (h_inch<=0)):
       return {}

    return {
        "figsize": (w_inch, h_inch),
        "dpi": dpi,
    }




###############################################################################
def mpl_plot_history():
    plt.close('all')
    fig, ax = plt.subplots(1,1,**figure_size(),facecolor='blue')
    #ax.cla()

    #fig.set_facecolor('black')
    #fig.tight_layout()
    #fig.patch.set_linewidth(10)
    #fig.patch.set_edgecolor('purple')
    ax.set_facecolor('#eafff5')
    fig.set_facecolor('blue')
    fig.patch.set_facecolor('blue')
    #ax.plot(
    #    np.random.rand(20),
    #    "-o",
    #    alpha=0.5,
    #    color="black",
    #    linewidth=5,
    #    markerfacecolor="green",
    #    markeredgecolor="lightgreen",
    #    markersize=20,
    #    markeredgewidth=10,
    #)
    #fig.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.9,hspace=0.8)

    fig.subplots_adjust(top=0.98, bottom=0.15, left=0.05, right=0.99, hspace=0.0,wspace=0.0)
    #fig.tight_layout()

    # loop over the list and plot
    for idx in state.monitorLinesRange:
      #print("line= ",idx,", name= ",state.monitorLinesNames[idx]," visible:",state.monitorLinesVisibility[idx])
      #print("__ range x = ", min(state.x), " ",max(state.x))
      # only plot if the visibility is True
      if state.monitorLinesVisibility[idx]:
        #print("printing line ",idx)
        ax.plot( state.x,state.ylist[idx], label=state.monitorLinesNames[idx],linewidth=5, markersize=20, markeredgewidth=10,color=mplColorList[idx])

    ax.set_xlabel('iterations',labelpad=10)
    ax.set_ylabel('residuals',labelpad=-15)
    ax.grid(True, color="lightgray", linestyle="solid")
    ax.legend(framealpha=1,facecolor='white')

    # autoscale the axis
    ax.autoscale(enable=True,axis="x")
    ax.autoscale(enable=True,axis="y")
    #ax.set_xlim(0, 22)
    #ax.set_ylim(-20, 0)
    #frame = ax.legend.get_frame()
    #frame.set_color('white')

    return fig


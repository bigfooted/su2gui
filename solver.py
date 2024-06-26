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
from su2_io import save_su2mesh, save_json_cfg_file

# check if a file is opened by another process
#import psutil

import pandas as pd

import sys, subprocess, io, time

# real-time update, asynchronous io
import asyncio
from trame.app import get_server, asynchronous

from trame.app.file_upload import ClientFile

import vtk
from vtkmodules.vtkCommonDataModel import vtkDataObject

# import the grid from the mesh module
from mesh import *
from vtk_helper import *

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

# the main su2 solver process
proc_SU2 = None

# list of fields that we could check for convergence
state.convergence_fields=[]
state.convergence_fields_range=[]
# list of booleans stating which of the fields need to be
# included in the convergence criteria
state.convergence_fields_visibility=[]

# global iteration number while running a case
state.global_iter = -1

# initialize from json file
def set_json_solver():
  state.iter_idx = state.jsonData['ITER']
  state.dirty('iter_idx')
  state.convergence_val = state.jsonData['CONV_RESIDUAL_MINVAL']
  state.dirty('convergence_val')

  #for field in state.jsonData['CONV_FIELD']:
  state.convergence_fields = state.jsonData['CONV_FIELD']
  log("info", f"state convergence fields =  = {state.convergence_fields," ",type(state.convergence_fields)}")


# matplotlib
state.active_figure="mpl_plot_history"
state.graph_update=True
@state.change("active_figure", "figure_size", "countdown","monitorLinesVisibility")
def update_chart(active_figure, **kwargs):
    log("info", "updating figure 1")
    ctrl.update_figure(globals()[active_figure]())
    #ctrl.update_figure2(globals()[active_figure]())

#matplotlib
def update_visibility(index, visibility):
    log("info", f"monitorLinesVisibility =  = {state.monitorLinesVisibility}")
    state.monitorLinesVisibility[index] = visibility
    log("info", f"monitorLinesVisibility =  = {state.monitorLinesVisibility}")
    state.dirty("monitorLinesVisibility")
    log("info", f"Toggle {index} to {visibility}")
    log("info", f"monitorLinesVisibility =  = {state.monitorLinesVisibility}")

#matplotlib
def dialog_card():
    log("info", f"dialog card, lines= = {state.monitorLinesNames}")
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
        # right-align the button
        with vuetify.VCol(classes="text-right"):
          vuetify.VBtn("Close", classes="mt-5",click=update_dialog)


# real-time update every xx seconds
@asynchronous.task
async def start_countdown(result):
    global proc_SU2

    while state.keep_updating:
        with state:
            await asyncio.sleep(2.0)
            log("info", f"iteration =  = {state.global_iter, type(state.global_iter)}")
            wrt_freq = state.jsonData['OUTPUT_WRT_FREQ'][1]
            log("info", f"wrt_freq =  = {wrt_freq, type(wrt_freq)}")
            log("info", f"iteration save =  = {state.global_iter % wrt_freq}")
            log("info", f"keep updating =  = {state.keep_updating}")
            # update the history from file
            readHistory(BASE / "user" / state.history_filename)
            # update the restart from file, do not reset the active scalar value
            # do not update when we are about to write to the file
            readRestart(BASE / "user" / state.restart_filename, False)

            # we flip-flop the true-false state to keep triggering the state and read the history file
            state.countdown = not state.countdown
            # check that the job is still running
            log("info", f"poll =  = {proc_SU2.poll()}")
            if proc_SU2.poll() != None:
              log("info", "job has stopped")
              # stop updating the graphs
              state.keep_updating = False
              # set the running state to false
              state.solver_running = False
              state.solver_icon="mdi-play-circle"


###############################################################
# PIPELINE CARD : Solver
###############################################################
def solver_card():
    with ui_card(title="Solver", ui_name="Solver"):
        log("info", "## Solver Selection ##")
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
                v_model=("iter_idx", 100),
                # the name of the list box
                label="Iterations",
            )

        with vuetify.VBtn("Solve",click=su2_play):
            vuetify.VIcon("{{solver_icon}}",color="purple")


###############################################################
# Solver - state changes
###############################################################
@state.change("iter_idx")
def update_material(iter_idx, **kwargs):
    #
    log("info", f"ITER value:  = {state.iter_idx}")
    #
    # we want to call a submenu
    #state.active_sub_ui = "submaterials_fluid"
    #
    # update config option value
    state.jsonData['ITER']= int(state.iter_idx)

@state.change("convergence_val")
def update_material(convergence_val, **kwargs):
    #
    # update config option value
    state.jsonData['CONV_RESIDUAL_MINVAL']= int(state.convergence_val)



# start SU2 solver
def su2_play():

    global proc_SU2

    # every time we press the button we switch the state
    state.solver_running = not state.solver_running
    if state.solver_running:
        log("info", "### SU2 solver started!")
        # change the solver button icon
        state.solver_icon="mdi-stop-circle"

        # save the cfg file
        save_json_cfg_file(state.filename_json_export,state.filename_cfg_export)
        # save the mesh file
        global root
        save_su2mesh(root,state.jsonData['MESH_FILENAME'])

        # run SU2_CFD with config.cfg
        with open(BASE / "user" / "su2.out", "w") as outfile:
          with open(BASE / "user" / "su2.err", "w") as errfile:
            proc_SU2 = subprocess.Popen(['SU2_CFD', state.filename_cfg_export],
                                cwd="user/",
                                text=True,
                                stdout=outfile,
                                stderr=errfile
                                )
        # at this point we have started the simulation
        # we can now start updating the real-time plots
        state.keep_updating = True
        log("info", f"start polling, poll =  = {proc_SU2.poll()}")

        # Wait until process terminates
        #while result.poll() is None:
        #  time.sleep(1.0)
        log("info", f"result =  = {proc_SU2}")
        log("info", f"result poll=  = {proc_SU2.poll()}")

        # periodic update of the monitor and volume result
        start_countdown(proc_SU2)


        log("info", f"result =  = {proc_SU2}")
        # save mesh
        # save config
        # save restart file
        # call su2_cfd
    else:
        state.solver_icon="mdi-play-circle"
        log("info", "### SU2 solver stopped!"),
        # we need to terminate or kill the result process here if stop is pressed
        log("info", f"process= = {type(proc_SU2)}")
        proc_SU2.terminate()

# matplotlib history
def update_convergence_fields_visibility(index, visibility):
    log("info", f"index= = {index}")
    log("info", f"visible= = {state.convergence_fields_visibility}")
    state.convergence_fields_visibility[index] = visibility
    log("info", f"visible= = {state.convergence_fields_visibility}")
    state.dirty("convergence_fields_visibility")
    log("info", f"Toggle {index} to {visibility}")


# matplotlib history
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



###############################################################################
def update_solver_dialog_card_convergence():
    log("info", f"changing state of solver_dialog_Card_convergence to: = {state.show_solver_dialog_card_convergence}")
    state.show_solver_dialog_card_convergence = not state.show_solver_dialog_card_convergence

    # if we show the card, then also update the fields that we need to show
    if state.show_solver_dialog_card_convergence==True:
      log("info", "updating list of fields")
      # note that Euler and inc_euler can be treated as compressible / incompressible as well
      log("info", state.jsonData['SOLVER'])
      log("info", state.jsonData['INC_ENERGY_EQUATION'])

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
         log("info", f"field= = {field}")
         for i in range(len(state.convergence_fields)):
            log("info", f"i= = {i," ",state.convergence_fields[i]}")
            if (field==state.convergence_fields[i]):
               log("info", "field found")
               state.convergence_fields_visibility[i] = True

      log("info", f"convergence fields: = {state.convergence_fields}")
      state.dirty('convergence_fields')
      state.dirty('convergence_fields_range')
    else:

       # the dialog is closed again: we update the state of CONV_FIELD in jsonData
         state.jsonData['CONV_FIELD']=[]
         for i in range(len(state.convergence_fields_visibility)):
            if (state.convergence_fields_visibility[i]==True):
               state.jsonData['CONV_FIELD'].append(state.convergence_fields[i])






###############################################################################
# matplotlib
def update_dialog():
    state.show_dialog = not state.show_dialog
    state.dirty('monitorLinesVisibility')
    state.dirty('monitorLinesNames')
    state.dirty('monitorLinesRange')



###############################################################################
# Read the history file
# set the names and visibility
def readHistory(filename):
    log("info", f"read_history, filename= = {filename}")
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
    # number of global iterations, assuming we start from 0 and every line is an iteration.
    # actually, we should look at Inner_Iter
    state.global_iter = len(dfrms.index)
    #log("info", f"x =  = {state.x}")
    state.ylist=[]
    for c in range(len(dfrms.columns)):
        state.ylist.append(dfrms.iloc[:,c].tolist())

    dialog_card()
    return [state.x,state.ylist]


###############################################################################
# # ##### upload ascii restart file #####
@state.change("restartFile")
def uploadRestart(restartFile, **kwargs):
  log("info", "Updating restart.csv file")
  if restartFile is None:
    state.jsonData["RESTART_SOL"] = "NO"
    log("info", "removed file")
    return

  # for .csv

  file = ClientFile(restartFile)
  try:
      filecontent = file.content.decode('utf-8')
  except:
      filecontent = file.content

  f = filecontent.splitlines()

  with open(BASE / "user" / "restart.csv",'w') as restartFile:
     restartFile.write(filecontent)

  state.jsonData["RESTART_FILENAME"] = "restart.csv"
  state.jsonData["RESTART_SOL"] = "YES"
  state.jsonData["READ_BINARY_RESTART"] = "NO"

  
  # log("info", ("Restart loaded ")


  # we reset the active field because we read or upload the restart from file as a user action
  readRestart(io.StringIO('\n'.join(f)), True)
  
  # readRestart(BASE / "user" / state.restart_filename, False)


# check if a file has a handle on it
#def has_handle(fpath):
#    for proc in psutil.process_iter():
#        try:
#            for item in proc.open_files():
#                log("info", f"item= = {item}")
#                if fpath == item.path:
#                    return True
#        except Exception:
#            pass
#
#    return False

# read the restart file
# reset_active_field is used to show the active field
def readRestart(restartFile, reset_active_field):

  # move the file to prevent that the file is overwritten while reading
  # the file can still be overwritten while renaming, but the time window is smaller
  # we also try to prevent this by not calling readRestart when we are about to write a file
  # (based on current iteration number)
  if isinstance(restartFile,str):
    os.rename(restartFile, restartFile + ".lock")
    df = pd.read_csv(restartFile+'.lock')
  else:
    df = pd.read_csv(restartFile)

  # check if the points and cells match, if not then we probably were writing to the file
  # while reading it and we just skip this update
  log("info", f"number of points read =  = {len(df)}")
  log("info", f"number of points expected =  = {grid.GetPoints().GetNumberOfPoints()}")
  if len(df) != grid.GetPoints().GetNumberOfPoints():
    return

  # construct the dataset_arrays
  datasetArrays = []
  counter=0
  for key in df.keys():
    name = key
    log("info", f"reading restart, field name =  = {name}")
    # let's skip these 
    if (name in ['PointID','x','y']):
      continue

    ArrayObject = vtk.vtkFloatArray()
    ArrayObject.SetName(name)
    # all components are scalars, no vectors for velocity
    ArrayObject.SetNumberOfComponents(1)
    # how many elements do we have?
    nElems = len(df[name])
    ArrayObject.SetNumberOfValues(nElems)
    ArrayObject.SetNumberOfTuples(nElems)

    # Nijso: TODO FIXME very slow!
    for i in range(nElems):
      ArrayObject.SetValue(i,df[name][i])

    grid.GetPointData().AddArray(ArrayObject)

    datasetArrays.append(
            {
                "text": name,
                "value": counter,
                "range": [df.min()[key],df.max()[key]],
                "type": vtkDataObject.FIELD_ASSOCIATION_POINTS,
            }
    )
    counter += 1

  state.dataset_arrays = datasetArrays
  #log("info", f"dataset =  = {datasetArrays}")
  #log("info", f"dataset_0 =  = {datasetArrays[0]}")
  #log("info", f"dataset_0 =  = {datasetArrays[0].get('text'}"))

  mesh_mapper.SetInputData(grid)
  mesh_actor.SetMapper(mesh_mapper)
  renderer.AddActor(mesh_actor)

  # we should now have the scalars available. If we update the field from an active run, do not reset the
  # active scalar field
  if reset_active_field==True:
    defaultArray = datasetArrays[0]

    mesh_mapper.SelectColorArray(defaultArray.get('text'))
    mesh_mapper.GetLookupTable().SetRange(defaultArray.get('range'))
    mesh_mapper.SetScalarVisibility(True)
    mesh_mapper.SetUseLookupTableScalarRange(True)

    # Mesh: Setup default representation to surface
    mesh_actor.GetProperty().SetRepresentationToSurface()
    mesh_actor.GetProperty().SetPointSize(1)
    #do not show the edges
    mesh_actor.GetProperty().EdgeVisibilityOff()

    # We have loaded a mesh, so enable the exporting of files
    state.export_disabled = False


  renderer.ResetCamera()
  ctrl.view_update()


###############################################################################
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
      #log("info", f"line=  = {idx,", name= ",state.monitorLinesNames[idx]," visible:",state.monitorLinesVisibility[idx]}")
      #log("info", f"__ range x =  = {min(state.x}"), " ",max(state.x))
      # only plot if the visibility is True
      if state.monitorLinesVisibility[idx]:
        #log("info", f"log("info", ing line  = {idx}")
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


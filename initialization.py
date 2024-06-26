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

# import the grid from the mesh module
from mesh import *
from vtk_helper import *

import vtk
from vtkmodules.vtkCommonDataModel import vtkDataObject

state, ctrl = server.state, server.controller

state.init_pressure = 0.0
state.init_density = 1.0
state.init_velx = 1.0
state.init_vely = 1.0
state.init_velz = 1.0
state.init_temperature = 1.0
state.init_momx = 1.0
state.init_momy = 1.0
state.init_momz = 1.0
state.init_energy = 1.0
state.init_nut = 1.0
state.init_tke = 1.0
state.init_dissipation = 1.0

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
# patch is enabled when uniform or restart has been used
state.LInitializationOption= [
  {"text": "Uniform", "value": 0},
  {"text": "From file (Restart)", "value": 1},
  {"text": "Patch", "value": 2, "disabled": True},
]

LInitializationPatch= [
  {"text": "Cube", "value": 0},
  {"text": "Cylinder", "value": 1},
  {"text": "Sphere", "value": 2},
]

# set the state variables using the json configuration file data
def set_json_initialization():
  state.initial_option_idx = 0
  if state.jsonData['RESTART_SOL']==True:
    log("info", "restarting solution from file")
    state.initial_option_idx = 1
  else:
    # note that we always restart from file, but in this case we create the file from uniform conditions
    log("info", "restarting from uniform initial conditions")
    state.initial_option_idx = 0
  state.dirty('initial_option_idx')

  if ("INC" in str(state.jsonData['SOLVER'])):
    compressible = False
  else:
    compressible = True

  # if incompressible, we check if temperature is on
  energy = False
  if (compressible == False):
    if (state.jsonData['INC_ENERGY_EQUATION']==True):
       energy = True

  if (compressible==True):
    state.init_momx = 1.0
  else:
    state.init_velx = state.jsonData['INC_VELOCITY_INIT'][0]
    state.init_vely = state.jsonData['INC_VELOCITY_INIT'][1]
    state.init_velz = state.jsonData['INC_VELOCITY_INIT'][2]
    if (energy==True):
      state.init_temperature = state.jsonData['INC_TEMPERATURE_INIT']

###############################################################
# PIPELINE CARD : Initialization
###############################################################
def initialization_card():
    with ui_card(title="Initialization", ui_name="Initialization"):
      log("info", "def initialization_card ")
      with vuetify.VContainer(fluid=True):

         # 1 row of option lists
        with vuetify.VRow(classes="pt-2"):
          with vuetify.VCol(cols="10"):

            # Then a list selection for initialization submodels
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("initial_option_idx", 0),
                # The items in the list
                #items=("representations_initial",state.LInitializationOption),
                items=("Object.values(LInitializationOption)",),
                # the name of the list box
                label="Initialize from:",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 mt-1",
            )


    # update the initial option to recompute based on upstream changes
    # this makes sure that the incompressible vs compressible subui
    # is changed when comp/incomp is changed in the physics solver

###############################################################
# Initialize - method
###############################################################
@state.change("initialization_state_idx")
def update_initial_option(initialization_state_idx, **kwargs):
    log("info", f"initialization state selection:  = {state.initialization_state_idx}")
    # but for compressible or incompressible?


@state.change("initial_option_idx")
def update_initial_option(initial_option_idx, **kwargs):
    log("info", f"initialization selection:  = {state.initial_option_idx}")
    log("info", f"restart_sol= {bool (state.initial_option_idx)}")

    # option=0 : uniform values
    # option=1 : restart from file
    # option=2 : patch
    if (state.initial_option_idx==0):
      # uniform (constant) initialization
      log("info", f"state.jsonData solve =  = {state.jsonData["SOLVER"]}")
      if "INC" in (state.jsonData["SOLVER"]):
        log("info", "initialization for incompressible")
        if state.active_ui=="Initialization":
          state.active_sub_ui = "subinitialization_inc"
      else:
        log("info", "initialization for compressible")
        if state.active_ui=="Initialization":
          state.active_sub_ui = "subinitialization_comp"
    elif (state.initial_option_idx==1):
      log("info", "initialization from file")
      if state.active_ui=="Initialization":
        state.active_sub_ui = "subinitialization_file"
    else:
      # patch
      if state.active_ui=="Initialization":
        state.active_sub_ui = "subinitialization_patch"


@state.change("initial_patch_idx")
def update_initial_patch(initial_patch_idx, **kwargs):
    log("info", f"patch selection:  = {initial_patch_idx}")



#@state.change("initialize")
def initialize_uniform():

  log("info", "initialize solution")

  # construct the dataset_arrays
  datasetArrays = []
  counter=0

  FieldNames=[]
  FieldValues=[]
  if ("INC" in str(state.jsonData['SOLVER'])):
    compressible = False
  else:
    compressible = True

  # if incompressible, we check if temperature is on
  energy = False
  if (compressible == False):
    if (state.jsonData['INC_ENERGY_EQUATION']==True):
       energy = True

  if (compressible==True):
    log("info", "compressible")
    FieldNames.extend(["Density","Momentum_x","Momentum_y"])
    FieldValues.extend([state.init_density,state.init_momx,state.init_momy])
    if state.nDim==3:
        FieldNames.append("Momentum_z")
        FieldValues.append(state.init_momz)
    FieldNames.append("Energy")
    FieldValues.append(state.init_energy)
  else:
    log("info", "incompressible")
    log("info", f"pressure: = {state.init_pressure}")
    log("info", f"velocity: = {state.init_velx," ",state.init_vely}")
    FieldNames.extend(["Pressure","Velocity_x","Velocity_y"])
    FieldValues.extend([state.init_pressure,state.init_velx,state.init_vely])
    if state.nDim==3:
        FieldNames.append("Velocity_z")
        FieldValues.append(state.init_velz)
    if energy==True:
      FieldNames.append("Temperature")
      FieldValues.append(state.init_temperature)

  turbmodelSA = False
  turbmodelSST = False
  turbulence = False
  if ("RANS" in str(state.jsonData['SOLVER'])):
    turbulence = True
    if state.jsonData['KIND_TURB_MODEL'] == "SA":
      turbmodelSA=True
    elif state.jsonData['KIND_TURB_MODEL'] == "SST":
      turbmodelSST = True

  if (turbmodelSA == True):
    FieldNames.append("Nu_Tilde")
    FieldValues.append(state.init_nut)
  elif (turbmodelSST == True):
    FieldNames.extend(["Tke","Dissipation"])
    FieldValues.extend([state.init_tke,state.init_dissipation])

  log("info", f"fieldnames= = {FieldNames}")

  nPoints = grid.GetPoints().GetNumberOfPoints()
  log("info", f"number of points =  = {nPoints}")


  for i in range(len(FieldNames)):
    name = FieldNames[i]
    value = FieldValues[i]

    ArrayObject = vtk.vtkFloatArray()
    ArrayObject.SetName(name)
    # all components are scalars, no vectors for velocity
    ArrayObject.SetNumberOfComponents(1)
    # how many elements do we have?
    ArrayObject.SetNumberOfValues(nPoints)
    ArrayObject.SetNumberOfTuples(nPoints)

    log("info", f"name =  = {name, " , value = ",value }")

    # Nijso: TODO FIXME reported to be a slow process.
    for i in range(nPoints):
      ArrayObject.SetValue(i,float(value))

    grid.GetPointData().AddArray(ArrayObject)

    # note that range is equal because value is uniform
    datasetArrays.append(
            {
                "text": name,
                "value": counter,
                "range": [float(value),float(value)],
                "type": vtkDataObject.FIELD_ASSOCIATION_POINTS,
            }
    )
    counter += 1


  # we should now have the scalars available...
  defaultArray = datasetArrays[0]
  state.dataset_arrays = datasetArrays
  #log("info", f"dataset =  = {datasetArrays}")
  #log("info", f"dataset_0 =  = {datasetArrays[0]}")
  #log("info", f"dataset_0 =  = {datasetArrays[0].get('text'}"))

  mesh_mapper.SetInputData(grid)
  mesh_actor.SetMapper(mesh_mapper)
  renderer.AddActor(mesh_actor)

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

  # save the restart file (should be a separate save/export button)
  # this routine should be in su2_io.py
  # note that we save the file in the solution file, and we always start from
  # the saved file
  solution_filename = state.jsonData['SOLUTION_FILENAME'] + ".csv"
  with open(BASE / "user" / solution_filename,'w') as f:
    fields = ["PointID","x","y"]
    if (state.nDim==3):
        fields.append("z")
    fields.extend(FieldNames)
    # convert to string, including double quotes
    stringfields = ', '.join(f'"{name}"' for name in fields) +"\n"
    f.write(stringfields)
    #log("info", grid.GetPointData().GetNumberOfArrays())
    #log("info", grid.GetPointData().GetArrayName(i))
    # now loop over points and get the coordinates

    # loop over all points
    for p in range(nPoints):
        # loop over all field names to be saved
        coord = grid.GetPoint(p)
        datalist = str(p) + "," + str(coord[0]) + "," + str(coord[1])
        if state.nDim==3:
            datalist = datalist + "," + str(coord[2])
        for name in FieldNames:
            datapoint =  grid.GetPointData().GetArray(name).GetValue(p)
            datalist = datalist + "," + str(datapoint)
        datalist = datalist+"\n"
        f.write(datalist)
        #log("info", p, " ",grid.GetPoint(p))
  f.close()

  log("info", f"options= = {state.LInitializationOption}")
  # switch patch option on
  state.LInitializationOption[2]= {"text": "Patch", "value": 2, "disabled": False}
  log("info", f"options= = {state.LInitializationOption}")
  state.dirty('LInitializationOption')




def initialization_patch_subcard():
  log("info", "initialization_file_subcard:: set the ui_subcard")
  with ui_subcard(title="initialization from file", sub_ui_name="subinitialization_patch"):
    with vuetify.VContainer(fluid=True):
      # ####################################################### #
      with vuetify.VRow(classes="py-0 my-0"):
        with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
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
                #disabled = True,
            )


def initialization_file_subcard():
  log("info", "initialization_file_subcard:: set the ui_subcard")
  with ui_subcard(title="initialization from file", sub_ui_name="subinitialization_file"):
    with vuetify.VContainer(fluid=True):
      # ####################################################### #
      with vuetify.VRow(classes="py-0 my-0"):
        with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):    # restart file input inside the toolbar
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
            label="Load Restart File",
            dense=True,
            hide_details=True,
            style="max-width: 300px;",
            accept=".dat, .csv",
            __properties=["accept"],
          )


###############################################################
# PIPELINE SUBCARD : INITIALIZATION
###############################################################
# secondary card
def initialization_uniform_subcard():

    log("info", "initialization_uniform_subcard:: set the ui_subcard")
    #with vuetify.VContainer(fluid=True):
    # 1 row of option lists
    energy = bool(state.jsonData['INC_ENERGY_EQUATION'])
    log("info", f"energy equation= = {energy}")
    # for the card to be visible, we have to set state.active_sub_ui = subinitialization_inc
    with ui_subcard(title="initialization (incompressible)", sub_ui_name="subinitialization_inc"):
      with vuetify.VContainer(fluid=True):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_pressure", 1.0),
              # the name of the list box
              label="pressure",
            )
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_velx", 1.0),
              # the name of the list box
              label="Velocity X",
            )
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_vely", 1.0),
              # the name of the list box
              label="Velocity_Y",
            )
      with vuetify.VContainer(fluid=True, v_if=("nDim==3")):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_velz", 1.0),
              # the name of the list box
              label="Velocity_Z",
              #disabled=("nDim==2",0)
            )
      with vuetify.VContainer(fluid=True, v_if=("jsonData['INC_ENERGY_EQUATION']==1")):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_temperature", 300.0),
              # the name of the list box
              label="temperature",
              # is temperature disabled?
              #disabled= ("jsonData['INC_ENERGY_EQUATION']==0",0)
            )
      # turbulence quantities (nijso TODO: add turbulence intensity and turb ratio and computed results for k,w)
      with vuetify.VContainer(fluid=True, v_if=("jsonData['KIND_TURB_MODEL']=='SA' ")):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_nu_tilde_idx", 1.2),
              # the name of the list box
              label="nu_tilde",
            )
      # turbulence quantities
      with vuetify.VContainer(fluid=True, v_if=("jsonData['KIND_TURB_MODEL']=='SST' ")):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_sst_k_idx", 1.2),
              # the name of the list box
              label="tke",
            )
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_sst_w_idx", 100),
              # the name of the list box
              label="dissipation",
            )

      with vuetify.VContainer(fluid=True):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="12"):
            with vuetify.VBtn("Initialize",click=initialize_uniform):
              vuetify.VIcon("{{solver_icon}}",color="purple")

    # use a vcontainer if you want to have a border around everything
    #with vuetify.VContainer(fluid=True):
    # 1 row of option lists
    # for the card to be visible, we have to set state.active_sub_ui = subinitialization
    with ui_subcard(title="initialization (compressible)", sub_ui_name="subinitialization_comp"):
      with vuetify.VContainer(fluid=True):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_density", 1.2),
              # the name of the list box
              label="density",
            )
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_momx", 1.0),
              # the name of the list box
              label="Momentum X",
            )
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_momy", 1.0),
              # the name of the list box
              label="Momentum Y",
            )

      with vuetify.VContainer(fluid=True, v_if=("nDim==3")):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_momz", 1.0),
              # the name of the list box
              label="Momentum Z",
            )

      with vuetify.VContainer(fluid=True):
        # ####################################################### #
        with vuetify.VRow(classes="py-0 my-0"):
          with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            vuetify.VTextField(
              # What to do when something is selected
              v_model=("init_energy", 1.0),
              # the name of the list box
              label="energy",
            )

          # turbulence quantities (nijso TODO: add turbulence intensity and turb ratio and computed results for k,w)
          with vuetify.VContainer(fluid=True, v_if=("jsonData['KIND_TURB_MODEL']=='SA' ")):
            # ####################################################### #
            with vuetify.VRow(classes="py-0 my-0"):
              with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
                vuetify.VTextField(
                  # What to do when something is selected
                  v_model=("init_nu_tilde_idx", 1.2),
                  # the name of the list box
                  label="nu_tilde",
                )
          # turbulence quantities
          with vuetify.VContainer(fluid=True, v_if=("jsonData['KIND_TURB_MODEL']=='SST' ")):
            # ####################################################### #
            with vuetify.VRow(classes="py-0 my-0"):
              with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
                vuetify.VTextField(
                  # What to do when something is selected
                  v_model=("init_sst_k_idx", 1.2),
                  # the name of the list box
                  label="tke",
                )
            with vuetify.VRow(classes="py-0 my-0"):
              with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
                vuetify.VTextField(
                  # What to do when something is selected
                  v_model=("init_sst_w_idx", 100),
                  # the name of the list box
                  label="dissipation",
                )

          with vuetify.VContainer(fluid=True):
            # ####################################################### #
            with vuetify.VRow(classes="py-0 my-0"):
              with vuetify.VCol(cols="12"):
                with vuetify.VBtn("Initialize",click=initialize_uniform):
                  vuetify.VIcon("{{solver_icon}}",color="purple")




    # for the card to be visible, we have to set state.active_sub_ui = "subinitialization_none"
    with ui_subcard(title="no subinitialization", sub_ui_name="subinitialization_none"):
       vuetify.VTextarea(
                label="no subinitialization:",
                rows="5",
                v_model=("subinitializationtext", state.subinitializationtext),
        )

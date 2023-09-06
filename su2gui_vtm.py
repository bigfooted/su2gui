r"""
Version for trame 1.x - https://github.com/Kitware/trame/blob/release-v1/examples/VTK/Applications/VTPViewer/app.py
Delta v1..v2          - https://github.com/Kitware/trame/commit/8d7fd7d3f11360637315f61ec8c66154d3b1af69
This example reads a .vtm file, shows the boundaries in a git-tree, lights up the boundaries when you select the
boundary in the git-tree, and when you select the internal element, you can still see the scalar fields.
"""
import os, copy
import pandas as pd
from trame.app import get_server
from trame.app.file_upload import ClientFile

from trame.ui.vuetify import SinglePageWithDrawerLayout
#from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, trame, vtk as vtk_widgets
#import itertools
from datetime import date
# Import json setup for writing the config file in json and cfg file format.
from su2_json import *
# Export su2 mesh file.
from su2_io import export_files

# Definition of ui_card and the server.
from uicard import ui_card, server

#############################################################################
# Gittree menu                                                              #
# We have defined each of the tabs in its own module and we import it here. #
# We then call the card in the SinglePageWithDrawerLayout() function.       #
#############################################################################
# gittree menu : import physics tab                                         #
from physics import *
# gittree menu : import materials tab                                       #
from materials import *
# gittree menu : import numerics tab                                        #
from numerics import *
# gittree menu : import solver tab                                          #
from solver import *
#############################################################################


from pipeline import PipelineManager
from pathlib import Path
BASE = Path(__file__).parent
from trame.assets.local import LocalFileManager

local_file_manager = LocalFileManager(__file__)
local_file_manager.url("collapsed", BASE / "icons/chevron-up.svg")
local_file_manager.url("collapsible", BASE / "icons/chevron-down.svg")

import vtk
# vtm reader
#from paraview.vtk.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.web.utils import mesh as vtk_mesh
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter

from vtkmodules.vtkCommonColor import vtkNamedColors

from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from vtkmodules.vtkCommonDataModel import vtkMultiBlockDataSet

from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON,
    VTK_LINE,
    VTK_POLYGON,
    VTK_QUAD,
    VTK_TETRA,
    VTK_TRIANGLE,
    VTK_PYRAMID,
    VTK_WEDGE,
    VTK_TRIANGLE_STRIP,
    VTK_VERTEX,
    vtkUnstructuredGrid)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
# offscreen rendering, no additional pop-up window
renderWindow.SetOffScreenRendering(1)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

state, ctrl = server.state, server.controller

state.BCDictList = []
# important for the interactive ui
state.setdefault("active_ui", None)

# disable the export file button
state.export_disabled=True

# (solver.py) disable the solve button
state.su2_solve_disabled=False

# solver settings
# current solver icon
state.solver_icon = "mdi-play-circle"
# current running state
state.solver_running = False

# the imported mesh block and boundary blocks
# must be state or else it cannot be an argument to click
#state.multiblockb1 = vtkMultiBlockDataSet()
mb1 = vtkMultiBlockDataSet()
state.su2_meshfile="mesh_out.su2"

colors = vtkNamedColors()


# define initial square (counterclockwise)
x = [[0.0, 0.0, 0.0],[1.0, 0.0, 0.0],[1.0, 1.0, 0.0],[0.0, 1.0, 0.0]]
pts=[[0,1,2,3]]
points = vtk.vtkPoints()
for i in range(0, len(x)):
        points.InsertPoint(i, x[i])
grid = vtkUnstructuredGrid()
grid.SetPoints(points)
grid.InsertNextCell(VTK_QUAD,4,pts[0])

# list of all the mesh actors (boundaries)
state.selectedBoundary = 0
mesh_actor_list = [{"id":0,"name":"None","mesh":0}]

# Mesh
mesh_mapper = vtkDataSetMapper()


mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
mesh_actor.SetObjectName("initial_square")

# Mesh: Setup default representation to surface
mesh_actor.GetProperty().SetRepresentationToSurface()
mesh_actor.GetProperty().SetPointSize(1)
mesh_actor.GetProperty().EdgeVisibilityOn()
renderer.AddActor(mesh_actor)

###################################
# ##### gradient background ##### #
###################################
# bottom: white
renderer.SetBackground(1., 1., 1.)
# top: light blue
renderer.SetBackground2(0.6, 0.8, 1.0)
# activate gradient background
renderer.GradientBackgroundOn()
###################################


# Extract Array/Field information
datasetArrays = []
name = "Solid"
ArrayObject = vtk.vtkFloatArray()
ArrayObject.SetName(name)
# all components are scalars, no vectors for velocity
ArrayObject.SetNumberOfComponents(1)
# how many elements do we have?
nElems = 1
ArrayObject.SetNumberOfValues(nElems)
ArrayObject.SetNumberOfTuples(4)


# Nijso: TODO FIXME very slow!
for i in range(nElems):
  ArrayObject.SetValue(i,1.0)

grid.GetPointData().AddArray(ArrayObject)
# as soon as we add the array, it is being used for coloring.


datasetArrays.append(
    {
        "text": name,
        "value": 0,
        "range": [1.0,1.0],
        "type": vtkDataObject.FIELD_ASSOCIATION_POINTS,
    }
)
default_array = datasetArrays[0]
default_min, default_max = default_array.get("range")
state.dataset_arrays= datasetArrays
print("dataset_arrays = ",state.dataset_arrays)

mesh_mapper.SetInputData(grid)
mesh_mapper.SelectColorArray(default_array.get("text"))
mesh_mapper.GetLookupTable().SetRange(default_min, default_max)
mesh_mapper.SetScalarModeToUsePointFieldData()
mesh_mapper.SetScalarVisibility(True)
mesh_mapper.SetUseLookupTableScalarRange(True)

#mesh_mapper.ScalarVisibilityOff()
#mesh_actor.GetProperty().SetColor(colors.GetColor3d('Peacock'))

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

pipeline = PipelineManager(state, "git_tree")

# main menu, note that only these are collapsible
# These are head nodes. boundary for instance are all subnodes sharing one head node
# 1
id_root       = pipeline.add_node(                      name="Mesh",
                                  subui="none", visible=1, color="#9C27B0", actions=["collapsible"])
# 2
id_physics    = pipeline.add_node(parent=id_root,       name="Physics",
                                  subui="subphysics", visible=1, color="#42A5F5", actions=["collapsible"])
# 3
id_materials  = pipeline.add_node(parent=id_physics,    name="Materials",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 4
id_numerics   = pipeline.add_node(parent=id_materials,  name="Numerics",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 5
id_boundaries = pipeline.add_node(parent=id_numerics,   name="Boundaries",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 6
id_initial    = pipeline.add_node(parent=id_boundaries, name="Initialization",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 7
id_monitor    = pipeline.add_node(parent=id_initial,    name="Monitor",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 8
id_fileio     = pipeline.add_node(parent=id_monitor,    name="File I/O",
                                  subui="none", visible=1, color="#42A5F5", actions=["collapsible"])
# 9
id_solver     = pipeline.add_node(parent=id_fileio,    name="Solver",
                                  subui="none", visible=1, color="#00ACC1", actions=["collapsible"])

pipeline.update()

state.active_id=0
state.active_sub_ui = "none"

state.counter = 0

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

def actives_change(ids):
    print("ids = ",ids)
    _id = ids[0]

    state.active_id = _id

    state.boundaryText=_id
    print("active id = ",state.active_id)
    # get boundary name belonging to ID
    _name = pipeline.get_node(_id)
    # get the headnode of this node
    _headnode = _name['headnode']
    print("headnode=",_headnode)

    # check if we need to show a submenu
    _subui = _name['subui']
    # whatever the value, we update the pipeline with it
    state.active_sub_ui = _subui
    print("subnode=",_subui)

    print("active name =",_name)
    print("children:",pipeline._children_map)

    _name = _name['name']
    print("active name =",_name)
    selectedBoundary = next((item for item in mesh_actor_list if item["name"] == _name), None)
    print("mesh_actor_list = ",mesh_actor_list)
    if not selectedBoundary==None:
      state.selectedBoundaryName = selectedBoundary["name"]
    else:
      state.selectedBoundaryName = "None"

    # get list of all actors, loop and color the selected actor
    actorlist = vtk.vtkActorCollection()
    actorlist = renderer.GetActors()
    actorlist.InitTraversal()

    internal=False
    print("selected item = ",state.selectedBoundaryName)
    if state.selectedBoundaryName=="internal":
        print("internal selected")
        internal=True

    for a in range(0, actorlist.GetNumberOfItems()):
        actor = actorlist.GetNextActor()
        print("getnextactor: name =",actor.GetObjectName())
        if actor.GetObjectName() == state.selectedBoundaryName:
            # current actor is selected, we switch it on
            actor.VisibilityOn()
            print("we have found the actor!")
            if (internal==False):
              # if it is not an internal, we highlight it in yellow
              actor.GetProperty().SetColor(colors.GetColor3d('yellow'))
        elif actor.GetObjectName()=="internal":
                # current actor is internal but it is not selected, then we switch it off
                print("actor is internal but not selected, we switch it off")
                actor.VisibilityOff()
        else:
            # current actor is not selected and also not internal, then we switch it on but do not highlight
            if (internal==True):
                # then the actor is internal: switch off all other actors, only show this one
                actor.VisibilityOff()
            else:
              # if we do not have internal selected, then show everything except internal
              actor.VisibilityOn()
              actor.GetProperty().SetColor(colors.GetColor3d('floralwhite'))

    # if the actor name is "internal", then we switch off all other actors
    # and we use the scalars for coloring
    # if the actor name is not internal, then we switch off internal


    ctrl.view_update()

    print("state=",_id)
    # active ui is the head node of the gittree
    state.active_ui = _headnode

    # check if we need to show a subui

###############################################################
# PIPELINE CARD : BOUNDARY
###############################################################
state.meshText="meshtext"
state.boundaryText="boundtext"

def boundary_card():
    with ui_card(title="Boundary", ui_name="Boundaries"):
        print("## Boundary Selection ##")
        vuetify.VTextarea(
                label="boundary info:",
                rows="5",
                v_model=("boundaryText", "bound"),
        )


#def new_boundary_card():
#    with ui_card(title="NewBoundary", ui_name="newboundary"):
#
#        vuetify.VTextarea(
#                label="boundary info:",
#                rows="5",
#                v_model=("selectedBoundaryName", "bound"),
#        )

def mesh_card():
    with ui_card(title="Mesh", ui_name="Mesh"):
        print("## Mesh Selection ##")
        vuetify.VTextarea(
                label="mesh info:",
                rows="5",
                v_model=("meshText", "blablabla"),
        )


# export su2 file
def export_files_01(su2_filename):
    print("********** export_files_01 **********\n")
      # add the filename to the json database
    state.jsonData['MESH_FILENAME'] = su2_filename
    export_files(mb1,su2_filename)



# Color By Callbacks
def color_by_array(actor, array):
    print("change color by array")
    _min, _max = array.get("range")
    mapper = actor.GetMapper()
    mapper.SelectColorArray(array.get("text"))
    mapper.GetLookupTable().SetRange(_min, _max)

    if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mesh_mapper.SetScalarModeToUsePointFieldData()
    else:
        mesh_mapper.SetScalarModeToUseCellFieldData()
    mapper.SetScalarVisibility(True)
    mapper.SetUseLookupTableScalarRange(True)


@state.change("mesh_color_array_idx")
def update_mesh_color_by_name(mesh_color_array_idx, **kwargs):
    print("change mesh color by array")
    array = state.dataset_arrays[mesh_color_array_idx]
    print("array = ",array)
    color_by_array(mesh_actor, array)
    ctrl.view_update()

@state.change("active_sub_ui")
def update_active_sub_ui(active_sub_ui, **kwargs):
    print("change active_sub_ui = ",active_sub_ui)
    if not(state.active_id ==0):
      # get boundary name belonging to ID
      _name = pipeline.get_node(state.active_id)['name']
      print("name=",_name)
      if (_name=="Physics"):
        pipeline.update_node_value("Physics","subui",active_sub_ui)

      #array = state.dataset_arrays[mesh_color_array_idx]
      #print("array = ",array)
      #color_by_array(mesh_actor, array)
      ctrl.view_update()


# some default options
noSSTSelected = True
noBodyForceSelected = True
noViscositySelected = False
state.noSST = noSSTSelected
# compressible
state.compressible = True
state.submodeltext = "none"
# the SA options
state.SAOptions={"NONE":True,
                 "QCR2000":False,
                 "WITHFT2":False,
                 "COMPRESSIBILITY":False,
                 "EDWARDS":False,
                 "ROTATION":False,
                 "BCM":False,
                 "NEGATIVE":False,
                 "EXPERIMENTAL":True
                }

# initial value for the materials-fluidmodel list
state.LMaterialsFluid = LMaterialsFluidComp

# save the new json configuration file #
# TODO: why do all the states get checked at startup?
# TODO: when we click the save button, the icon color changes
def nijso_list_change():
    print("write config file"),
    state.counter = state.counter + 1
    print("counter=",state.counter)
    if (state.counter==2):
      print("counter=",state.counter)
    with open('config_new.json','w') as jsonOutputFile:
        json.dump(state.jsonData,jsonOutputFile,sort_keys=True,indent=4,ensure_ascii=False)

    # now convert the json file to a cfg file
    with open('config_new.cfg','w') as f:
      f.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
      f.write("%                                                                              %\n")
      f.write("% SU2 configuration file                                                       %\n")
      f.write("% Case description:                                                            %\n")
      f.write("% Author:                                                                      %\n")
      s = "% Date: " \
        + str(date.today()) \
        + "                                                             %\n"
      f.write(s)
      f.write("% SU2 version:                                                                 %\n")
      f.write("%                                                                              %\n")
      f.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
      #for k in state.jsonData:
      for attribute, value in state.jsonData.items():
        print(attribute, value)
        # convert boolean
        if isinstance(value, bool):
            if value==True:
                value="YES"
            else:
                value="NO"
        # we can have lists or lists of lists
        # we can simply flatten the list, remove the quotations,
        # convert square brackets to round brackets and done.
        if isinstance(value, list):
          #flatlist = [x for row in value for x in row]
          #flatlist = sum(value,[])
          #flatlist = list(itertools.chain(*value))
          flat_list = []
          for sublist in value:
            print(sublist)
            if isinstance(sublist,list):
              for num in sublist:
                flat_list.append(num)
            else:
              flat_list.append(sublist)

          flatlist = ', '.join(str(e) for e in flat_list)
          value = "(" + flatlist + ")"


        filestring=str(attribute) + "= " + str(value) + "\n"
        f.write(filestring)



###############################################################
# FILES
###############################################################
@state.change("file_upload")
def load_client_files(file_upload, **kwargs):
    global pipeline
    # remove the added boundary conditions in the pipeline
    print("read file")
    print("***************************************")
    pipeline.remove_right_subnode("Boundaries")
    print("***************************************")
    print("pipeline=",pipeline)

    del mesh_actor_list[:]

    ## file from the client
    #file = ClientFile(file_upload)
    file = file_upload

    if file is None or isinstance(file,list):
        return

    # remove all actors
    renderer.RemoveAllViewProps()

    # these are the scalar fields of the paraview file
    field = "solid"
    fields = {
        "solid": {"value": "solid", "text": "Solid color", "range": [0, 1]},
    }
    #meshes = []
    filesOutput = []

    ## file from the client
    #file = ClientFile(file_upload)
    #file = file_upload

    filename = file_upload.get("name")
    file_size = file_upload.get("size")

    #file_binary_content = file_upload.get(
    #    "content"
    #)  # can be either list(bytes, ...), or bytes
    #
    #with open(filename, "wb") as binary_file:
    #    # uploads are sent in chunks of 2Mb, so we need to join them
    #    file_binary_content = b"".join(file_binary_content)
    #    binary_file.write(file_binary_content)

    if not file.get("content"):
            return
    else:

            # necessary to clear the cell data
            grid.Reset()

            bytes = file.get("content")
            filesOutput.append({"name": filename, "size": file_size})

            # the vtm reader
            reader = vtk.vtkXMLMultiBlockDataReader()

            print("reading multiblock file")

            # ***** BASE PATH ***** #
            base_path = "user/nijso/"

            filename = base_path + filename

            print("file name = ",filename)


            # for the mesh info display
            state.meshText = "filename: " + filename + "\n"
            state.meshText += "filesize: " + str(file.get("size")) + "\n"

            reader.SetFileName(filename)
            reader.Update()
            mb = reader.GetOutput()
            # nr of external blocks, should be 1
            print("nr of external blocks = ",mb.GetNumberOfBlocks())
            global mb1
            mb1 = mb.GetBlock(0)
            print("type=",type(mb1))
            print("nr of blocks inside block = ",mb1.GetNumberOfBlocks())

            blockNames=[]
            for i in range(mb1.GetNumberOfBlocks()):
                print("number of internal blocks = ", i+1," / ", mb1.GetNumberOfBlocks() )
                data = mb1.GetBlock(i)
                name = mb1.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
                print("metadata block name = ",name)
                blockNames.append(
                    {
                        "text": name,
                        "value": i,
                    }
                )
            # we now get only the first 2 blocks, if there are more we give a warning
            if (mb1.GetNumberOfBlocks()>2) :
                print("warning, more than 2 blocks found, we only read the first 2 blocks, which should be internal and boundary blocks")

            internalBlock = mb1.GetBlock(0)
            print("nr of blocks inside internal block = ",internalBlock.GetNumberOfBlocks())
            boundaryBlock = mb1.GetBlock(1)
            print("nr of blocks inside block = ",boundaryBlock.GetNumberOfBlocks())

            #print(dir(internalBlock))
            # nr of data in internal block
            NELEM = internalBlock.GetNumberOfCells()
            NPOINT = internalBlock.GetNumberOfPoints()
            BOUND=[0,0,0,0,0,0]
            internalBlock.GetBounds(BOUND)
            # for the mesh info display
            state.meshText += "Number of cells: " + str(NELEM) + "\n"
            state.meshText += "Number of points: " + str(NPOINT) + "\n"
            state.meshText += "bounds: " + str(BOUND) + "\n"


            internalNames=[]
            for i in range(internalBlock.GetNumberOfBlocks()):
                print("number of internal elements = ", i+1," / ", internalBlock.GetNumberOfBlocks() )
                data = internalBlock.GetBlock(i)
                #print(dir(data))
                #print(data)
                #for p in range(NPOINT):
                #  print(p," ",data.GetPoint(p))

                name = internalBlock.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
                print("metadata block name = ",name)
                internalNames.append(
                    {
                        "text": name,
                        "value": i,
                    }
                )

            boundaryNames=[]
            for i in range(boundaryBlock.GetNumberOfBlocks()):
                print("number of boundary blocks = ", i+1," / ", boundaryBlock.GetNumberOfBlocks() )
                data = boundaryBlock.GetBlock(i)
                name = boundaryBlock.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
                print("metadata block name = ",name)
                boundaryNames.append(
                    {
                        "text": name,
                        "value": i,
                    }
                )

            # internal mesh
            print("getting the single element from the internal block")
            grid = vtk.vtkUnstructuredGrid.SafeDownCast(internalBlock.GetBlock(0))

            # boundary meshes
            ds_b = []
            for i in range(boundaryBlock.GetNumberOfBlocks()):
              ds_b.append(vtk.vtkUnstructuredGrid.SafeDownCast(boundaryBlock.GetBlock(i)))


             # coloring by scalar field
            datasetArrays = []

            pd = grid.GetPointData()
            nb_arrays = pd.GetNumberOfArrays()
            for i in range(nb_arrays):
                array = pd.GetArray(i)
                name = array.GetName()
                min, max = array.GetRange(-1)

                grid.GetPointData().AddArray(array)

                datasetArrays.append(
                    {
                    "text": name,
                    "value": i,
                    "range": [min, max],
                    "type": vtkDataObject.FIELD_ASSOCIATION_POINTS,
                    }
                )



    defaultArray = datasetArrays[0]
    state.dataset_arrays = datasetArrays
    print("dataset = ",datasetArrays)
    print("dataset_0 = ",datasetArrays[0])
    print("dataset_0 = ",datasetArrays[0].get('text'))


    # Mesh - add mesh to the renderer
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
    mesh_actor.GetProperty().EdgeVisibilityOff()
    mesh_actor.SetObjectName("internal")
    mesh_actor.VisibilityOff()

    boundary_id = 101
    i = 0
    for bcName in boundaryNames:
        mesh_mapper_b1 = vtkDataSetMapper()
        mesh_mapper_b1.ScalarVisibilityOff()
        mesh_actor_b1 = vtkActor()
        mesh_actor_b1.GetProperty().SetColor(colors.GetColor3d('Peacock'))

        mesh_mapper_b1.SetInputData(ds_b[i])
        i += 1
        mesh_actor_b1.SetMapper(mesh_mapper_b1)
        mesh_actor_b1.SetObjectName(bcName.get("text"))
        renderer.AddActor(mesh_actor_b1)
        mesh_actor_list.append({"id":boundary_id,"name":bcName.get("text"), "mesh":mesh_actor_b1})
        boundary_id += 1

    mesh_actor_list.append({"id":boundary_id,"name":"internal", "mesh":mesh_actor})
    boundaryNames.append(
                            {
                        "text": "internal",
                        "value": boundaryBlock.GetNumberOfBlocks()+1,
                    }
    )



    state.field = field
    state.fields = fields
    state.files = filesOutput

    for bcName in boundaryNames:
       print("boundary name=",bcName.get("text"))
       # add the boundaries to the right tree and not the left tree
       id_aa = pipeline.append_node(parent_name="Boundaries", name=bcName.get("text"), left=False, subui="none", visible=1, color="#2962FF")
    print("updated pipeline",pipeline)

    # We have loaded a mesh, so enable the exporting of files
    state.export_disabled = False

    renderer.ResetCamera()
    ctrl.view_update()
    pass

# -----------------------------------------------------------------------------
# GUI elements
# -----------------------------------------------------------------------------

# collapse or expand the gittree
def on_action(event):
    #print("on_action", event)
    _id = event.get("id")
    _action = event.get("action")
    if _action.startswith("collap"):
        print(pipeline.toggle_collapsed(_id))

def on_event(event):
    print(event)

# git tree in the left drawer
def pipeline_widget():
    trame.GitTree(
        sources = ("git_tree", pipeline),
        ### collabsable gittree: ###
        action_map=("icons", local_file_manager.assets),
        # size of the icon
        action_size=25,
        width=350,
        action=(on_action, "[$event]"),
        actives_change=(actives_change, "[$event]"),
    )

# buttons in the top header

def standard_buttons():
    # export su2 mesh file button
    #global mb1
    #print("mb1 = ",mb1)
    #with vuetify.VBtn("{{ mb1 }}",icon=True, click=(export_files,"[mb1]"), disabled=("export_disabled",True)):
    #    vuetify.VIcon("mdi-download-box-outline")
    with vuetify.VBtn("download",click=(export_files_01,"[su2_meshfile]")):
        vuetify.VIcon("mdi-download-box-outline")

    with vuetify.VBtn(icon=True, click=nijso_list_change, disabled=("export_disabled",True)):
        vuetify.VIcon("mdi-lightbulb-outline")

    #
    vuetify.VCheckbox(
        v_model=("viewMode", "local"),
        on_icon="mdi-lan-disconnect",
        off_icon="mdi-lan-connect",
        true_value="local",
        false_value="remote",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )

    # reset the view
    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-crop-free")

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

state.trame__title = "File loading"

state.fields = []
#state.meshes = []

with SinglePageWithDrawerLayout(server) as layout:

    # text inside the toolbar
    layout.title.set_text("SU2 GUI")

    with layout.toolbar:

        # vertical spacer inside the toolbar
        vuetify.VSpacer()

        # vertical divider inside the toolbar (solid line)
        vuetify.VDivider(vertical=True, classes="mx-2")
        standard_buttons()
        vuetify.VDivider(vertical=True, classes="mx-2")

        ######################################################
        # scalar selection field inside the top toolbar
        vuetify.VSelect(
            # Color By
            label="Color by",
            v_model=("mesh_color_array_idx", 0),
            #items=("array_list", datasetArrays),
            items=("Object.values(dataset_arrays)",),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
            #v_model=("field", "solid"),
            #items=("Object.values(fields)",),
            #style="max-width: 200px;",
            #classes="mr-4",
        )
        ######################################################

        # file input inside the top toolbar
        vuetify.VFileInput(
            # read more than one file
            multiple=False,
            background_color="white",
            # the icon in front of the file input
            prepend_icon="mdi-file",
            show_size=True,
            small_chips=True,
            truncate_length=25,
            v_model=("file_upload", None),
            dense=True,
            hide_details=True,
            style="max-width: 300px;",
            # only accepts paraview .vtm files
            accept=".vtm",
            __properties=["accept"],
        )

        # progress inside the toolbar
        vuetify.VProgressLinear(
            indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
        )

        #trame.ClientStateChange(name="meshes", change=ctrl.view_reset_camera)

    # left side menu
    with layout.drawer as drawer:
        # drawer components
        drawer.width = 400
        # git pipeline widget (defined below)
        pipeline_widget()
        # simple divider
        vuetify.VDivider(classes="mb-2")
        #
        boundary_card()
        #
        physics_card()
        physics_subcard()
        #
        materials_card()
        materials_subcard()
        #
        numerics_card()
        #
        #new_boundary_card()
        mesh_card()
        #
        solver_card()
        #
        pass

    print("setting up layout content")
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
            style="position: relative;"
        ):

            #view = vtk_widgets.VtkRemoteView(renderWindow)
            view = vtk_widgets.VtkRemoteView(renderWindow)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
            ctrl.on_server_ready.add(view.update)

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()

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

    # nijso: hardcode internal as selected mesh
    #state.selectedBoundaryName = "internal"

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
    jsonData['MESH_FILENAME'] = su2_filename
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
        json.dump(jsonData,jsonOutputFile,sort_keys=True,indent=4,ensure_ascii=False)

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
      #for k in jsonData:
      for attribute, value in jsonData.items():
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


# load SU2 .su2 mesh file
@state.change("file_upload")
def load_client_files(file_upload, **kwargs):
    global pipeline
    # remove the added boundary conditions in the pipeline

    print("***************************************")
    pipeline.remove_right_subnode("Boundaries")
    print("***************************************")
    print("pipeline=",pipeline)

    del mesh_actor_list[:]

    #file = file_upload
    file = ClientFile(file_upload)

    if file_upload is None:
        return

    print("name = ",file_upload.get("name"))
    print("last modified = ",file_upload.get("lastModified"))
    print("size = ",file_upload.get("size"))
    print("type = ",file_upload.get("type"))


    # remove all actors
    renderer.RemoveAllViewProps()

    grid.Reset()


    # ### setup of the internal data structure ###
    root = vtkMultiBlockDataSet()
    branch_interior = vtkMultiBlockDataSet()
    branch_boundary = vtkMultiBlockDataSet()

    root.SetBlock(0, branch_interior)
    root.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), 'Interior')
    root.SetBlock(1, branch_boundary)
    root.GetMetaData(1).Set(vtk.vtkCompositeDataSet.NAME(), 'Boundary')
    del root
    pts = vtk.vtkPoints()
    # ### ### #


    # mesh file format specific
    filecontent = file.content.decode('utf-8')
    f = filecontent.splitlines()

    index = [idx for idx, s in enumerate(f) if 'NDIME' in s][0]
    NDIME = int(f[index].split('=')[1])
    #state.meshDim = NDIME
    # for the mesh info display
    #state.meshText += "Mesh Dimensions: " + str(NDIME) + "D \n"

    index = [idx for idx, s in enumerate(f) if 'NPOIN' in s][0]
    numPoints = int(f[index].split('=')[1])
    #state.meshText += "Number of points: " + str(numPoints) + "\n"

    # get all the points
    for point in range(numPoints):
           x = float()
           y = float()
           z = float()
           line = f[index+point+1].split(" ")
           x = float(line[0])
           y = float(line[1])

           if (NDIME==2):
             # 2D is always x-y plane (z=0)
             z = float(0.0)
           else:
             z = float(line[2])
           pts.InsertNextPoint(x,y,z)

    grid.SetPoints(pts)

    # get the elements
    index = [idx for idx, s in enumerate(f) if 'NELEM' in s][0]
    numCells = int(f[index].split('=')[1])
    state.mesh= ["Number of cells: " + str(numCells) + "\n"]

    for cell in range(numCells):
            data = f[index+cell+1].split(" ")
            CellType = int(data[0])
            # quadrilaterals
            if(CellType==9):
              quaddata = [int(data[1]),int(data[2]),int(data[3]),int(data[4])]
              grid.InsertNextCell(VTK_QUAD,4,quaddata)
            # triangles
            elif(CellType==5):
              tridata = [int(data[1]),int(data[2]),int(data[3])]
              grid.InsertNextCell(VTK_TRIANGLE,3,tridata)
            # hexahedral
            elif(CellType==12):
              hexdata = [int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6]),int(data[7]),int(data[8])]
              grid.InsertNextCell(VTK_HEXAHEDRON,8,hexdata)
            # tetrahedral (4 faces)
            elif(CellType==10):
              tetdata = [int(data[1]),int(data[2]),int(data[3]),int(data[4])]
              grid.InsertNextCell(VTK_TETRA,4,tetdata)
            # wedge
            elif(CellType==13):
              wedgedata = [int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6])]
              grid.InsertNextCell(VTK_WEDGE,6,wedgedata)
            # pyramid
            elif(CellType==14):
              pyramiddata = [int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5])]
              grid.InsertNextCell(VTK_PYRAMID,5,pyramiddata)
            else:
              print("ERROR: cell type not suppported")


    branch_interior.SetBlock(0, grid)
    branch_interior.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), 'Fluid-Zone-1')
    del branch_interior

    # ### read the markers ### #
    boundaryNames = []

    markerNames=[]
    index = [idx for idx, s in enumerate(f) if 'NMARK' in s][0]
    numMarkers = int(f[index].split('=')[1])

    # now loop over the markers
    counter=0
    for iMarker in range(numMarkers):
          # grid for the marker
          markergrid = vtkUnstructuredGrid()
          # copy all the pints into the markergrid (inefficient)
          markergrid.SetPoints(pts)
          # next line: marker tag, marker_elem
          counter += 1
          # this is the name (string) of the boundary
          markertag = f[index+counter].split("=")[1].strip()

          # add name to the boundaryNames list of dicts
          boundaryNames.append(
            {
                "text": markertag,
                "value": iMarker,
            }
          )
          markerNames.append(markertag)
          # next line: marker tag, marker_elem
          counter+=1
          line = f[index+counter].split("=")
          numCells = int(line[1])
          #print("number of cells = ",numCells)

          # loop over all cells
          for cell in range(numCells):
            counter+=1
            data = f[index+counter].split(" ")
            #print("data = ",data)
            CellType = int(data[0])
            # line
            if(CellType==3):
              linedata = [int(data[1]),int(data[2])]
              markergrid.InsertNextCell(VTK_LINE,2,linedata)
            # triangles
            elif(CellType==5):
              tridata = [int(data[1]),int(data[2]),int(data[3])]
              markergrid.InsertNextCell(VTK_TRIANGLE,3,tridata)
            # quadrilaterals
            elif(CellType==9):
              quaddata = [int(data[1]),int(data[2]),int(data[3]),int(data[4])]
              markergrid.InsertNextCell(VTK_QUAD,4,quaddata)
            else:
              print("ERROR: marker cell type not suppported")
          # put boundary in multiblock structure
          branch_boundary.SetBlock(iMarker, markergrid)
          branch_boundary.GetMetaData(iMarker).Set(vtk.vtkCompositeDataSet.NAME(), markertag)


    # end loop over lines

    del markergrid
    del pts

    # boundary meshes as unstructured grids
    ds_b = []
    #for i in range(boundaryBlock.GetNumberOfBlocks()):
    for i in range(branch_boundary.GetNumberOfBlocks()):
        ds_b.append(vtk.vtkUnstructuredGrid.SafeDownCast(branch_boundary.GetBlock(i)))
    del branch_boundary



    # we also clear the arrays, if any
    for array in state.dataset_arrays:
        arrayName = array.get("text")
        print("removing array ",arrayName)
        grid.GetPointData().RemoveArray(arrayName)
    # and we only use the default array
    state.dataset_arrays = []

    # Mesh - add mesh to the renderer
    mesh_mapper.SetInputData(grid)
    mesh_actor.SetMapper(mesh_mapper)
    renderer.AddActor(mesh_actor)
    mesh_actor.SetObjectName("internal")

    # boundary actors
    boundary_id = 101
    i = 0
    print("length of ds_b=",len(ds_b))
    for bcName in boundaryNames:
        print("bc name=",bcName)
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

    # add internal mesh as well.
    mesh_actor_list.append({"id":boundary_id,"name":"internal", "mesh":mesh_actor})
    # internal block is also a 'boundary'
    boundaryNames.append(
                            {
                        "text": "internal",
                        "value": numMarkers,
                    }
    )


    # now construct the actual boundary list for the GUI
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

#state.fields = []

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
            accept=".su2",
            __properties=["accept"],
        )

        # progress inside the toolbar
        vuetify.VProgressLinear(
            indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
        )


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

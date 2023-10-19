# vtk_helper.py
# helper functions for vtk and rendering related actions

import vtk
# vtm reader
#from paraview.vtk.vtkIOXML import vtkXMLMultiBlockDataReader
#from vtkmodules.web.utils import mesh as vtk_mesh
from vtkmodules.vtkCommonDataModel import vtkDataObject
#from vtkmodules.vtkFiltersCore import vtkContourFilter #noqa
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkScalarBarActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget, vtkScalarBarWidget
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)


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

# mesh_mapper
from mesh import *


# default visibility of the actors
state.cube_axes_visibility = True
state.coord_axes_visibility = True
state.color_bar_visibiliy = True

renderer = vtkRenderer()

renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
# offscreen rendering, no additional pop-up window
renderWindow.SetOffScreenRendering(1)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

def MakeAxesActor():
    axes = vtkAxesActor()
    axes.SetObjectName("CoordAxes")
    axes.SetShaftTypeToCylinder()
    # text labels 
    axes.SetXAxisLabelText('X')
    axes.SetYAxisLabelText('Y')
    axes.SetZAxisLabelText('Z')
    axes.SetTotalLength(1.0, 1.0, 1.0)
    axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
    axes.SetConeRadius(1.025 * axes.GetConeRadius())
    axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
    return axes

def MakeOrientationMarkerWidget(axes):
    coordaxes = vtkOrientationMarkerWidget()
    coordaxes.SetOrientationMarker(axes)
    # Position lower left in the viewport.
    coordaxes.SetViewport(0, 0, 0.2, 0.2)
    coordaxes.SetInteractor(renderWindowInteractor)
    coordaxes.SetEnabled(True)
    coordaxes.InteractiveOn()
    return coordaxes

def MakeCubeAxesActor():
    cubeaxes = vtkCubeAxesActor()
    cubeaxes.SetObjectName("CubeAxes")
    # Cube Axes: Boundaries, camera, and styling
    cubeaxes.SetBounds(mesh_actor.GetBounds())
    cubeaxes.SetCamera(renderer.GetActiveCamera())
    cubeaxes.SetXLabelFormat("%6.1f")
    cubeaxes.SetYLabelFormat("%6.1f")
    cubeaxes.SetZLabelFormat("%6.1f")
    #cube_axes.SetFlyModeToOuterEdges()
    #cube_axes.SetUseTextActor3D(1)
    cubeaxes.GetTitleTextProperty(0).SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetTitleTextProperty(1).SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetTitleTextProperty(2).SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetLabelTextProperty(0).SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetLabelTextProperty(1).SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetLabelTextProperty(2).SetColor(0.0, 0.0, 0.0)
    cubeaxes.DrawXGridlinesOn()
    cubeaxes.DrawYGridlinesOn()
    cubeaxes.DrawZGridlinesOn()
    cubeaxes.GetXAxesLinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetYAxesLinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetZAxesLinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetXAxesGridlinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetYAxesGridlinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.GetZAxesGridlinesProperty().SetColor(0.0, 0.0, 0.0)
    cubeaxes.XAxisMinorTickVisibilityOff()
    cubeaxes.YAxisMinorTickVisibilityOff()
    cubeaxes.ZAxisMinorTickVisibilityOff()
    cubeaxes.SetVisibility(False)
    state.cube_axes_visibility = False

    return cubeaxes

def MakeScalarBarActor():
    # Create a scalar bar
    scalarbar = vtkScalarBarActor()
    scalarbar.SetObjectName("ScalarAxes")
    scalarbar.SetLookupTable(mesh_mapper.GetLookupTable())
    #scalar_bar.SetTitle('scalar bar')
    scalarbar.UnconstrainedFontSizeOn()
    scalarbar.SetBarRatio(0.2)
    #scalar_bar.SetNumberOfLabels(5)
    scalarbar.SetMaximumWidthInPixels(60)
    scalarbar.SetMaximumHeightInPixels(300)
    return scalarbar

def MakeScalarBarWidget(scalarbar):
    # create the scalar_bar_widget
    scalarbarwidget = vtkScalarBarWidget()
    scalarbarwidget.SetInteractor(renderWindowInteractor)
    scalarbarwidget.SetScalarBarActor(scalarbar)
    scalarbarwidget.RepositionableOn()
    scalarbarwidget.On()
    return scalarbarwidget
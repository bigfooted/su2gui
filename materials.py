# materials gittree menu

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *

state, ctrl = server.state, server.controller

############################################################################
# Materials models - list options #
############################################################################

# List: materials model: Fluid model selection
LMaterialsFluidComp= [
  {"text": "Standard Air", "value": 0, "json": "STANDARD_AIR"},
  {"text": "Ideal Gas", "value": 1, "json": "IDEAL_GAS"},
]

LMaterialsFluidIncomp= [
  {"text": "Constant Density", "value": 0, "json": "CONSTANT_DENSITY"},
  {"text": "Inc. Ideal Gas", "value": 1, "json": "INC_IDEAL_GAS"},
]

LMaterialsViscosity= [
  {"text": "Constant", "value": 0, "json": "CONSTANT_VISCOSITY"},
  {"text": "Sutherland", "value": 1, "json": "SUTHERLAND"},
  {"text": "Polynomial mu(T) ", "value": 2, "json": "POLYNOMIAL_VISCOSITY"},
]

LMaterialsConductivity= [
  {"text": "Constant value", "value": 0, "json": "CONSTANT_CONDUCTIVITY"},
  {"text": "Constant Prandtl", "value": 1, "json": "CONSTANT_PRANDTL"},
  {"text": "Polynomial k(T)", "value": 2, "json": "POLYNOMIAL_CONDUCTIVITY"},
]


###############################################################
# PIPELINE CARD : Materials
###############################################################
def materials_card():
    with ui_card(title="Materials", ui_name="Materials"):
        print("## Materials Selection ##")

        # 1 row of option lists
        with vuetify.VRow(classes="pt-2"):
          with vuetify.VCol(cols="10"):

            # Then a list selection for turbulence submodels
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("materials_fluid_idx", 0),
                # The items in the list
                items=("Object.values(LMaterialsFluid)",),
                # the name of the list box
                label="Fluid density",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 mt-1",
            )
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("materials_viscosity_idx", 0),
                # The items in the list
                items=("representations_viscosity",LMaterialsViscosity),
                # the name of the list box
                label="Fluid viscosity",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 mt-1",
            )
            # conductivity should be off when incompressible + energy=off
            vuetify.VSelect(
                # What to do when something is selected
                v_model=("materials_conductivity_idx", 0),
                # The items in the list
                items=("representations_conductivity",LMaterialsConductivity),
                # the name of the list box
                label="Fluid conductivity",
                hide_details=True,
                dense=True,
                outlined=True,
                # bottom margin larger
                classes="pt-1 mt-1 mb-3",
            )

###############################################################
# Materials - fluid model options
###############################################################
@state.change("materials_fluid_idx")
def update_material(materials_fluid_idx, **kwargs):
    print("fluid density model selection: ",materials_fluid_idx)

    state.active_sub_ui = "submaterials_fluid"
    # update config option value
    jsonData['FLUID_MODEL']= GetJsonName(materials_fluid_idx,state.LMaterialsFluid)

@state.change("materials_viscosity_idx")
def update_material(materials_viscosity_idx, **kwargs):
    print("fluid viscosity model selection: ",materials_viscosity_idx)
    # update config option value
    jsonData['VISCOSITY_MODEL']= GetJsonName(materials_viscosity_idx,LMaterialsViscosity)

@state.change("materials_conductivity_idx")
def update_material(materials_conductivity_idx, **kwargs):
    print("fluid conductivity model selection: ",materials_conductivity_idx)
    # update config option value
    jsonData['CONDUCTIVITY_MODEL']= GetJsonName(materials_conductivity_idx,LMaterialsConductivity)


###############################################################
# PIPELINE SUBCARD : MATERIALS
###############################################################
# secondary card
def materials_subcard():
    # visible when specific materials properties are selected

    # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
    with ui_subcard(title=" submodels", sub_ui_name="submaterials_fluid"):
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("density", 1.22),
            # the name of the list box
            label="density",
        )

   # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
    with ui_subcard(title=" submodels", sub_ui_name="submaterials_fluid"):
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("viscosity", 0.000018),
            # the name of the list box
            label="viscosity",
        )

   # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
    with ui_subcard(title=" submodels", sub_ui_name="submaterials_fluid"):
        vuetify.VTextField(
            # What to do when something is selected
            v_model=("conductivity", 0.025),
            # the name of the list box
            label="conductivity",
        )

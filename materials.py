# materials gittree menu

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *
from trame.widgets import markdown

state, ctrl = server.state, server.controller

# for dialog cards:
#1. define a boolean to show//hide the dialog
#2. define dialog_card
#3. define an update for the boolean to show/hide the dialog
#4. initialize the dialog by calling it in the singlepagewithdrawerlayout
#5. couple to a button in the main ui dialog

# show the material dialog cards
state.show_materials_dialog_card_fluid = False
state.show_materials_dialog_card_viscosity = False
state.show_materials_dialog_card_heatcapacity = False
state.show_materials_dialog_card_conductivity = False

mdstring = """
$a \cdot x^2
"""
widget1 = markdown.Markdown(classes="pa-0 ma-0",content=("var_name", "**f=** $a \\cdot x^2$"))

widget2 = "blabla"
############################################################################
# Materials models - list options #
############################################################################

# List: materials model: Fluid model selection
LMaterialsFluidComp= [
  {"text": "Standard Air", "value": 0, "json": "STANDARD_AIR"},
  {"text": "Ideal Gas", "value": 1, "json": "IDEAL_GAS"},
]

LMaterialsFluidIncomp= [
  {"text": "Constant value", "value": 0, "json": "CONSTANT_DENSITY"},
  {"text": "Inc. Ideal Gas", "value": 1, "json": "INC_IDEAL_GAS"},
]

LMaterialsViscosity= [
  {"text": "Constant value", "value": 0, "json": "CONSTANT_VISCOSITY"},
  {"text": "Sutherland", "value": 1, "json": "SUTHERLAND"},
  {"text": "Polynomial mu(T) ", "value": 2, "json": "POLYNOMIAL_VISCOSITY"},
]

# heat capacity has only one option
LMaterialsHeatCapacity= [
  {"text": "Constant value", "value": 0},
]

LMaterialsConductivity= [
  {"text": "Constant value", "value": 0, "json": "CONSTANT_CONDUCTIVITY"},
  {"text": "Constant Prandtl", "value": 1, "json": "CONSTANT_PRANDTL"},
  {"text": "Polynomial k(T)", "value": 2, "json": "POLYNOMIAL_CONDUCTIVITY"},
]


######################################################################
def materials_dialog_card_fluid():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_materials_dialog_card_fluid",False)):
      with vuetify.VCard():


        vuetify.VCardTitle("density [kg/m^3]",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")


        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("materials_constant_density_idx", 1.2),
                # the name of the list box
                label="density",
              )

        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_materials_dialog_card_fluid)


def update_materials_dialog_card_fluid():
    state.show_materials_dialog_card_fluid = not state.show_materials_dialog_card_fluid

#####################################################################
def materials_dialog_card_viscosity():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_materials_dialog_card_viscosity",False)):
      with vuetify.VCard():
        # UI Component
        vuetify.VCardTitle("viscosity [N.s/m^2]",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")



        with vuetify.VContainer(fluid=True,v_if=("jsonData['VISCOSITY_MODEL']=='CONSTANT_VISCOSITY' ")):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):

            # TODO: example markdown to be tested further
            #with vuetify.VCol(cols="12", classes="py-1 my-1 pr-0 mr-0"):
            #  vuetify.VTextField(
            #    v_model=("materials_constant_viscosity_idx", 1.18e-5),
            #    label=(markdown.Markdown(classes="pa-0 ma-0",content=("var_name", "**f=** $a \\cdot x^2$")))
            #  )

            #with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
            #  vuetify.VTextField(
            #     label=("jsonData['VISCOSITY_MODEL']","none")
            #     )

            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("materials_constant_viscosity_idx", 1.18e-5),
                # the name of the list box
                label="viscosity",

              )

        with vuetify.VContainer(fluid=True,v_if=("jsonData['VISCOSITY_MODEL']=='SUTHERLAND' "),):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):

              vuetify.VTextField(
                 label=("jsonData['VISCOSITY_MODEL']","none")
                 )

            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                v_model=("materials_sutherland_muref_idx", 1.18e-5),
                 label="Reference viscosity mu_ref [kg/m.s]",
                 )

            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                v_model=("materials_sutherland_muTref_idx", 273.15),
                 label="Reference Temperature mu_T_ref [K]",
                 )

            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                v_model=("materials_sutherland_S_idx", 110.4),
                 label="Sutherland constant [K]",
                 )



        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_materials_dialog_card_viscosity)


def update_materials_dialog_card_viscosity():
    state.show_materials_dialog_card_viscosity = not state.show_materials_dialog_card_viscosity

#####################################################################
def materials_dialog_card_heatcapacity():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_materials_dialog_card_heatcapacity",False)):
      with vuetify.VCard():
        vuetify.VCardTitle("heat capacity [J/Kg.K]",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("materials_constant_cp_idx", 1005.0),
                # the name of the list box
                label="specific heat Cp",
              )

        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_materials_dialog_card_heatcapacity)


def update_materials_dialog_card_heatcapacity():
    state.show_materials_dialog_card_heatcapacity = not state.show_materials_dialog_card_heatcapacity

#####################################################################
def materials_dialog_card_conductivity():
    with vuetify.VDialog(width=300,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_materials_dialog_card_conductivity",False)):

      with vuetify.VCard():
        vuetify.VCardTitle("thermal conductivity [W/m.K]",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VTextField(
                # What to do when something is selected
                v_model=("materials_constant_conductivity_idx", 1005.0),
                # the name of the list box
                label="thermal conductivity",
              )

        with vuetify.VCardText():
          vuetify.VBtn("close", click=update_materials_dialog_card_conductivity)


def update_materials_dialog_card_conductivity():
    state.show_materials_dialog_card_conductivity = not state.show_materials_dialog_card_conductivity





###############################################################
# PIPELINE CARD : Materials
###############################################################
def materials_card():
    with ui_card(title="Materials", ui_name="Materials"):
        print("## Materials Selection ##")

        # 1 row of option lists

        with vuetify.VContainer(fluid=True):
          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
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
                classes="py-0 my-0",
            )
            with vuetify.VCol(cols="4", classes="py-0 my-0"):
              with vuetify.VBtn(classes="mx-0 py-0 mt-2 mb-0",elevation=1,variant="text",color="white", click=update_materials_dialog_card_fluid, icon="mdi-dots-vertical"):
                vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")


          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
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
                classes="py-0 my-0",
              )
            with vuetify.VCol(cols="4", classes="py-0 my-0"):
              with vuetify.VBtn(classes="mx-0 py-0 mt-2 mb-0",elevation=1,variant="text",color="white", click=update_materials_dialog_card_viscosity, icon="mdi-dots-vertical"):
                vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              vuetify.VSelect(
                # What to do when something is selected
                v_model=("materials_heatcapacity_idx", 0),
                # The items in the list
                items=("representations_heatcapacity",LMaterialsHeatCapacity),
                # the name of the list box
                label="Fluid heat capacity",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="py-0 my-0",
              )
            with vuetify.VCol(cols="4", classes="py-0 my-0"):
              with vuetify.VBtn(classes="mx-0 py-0 mt-2 mb-0",elevation=1,variant="text",color="white", click=update_materials_dialog_card_heatcapacity, icon="mdi-dots-vertical"):
                vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")

          # ####################################################### #
          with vuetify.VRow(classes="py-0 my-0"):
            with vuetify.VCol(cols="8", classes="py-1 my-1 pr-0 mr-0"):
              # conductivity should be off when incompressible + energy=off
              vuetify.VSelect(
                # What to do when something is selected
                v_model=("materials_conductivity_idx", 0),
                # The items in the list
                items=("representations_conductivity",LMaterialsConductivity),
                # the name of the list box
                label="Fluid conductivity",
                # note that when jsonData changes, it needs to be updated using state.dirty
                disabled=("jsonData['INC_ENERGY_EQUATION']=='NO'",False),
                hide_details=True,
                dense=True,
                outlined=True,
                # bottom margin larger
                classes="py-0 my-0",
              )
            with vuetify.VCol(cols="4", classes="py-0 my-0"):
              with vuetify.VBtn(classes="mx-0 py-0 mt-2 mb-0",
                                elevation=1,
                                variant="text",
                                color="white",
                                click=update_materials_dialog_card_conductivity,
                                disabled=("jsonData['INC_ENERGY_EQUATION']=='NO'",False),
                                icon="mdi-dots-vertical"):
                vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")

###############################################################
# Materials - fluid model options
###############################################################
@state.change("materials_fluid_idx")
def update_material(materials_fluid_idx, **kwargs):
    print("fluid density model selection: ",materials_fluid_idx)
    print("parent ui = ",state.active_ui)
    # only set it if the parent is Materials
    #if state.active_ui=="Materials":
    #  state.active_sub_ui = "submaterials_density"

    # update config option value
    state.jsonData['FLUID_MODEL']= GetJsonName(materials_fluid_idx,state.LMaterialsFluid)

@state.change("materials_heatcapacity_idx")
def update_material(materials_heatcapacity_idx, **kwargs):
    print("fluid heat capacity model selection: ",materials_heatcapacity_idx)
    # only set it if the parent is Materials
    #if state.active_ui=="Materials":
    #  state.active_sub_ui = "submaterials_heatcapacity"

    # update config option value
    # <> no config option exists for heat capacity yet


@state.change("materials_viscosity_idx")
def update_material(materials_viscosity_idx, **kwargs):
    print("fluid viscosity model selection: ",materials_viscosity_idx)
    # only set it if the parent is Materials
    #if state.active_ui=="Materials":
    #  state.active_sub_ui = "submaterials_viscosity"

    # update config option value
    state.jsonData['VISCOSITY_MODEL']= GetJsonName(materials_viscosity_idx,LMaterialsViscosity)
    print("state.jsonData=",state.jsonData['VISCOSITY_MODEL'])
    state.dirty('jsonData')


@state.change("materials_conductivity_idx")
def update_material(materials_conductivity_idx, **kwargs):
    print("fluid conductivity model selection: ",materials_conductivity_idx)
    # only set it if the parent is Materials
    #if state.active_ui=="Materials":
    #  state.active_sub_ui = "submaterials_conductivity"
    print("energy = ",state.jsonData['INC_ENERGY_EQUATION'])

    # update config option value
    state.jsonData['CONDUCTIVITY_MODEL']= GetJsonName(materials_conductivity_idx,LMaterialsConductivity)


###############################################################
# PIPELINE SUBCARD : MATERIALS
###############################################################
# # secondary card
# def materials_subcard():
#     # visible when specific materials properties are selected

#     # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
#     with ui_subcard(title=" submodels", sub_ui_name="submaterials_density"):
#         vuetify.VTextField(
#             # What to do when something is selected
#             v_model=("materials_constant_density_idx", 1.22),
#             # the name of the list box
#             label="density",
#         )

#     # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
#     with ui_subcard(title=" submodels", sub_ui_name="submaterials_specific_heat"):
#         vuetify.VTextField(
#             # What to do when something is selected
#             v_model=("materials_constant_cp_idx", 1005.0),
#             # the name of the list box
#             label="specific heat Cp",
#         )

#    # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
#     with ui_subcard(title=" submodels", sub_ui_name="submaterials_viscosity"):
#         vuetify.VTextField(
#             # What to do when something is selected
#             v_model=("materials_constant_viscosity_idx", 0.000018),
#             # the name of the list box
#             label="viscosity",
#         )

#    # for the card to be visible, we have to set state.active_sub_ui = submaterials_fluid
#     with ui_subcard(title=" submodels", sub_ui_name="submaterials_conductivity"):
#         vuetify.VTextField(
#             # What to do when something is selected
#             v_model=("materials_constant_conductivity_idx", 0.025),
#             # the name of the list box
#             label="conductivity",
#         )

###############################################################
# Materials - fluid model options
###############################################################
# fluid_model = constant density model
# the density is set to the freestream density
# cp = cv = SPECIFIC_HEAT_CP
@state.change("materials_constant_density_idx")
def update_material(materials_constant_density_idx, **kwargs):
    print("fluid density model selection: ",materials_constant_density_idx)
    print("parent ui = ",state.active_ui)
    # only set it if the parent is Materials
    if state.active_ui=="Materials":
      state.active_sub_ui = "submaterials_fluid"
    # update config option value
    state.jsonData['FREESTREAM_DENSITY']= materials_constant_density_idx

# constant viscosity model
@state.change("materials_constant_viscosity_idx")
def update_material(materials_constant_viscosity_idx, **kwargs):
    print("constant viscosity value: ",materials_constant_viscosity_idx)
    # update config option value
    state.jsonData['MU_CONSTANT']= materials_constant_viscosity_idx

# constant cp
@state.change("materials_constant_cp_idx")
def update_material(materials_constant_cp_idx, **kwargs):
    print("constant cp value: ",materials_constant_cp_idx)
    # update config option value
    state.jsonData['SPECIFIC_HEAT_CP']= materials_constant_cp_idx

# constant conductivity model
@state.change("materials_constant_conductivity_idx")
def update_material(materials_constant_conductivity_idx, **kwargs):
    print("constant conductivity value: ",materials_constant_conductivity_idx)
    # update config option value
    state.jsonData['THERMAL_CONDUCTIVITY_CONSTANT']= materials_constant_conductivity_idx

# Sutherland viscosity model
@state.change("materials_sutherland_muref_idx")
def update_material(materials_sutherland_muref_idx, **kwargs):
    print("Sutherland viscosity mu_ref value: ",materials_sutherland_muref_idx)
    # update config option value
    state.jsonData['MU_REF']= materials_sutherland_muref_idx

# Sutherland viscosity model
@state.change("materials_sutherland_muTref_idx")
def update_material(materials_sutherland_muTref_idx, **kwargs):
    print("Sutherland viscosity mu_T_ref value: ",materials_sutherland_muTref_idx)
    # update config option value
    state.jsonData['MU_T_REF']= materials_sutherland_muTref_idx

# Sutherland viscosity model
@state.change("materials_sutherland_S_idx")
def update_material(materials_sutherland_S_idx, **kwargs):
    print("Sutherland viscosity S value: ",materials_sutherland_S_idx)
    # update config option value
    state.jsonData['SUTHERLAND_CONSTANT']= materials_sutherland_S_idx
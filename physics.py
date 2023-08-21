# physics gittree menu

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *
from materials import *

state, ctrl = server.state, server.controller

############################################################################
# Physics models - list options #
############################################################################

# List: physics model: {compressible, incompressible} selection
LPhysicsComp= [
  {"text": "Incompressible", "value": 0},
  {"text": "Compressible", "value": 1},
]

# List: physics model: Turbulence: {SA, SST} selection
LPhysicsTurbModel= [
  {"text": "Inviscid (Euler)", "value": 0},
  {"text": "Laminar (Navier-Stokes)", "value": 1},
  {"text": "Spalart-Allmaras (RANS)", "value": 2},
  {"text": "k-omega SST (RANS)", "value": 3},
]

# List: physics model: Spalart-Allmaras options: selection
LPhysicsTurbSAOptions= [
        {"text": "Default", "value": 0, "json":"NONE"},
        {"text": "Negative", "value": 1,"json":"NEGATIVE"},
        {"text": "Edwards", "value": 2,"json":"EDWARDS"},
        ]
#LPhysicsTurbSAOptions= [
#        {"text": "Negative", "value": 0},
#        {"text": "Edwards", "value": 1},
#        {"text": "FT2", "value": 2},
#        {"text": "QCR2000", "value": 3},
#        {"text": "Compressibility", "value": 4},
#        {"text": "Rotation", "value": 5},
#        {"text": "BCM", "value": 6},
#        {"text": "Experimental", "value": 7},
#        ]

# List: physics model: SST options
LPhysicsTurbSSTOptions= [
        {"text": "V1994m", "value": 0, "json":"V1994m"},
        {"text": "V2003m", "value": 1, "json":"V2003m"},
        ]

# compressible inlet boundary types
# json name: INLET_TYPE
LBoundaryInletType= [
        {"text": "Total conditions", "value": 0,"json":"TOTAL_CONDITIONS"},
        {"text": "Mass flow", "value": 1,"json":"MASS_FLOW"},
]
# compressible inlet boundary types
# json name: -
LBoundaryOutletType= [
  {"text": "None", "value": 0},
]

# incompressible inlet boundary types
# json name: INC_INLET_TYPE
LBoundaryIncInletType= [
        {"text": "Pressure", "value": 0,"json":"PRESSURE_INLET"},
        {"text": "Velocity", "value": 1,"json":"VELOCITY_INLET"},
]

# incompressible outlet boundary types
# json name: INC_OUTLET_TYPE
LBoundaryIncOutletType= [
        {"text": "Pressure", "value": 0,"json":"PRESSURE_OUTLET"},
        {"text": "Mass flow", "value": 1,"json":"VELOCITY_OUTLET"},
]


###############################################################
# PIPELINE CARD : PHYSICS
###############################################################
def physics_card():
    with ui_card(title="Physics", ui_name="Physics"):
        print("## Physics Selection ##")

        # todo: viscous flow on/off (Euler vs Navier-Stokes)

        # 2 columns, left containing compressible/incompressible
        # right containing energy on/off (for incompressible only)
        with vuetify.VRow(classes="pt-2"):
            with vuetify.VCol(cols="6"):
                # first a list selection for compressible/incompressible
                vuetify.VSelect(
                    # What to do when something is selected
                    v_model=("physics_comp_idx", 0),
                    # The items in the list
                    items=("representations_comp",LPhysicsComp),
                    # the name of the list box
                    label="Solver",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="mt-0 pt-0",
                )
            with vuetify.VCol(cols="6"):
                # checkbox for energy (can only be deselected for incompressible)
                vuetify.VCheckbox(
                    v_model=("physics_energy_idx", True),
                    label="Energy equation",
                    # activate or deactivate/disable the checkbox
                    # only active for incompressible flow
                    # else, default is on
                    disabled=("compressible",0),
                    #on_icon="mdi-cube-outline",
                    #off_icon="mdi-cube-off-outline",
                    #on_icon="mdi-download-box-outline",
                    #off_icon="mdi-download-box-outline",
                    classes="mt-1 pt-1",
                    hide_details=True,
                    dense=True,
                )

        # Then a list selection for turbulence submodels
        vuetify.VSelect(
            # What to do when something is selected
            v_model=("physics_turb_idx", 0),
            # The items in the list
            items=("representations_turb",LPhysicsTurbModel),
            # the name of the list box
            label="Turbulence model",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1 mt-1",
        )


###############################################################


###############################################################
# turbulence - SST - model options
###############################################################
@state.change("physics_turb_sst_idx")
def update_physics_turb_sst(physics_turb_sst_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sst_idx)
    jsonData['SST_OPTIONS']= GetJsonName(physics_turb_sst_idx,LPhysicsTurbSSTOptions)

###############################################################
# turbulence - SST - model options
###############################################################
@state.change("physics_turb_sa_idx")
def update_physics_turb_sa(physics_turb_sa_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_idx)
    #NONE should be false
    state.SAOptions['NONE'] = False
    state.SAOptions['NEGATIVE'] = False
    state.SAOptions['EDWARDS'] = False
    state.SAOptions[GetJsonName(physics_turb_sa_idx,LPhysicsTurbSAOptions)] = True
    print("SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if value==True:
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_ft2_idx")
def update_physics_turb_sa(physics_turb_sa_ft2_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_ft2_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['WITHFT2'] = physics_turb_sa_ft2_idx
    print("SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("key=",key,", val=",value)
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_qcr2000_idx")
def update_physics_turb_sa(physics_turb_sa_qcr2000_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_qcr2000_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['QCR2000'] = physics_turb_sa_qcr2000_idx
    print("SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("key=",key,", val=",value)
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_compressibility_idx")
def update_physics_turb_sa(physics_turb_sa_compressibility_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_compressibility_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['COMPRESSIBILITY'] = physics_turb_sa_compressibility_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("key=",key,", val=",value)
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_rotation_idx")
def update_physics_turb_sa(physics_turb_sa_rotation_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_rotation_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['ROTATION'] = physics_turb_sa_rotation_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("key=",key,", val=",value)
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_bcm_idx")
def update_physics_turb_sa(physics_turb_sa_bcm_idx, **kwargs):
    print("turbulence model selection: ",physics_turb_sa_bcm_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['BCM'] = physics_turb_sa_bcm_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("key=",key,", val=",value)
          optionstring += str(key) + " "
    jsonData['SA_OPTIONS']= optionstring

###############################################################
# physics - energy equation
###############################################################
@state.change("physics_energy_idx")
def update_physics_energy(physics_energy_idx, **kwargs):
    print("energy selection: ",physics_energy_idx)
    # can only be activated/deactivated for incompressible
    energy = bool(physics_energy_idx)
    if (energy==True):
      jsonData['INC_ENERGY_EQUATION']= "YES"
    else:
      jsonData['INC_ENERGY_EQUATION']= "NO"

############################################################################
# UI value update: Physics properties #
############################################################################
@state.change("physics_comp_idx")
def update_physics_comp(physics_comp_idx, **kwargs):
    print("compressible selection: ",physics_comp_idx)
    # compressible selected means we have either NAVIER_STOKES or RANS
    # incompressible selected means we have either INC_RANS or INC_NAVIER_STOKES
    # This option goes together with the turbulence option

    state.compressible = bool(physics_comp_idx)

    turb = True
    if (jsonData['KIND_TURB_SOLVER']=="NONE"): turb=False

    # physics_comp_idx=0 = compressible
    if (physics_comp_idx==0):
        if (turb==False):
            jsonData['SOLVER']="NAVIER_STOKES"
        else:
            jsonData['SOLVER']="RANS"
    else:
        if (turb==False):
            jsonData['SOLVER']="INC_NAVIER_STOKES"
        else:
            jsonData['SOLVER']="INC_RANS"



    # select compressible or incompressible options for:
    # - fluid model (density)
    # - boundary conditions
    if (state.compressible==True):
      state.LMaterialsFluid = LMaterialsFluidComp
      print("selecting compressible boundary type for inlet and outlet")
      state.bcinletsubtype = LBoundaryInletType
      state.bcoutletsubtype = LBoundaryOutletType
    else:
      state.LMaterialsFluid = LMaterialsFluidIncomp
      print("selecting incompressible boundary type for inlet and outlet")
      state.bcinletsubtype = LBoundaryIncInletType
      state.bcoutletsubtype = LBoundaryIncOutletType


###############################################################
# UI value update: turbulence model selection #
###############################################################
@state.change("physics_turb_idx")
def update_physics_turb(physics_turb_idx, **kwargs):
    print("turbulence selection: ",physics_turb_idx)
    # if turbulence is selected, we also need to select a default turbulence model
    # if turbulence is deselected, we put turbulence model to "NONE"

    compressible=False
    if "INC" in (jsonData["SOLVER"]): compressible=False

    # physics_turb_idx=0 = Euler
    if (physics_turb_idx==0):
        if (compressible==True):
            jsonData['SOLVER']="EULER"
            jsonData['KIND_TURB_SOLVER']="NONE"
        else:
            jsonData['SOLVER']="INC_EULER"
            jsonData['KIND_TURB_SOLVER']="NONE"
    # 1 = laminar
    elif (physics_turb_idx==1):
        if (compressible==True):
            jsonData['SOLVER']="NAVIER_STOKES"
            jsonData['KIND_TURB_SOLVER']="NONE"
        else:
            jsonData['SOLVER']="INC_NAVIER_STOKES"
            jsonData['KIND_TURB_SOLVER']="NONE"
    # 2 = turbulent - SA
    elif (physics_turb_idx==2):
        if (compressible==True):
            jsonData['SOLVER']="RANS"
            jsonData['KIND_TURB_SOLVER']="SA"
        else:
            jsonData['SOLVER']="INC_RANS"
            jsonData['KIND_TURB_SOLVER']="SA"
    # 3 = turbulent - SST
    elif (physics_turb_idx==3):
        if (compressible==True):
            jsonData['SOLVER']="RANS"
            jsonData['KIND_TURB_SOLVER']="SST"
        else:
            jsonData['SOLVER']="INC_RANS"
            jsonData['KIND_TURB_SOLVER']="SST"

    if (physics_turb_idx == 2):
        print("SA turbulence model activated")
        noSSTSelected=True
        state.noSST=True
        state.active_sub_ui = "subphysics_sa"
        state.submodeltext = "SA text"
    elif (physics_turb_idx == 3):
        print("SST turbulence model activated")
        noSSTSelected=False
        state.noSST=False
        state.active_sub_ui = "subphysics_sst"
        state.submodeltext = "SST text"
    else:
        print("SST turbulence model deactivated")
        noSSTSelected=True
        state.noSST=True
        state.active_sub_ui = "subphysics_none"
        state.submodeltext = "no model"


###############################################################
# PIPELINE SUBCARD : PHYSICS
###############################################################
# secondary card
def physics_subcard():
    # also visible when physics is selected

    # for the card to be visible, we have to set state.active_sub_ui = "subphysics_sst"
    with ui_subcard(title="SST submodels", sub_ui_name="subphysics_sst"):
        # Then a list selection for SST turbulence submodels
        vuetify.VSelect(
            # What to do when something is selected
            v_model=("physics_turb_sst_idx", 0),
            # The items in the list
            items=("representations_sst",LPhysicsTurbSSTOptions),
            # the name of the list box
            label="SST model",
            # ### disables the entire selection ###
            #disabled=("noSST",0),
            ### ### ### ### ### ### ### ### ### ###
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1 mt-1",
        )

    # for the card to be visible, we have to set state.active_sub_ui = "subphysics_sa"
    with ui_subcard(title="SA submodels", sub_ui_name="subphysics_sa"):
        # Then a list selection for SST turbulence submodels
        vuetify.VSelect(
            # What to do when something is selected
            v_model=("physics_turb_sa_idx", 0),
            # The items in the list
            items=("representations_sa",LPhysicsTurbSAOptions),
            # the name of the list box
            label="SA model",
            # ### disables the entire selection ###
            #disabled=("noSA",0),
            ### ### ### ### ### ### ### ### ### ###
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1 mt-1",
        )
        with vuetify.VCol(cols="6"):
            vuetify.VCheckbox(
                v_model=("physics_turb_sa_ft2_idx", False),
                label="ft2",
                classes="mt-1 pt-1",
                hide_details=True,
                dense=True,
            )
            vuetify.VCheckbox(
                v_model=("physics_turb_sa_qcr2000_idx", False),
                label="qcr2000",
                classes="mt-1 pt-1",
                hide_details=True,
                dense=True,
            )
            vuetify.VCheckbox(
                v_model=("physics_turb_sa_compressibility_idx", False),
                label="compressibility",
                classes="mt-1 pt-1",
                hide_details=True,
                dense=True,
            )
            vuetify.VCheckbox(
                v_model=("physics_turb_sa_rotation_idx", False),
                label="rotation",
                classes="mt-1 pt-1",
                hide_details=True,
                dense=True,
            )
            vuetify.VCheckbox(
                v_model=("physics_turb_sa_bcm_idx", False),
                label="BCM",
                classes="mt-1 pt-1",
                hide_details=True,
                dense=True,
            )

    # for the card to be visible, we have to set state.active_sub_ui = "subphysics_sa"
    with ui_subcard(title="no submodels", sub_ui_name="subphysics_none"):
       vuetify.VTextarea(
                label="no submodels:",
                rows="5",
                v_model=("submodeltext", state.submodeltext),
        )

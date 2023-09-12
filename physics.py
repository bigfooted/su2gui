# physics gittree menu

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *
from materials import *
import copy
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




# set the state variables using the json data
def set_json_physics():
  # energy equation on/off
  state.physics_energy_idx = bool(state.jsonData['INC_ENERGY_EQUATION']=="YES")
  state.dirty('physics_energy_idx')

  # compressible or incompressible
  state.physics_comp_idx = 0 if "INC" in state.jsonData['SOLVER'] else 1
  print("       ################# compressible= ",state.physics_comp_idx)
  state.dirty('physics_comp_idx')

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

  # turbulence model
  state.physics_turb_idx = 0
  state.physics_turb_sst_idx = 0
  state.physics_turb_sa_idx = 0
  state.physics_turb_sa_ft2_idx = 0
  state.physics_turb_sa_qcr2000_idx = 0
  state.physics_turb_sa_compressibility_idx = 0
  state.physics_turb_sa_rotation_idx = 0
  state.physics_turb_sa_bcm_idx = 0

  if "RANS" in state.jsonData['KIND_TURB_SOLVER']:
    if state.jsonData['KIND_TURB_SOLVER'] == "SST":
      state.physics_turb_idx = 3
      state.physics_turb_sst_idx= GetJsonIndex(state.jsonData['SST_OPTIONS'],LPhysicsTurbSSTOptions)
    else:
      # must be SA
      state.physics_turb_idx = 2
      state.physics_turb_sa_idx= GetJsonIndex(state.jsonData['SA_OPTIONS'],LPhysicsTurbSSTOptions)
      # SA submodels
      state.physics_turb_sa_ft2_idx= bool("WITHFT2" in state.jsonData['SA_OPTIONS'])
      state.physics_turb_sa_qcr2000_idx= bool("QCR200" in state.jsonData['SA_OPTIONS'])
      state.physics_turb_sa_compressibility_idx= bool("COMPRESSIBILITY" in state.jsonData['SA_OPTIONS'])
      state.physics_turb_sa_rotation_idx= bool("ROTATION" in state.jsonData['SA_OPTIONS'])
      state.physics_turb_sa_bcm_idx= bool("BCM" in state.jsonData['SA_OPTIONS'])

  state.dirty('physics_turb_idx')
  state.dirty('physics_turb_sa_ft2_idx')
  state.dirty('physics_turb_sa_qcr2000_idx')
  state.dirty('physics_turb_sa_compressibility_idx')
  state.dirty('physics_turb_sa_rotation_idx')
  state.dirty('physics_turb_sa_bcm_idx')
  state.dirty('physics_turb_sst_idx')


###############################################################
# PIPELINE CARD : PHYSICS
###############################################################
def physics_card():
    with ui_card(title="Physics", ui_name="Physics"):
        print("     ## Physics Selection ##")

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
                    disabled=("physics_comp_idx",0),
                    classes="mt-1 pt-1",
                    hide_details=True,
                    dense=True,
                )

        # Then a list selection for turbulence submodels
        vuetify.VSelect(
            # What to do when something is selected
            # the value is the default
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
    print("     turbulence model selection: ",physics_turb_sst_idx)
    state.jsonData['SST_OPTIONS']= GetJsonName(physics_turb_sst_idx,LPhysicsTurbSSTOptions)

###############################################################
# turbulence - SST - model options
###############################################################
@state.change("physics_turb_sa_idx")
def update_physics_turb_sa(physics_turb_sa_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_idx)
    #NONE should be false
    state.SAOptions['NONE'] = False
    state.SAOptions['NEGATIVE'] = False
    state.SAOptions['EDWARDS'] = False
    state.SAOptions[GetJsonName(physics_turb_sa_idx,LPhysicsTurbSAOptions)] = True
    print("     SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if value==True:
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_ft2_idx")
def update_physics_turb_sa(physics_turb_sa_ft2_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_ft2_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['WITHFT2'] = physics_turb_sa_ft2_idx
    print("     SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("           key=",key,", val=",value)
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_qcr2000_idx")
def update_physics_turb_sa(physics_turb_sa_qcr2000_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_qcr2000_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['QCR2000'] = physics_turb_sa_qcr2000_idx
    print("     SA options=",state.SAOptions)
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("           key=",key,", val=",value)
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_compressibility_idx")
def update_physics_turb_sa(physics_turb_sa_compressibility_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_compressibility_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['COMPRESSIBILITY'] = physics_turb_sa_compressibility_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("           key=",key,", val=",value)
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_rotation_idx")
def update_physics_turb_sa(physics_turb_sa_rotation_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_rotation_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['ROTATION'] = physics_turb_sa_rotation_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("           key=",key,", val=",value)
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

@state.change("physics_turb_sa_bcm_idx")
def update_physics_turb_sa(physics_turb_sa_bcm_idx, **kwargs):
    print("     turbulence model selection: ",physics_turb_sa_bcm_idx)
    state.SAOptions['NONE'] = False
    state.SAOptions['BCM'] = physics_turb_sa_bcm_idx
    optionstring=""
    for key in state.SAOptions:
      value=state.SAOptions[key]
      if (value==True):
          print("           key=",key,", val=",value)
          optionstring += str(key) + " "
    state.jsonData['SA_OPTIONS']= optionstring

###############################################################
# physics - energy equation
###############################################################
@state.change("physics_energy_idx")
def update_physics_energy(physics_energy_idx, **kwargs):

    print("     energy selection: ",physics_energy_idx)
    # can only be activated/deactivated for incompressible
    #state.energy = bool(state.physics_energy_idx)


    state.jsonData['INC_ENERGY_EQUATION']= bool(physics_energy_idx)
    #if (state.energy==True):
    #  state.jsonData['INC_ENERGY_EQUATION']= "YES"
    #else:
    #  state.jsonData['INC_ENERGY_EQUATION']= "NO"

    # update jsonData
    state.dirty("jsonData")

############################################################################
# UI value update: Physics properties #
############################################################################
@state.change("physics_comp_idx")
def update_physics_comp(physics_comp_idx, **kwargs):
    print("     compressible selection: ",physics_comp_idx)
    # compressible selected means we have either NAVIER_STOKES or RANS
    # incompressible selected means we have either INC_RANS or INC_NAVIER_STOKES
    # This option goes together with the turbulence option

    compressible = bool(physics_comp_idx)

    turb = True
    if (state.jsonData['KIND_TURB_SOLVER']=="NONE"): turb=False

    # physics_comp_idx=0 = compressible
    if (compressible):
        if (turb==False):
            state.jsonData['SOLVER']="NAVIER_STOKES"
        else:
            state.jsonData['SOLVER']="RANS"
    else:
        if (turb==False):
            state.jsonData['SOLVER']="INC_NAVIER_STOKES"
        else:
            state.jsonData['SOLVER']="INC_RANS"



    # select compressible or incompressible options for:
    # - fluid materials (density)
    # - fluid materials (viscosity)
    # - boundary conditions
    if (compressible==True):
      print("       selecting compressible for material fluids")
      state.LMaterialsFluid = LMaterialsFluidComp
      state.field_state_name = "Density"
      state.LMaterialsViscosity = LMaterialsViscosityComp
      state.LMaterialsConductivity = LMaterialsConductivityComp
      print("       selecting compressible boundary type for inlet and outlet")
      state.bcinletsubtype = LBoundaryInletType
      state.bcoutletsubtype = LBoundaryOutletType
    else:
      print("       selecting incompressible for material fluids")
      state.LMaterialsFluid = LMaterialsFluidIncomp
      state.field_state_name = "Pressure"
      state.LMaterialsViscosity = LMaterialsViscosityIncomp
      state.LMaterialsConductivity = LMaterialsConductivityIncomp
      print("       selecting incompressible boundary type for inlet and outlet")
      state.bcinletsubtype = LBoundaryIncInletType
      state.bcoutletsubtype = LBoundaryIncOutletType


###############################################################
# UI value update: turbulence model selection #
###############################################################
@state.change("physics_turb_idx")
def update_physics_turb(physics_turb_idx, **kwargs):
    print("     turbulence selection: ",physics_turb_idx)
    # if turbulence is selected, we also need to select a default turbulence model
    # if turbulence is deselected, we put turbulence model to "NONE"

    compressible=True
    if "INC" in (state.jsonData["SOLVER"]): compressible=False

    # physics_turb_idx=0 = Euler
    if (physics_turb_idx==0):
        if (compressible==True):
            state.jsonData['SOLVER']="EULER"
            state.jsonData['KIND_TURB_SOLVER']="NONE"
        else:
            state.jsonData['SOLVER']="INC_EULER"
            state.jsonData['KIND_TURB_SOLVER']="NONE"
    # 1 = laminar
    elif (physics_turb_idx==1):
        if (compressible==True):
            state.jsonData['SOLVER']="NAVIER_STOKES"
            state.jsonData['KIND_TURB_SOLVER']="NONE"
        else:
            state.jsonData['SOLVER']="INC_NAVIER_STOKES"
            state.jsonData['KIND_TURB_SOLVER']="NONE"
    # 2 = turbulent - SA
    elif (physics_turb_idx==2):
        if (compressible==True):
            state.jsonData['SOLVER']="RANS"
            state.jsonData['KIND_TURB_SOLVER']="SA"
        else:
            state.jsonData['SOLVER']="INC_RANS"
            state.jsonData['KIND_TURB_SOLVER']="SA"
    # 3 = turbulent - SST
    elif (physics_turb_idx==3):
        if (compressible==True):
            state.jsonData['SOLVER']="RANS"
            state.jsonData['KIND_TURB_SOLVER']="SST"
        else:
            state.jsonData['SOLVER']="INC_RANS"
            state.jsonData['KIND_TURB_SOLVER']="SST"

    if (physics_turb_idx == 2):
        print("     SA turbulence model activated")
        #noSSTSelected=True
        #state.noSST=True
        if state.active_ui=="Physics":
          state.active_sub_ui = "subphysics_sa"
        state.submodeltext = "SA text"
    elif (physics_turb_idx == 3):
        print("     SST turbulence model activated")
        #noSSTSelected=False
        #state.noSST=False
        if state.active_ui=="Physics":
          state.active_sub_ui = "subphysics_sst"
        state.submodeltext = "SST text"
    else:
        print("     SST turbulence model deactivated")
        #noSSTSelected=True
        #state.noSST=True
        if state.active_ui=="Physics":
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

    # for the card to be visible, we have to set state.active_sub_ui = "subphysics_none"
    with ui_subcard(title="no submodels", sub_ui_name="subphysics_none"):
       vuetify.VTextarea(
                label="no submodels:",
                rows="5",
                v_model=("submodeltext", state.submodeltext),
        )

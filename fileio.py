# fileio gittree menu

# note that in the main menu, we need to call add the following:
# 1) from fileio import *
# 2) call fileio_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline), note that name in gittree node should be
#    the same as name in ui_card() in fileio_card definition
# 4) define any global state variables that might be needed

# 5) to initialize all fields from the config file, createfunction set_json_fileio()
#    and set all state variables using the json file
# 6) call set_json_fileio() from the main su2gui

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *

state, ctrl = server.state, server.controller

# [SOLUTION_FILENAME - text string]
# RESTART_FILENAME - text string
# VOLUME_FILENAME - text string
# [READ_BINARY_RESTART -boolean]
# OUTPUT_WRT_FREQ - integer
# VOLUME_OUTPUT - list of strings
# OUTPUT_FILES - list of strings
# HISTORY_OUTPUT - text string
# HISTORY_WRT_FREQ_INNER integer
# CONV_FILENAME - text string
#
# CONV_FIELD - string
# CONV_RESIDUAL_MINVAL - negative integer
# CONV_STARTITER - integer

# set the state variables using the json data from the config file
def set_json_fileio():
  state.fileio_restart_name = state.jsonData['RESTART_FILENAME']
  state.fileio_restart_frequency = state.jsonData['OUTPUT_WRT_FREQ'][0]
  state.fileio_restart_binary_idx = bool( not "RESTART_ASCII" in  state.jsonData['OUTPUT_FILES'])
  state.fileio_restart_overwrite_idx = bool(state.jsonData['WRT_RESTART_OVERWRITE'])

  state.fileio_volume_name = state.jsonData['VOLUME_FILENAME']
  state.fileio_volume_frequency = state.jsonData['OUTPUT_WRT_FREQ'][1]
  state.fileio_volume_overwrite_idx = bool(state.jsonData['WRT_VOLUME_OVERWRITE'])

  state.fileio_history_name = state.jsonData['CONV_FILENAME']
  state.fileio_history_frequency = state.jsonData['HISTORY_WRT_FREQ_INNER']

  state.dirty('fileio_restart_name')
  state.dirty('fileio_restart_frequency')
  state.dirty('fileio_restart_binary_idx')
  state.dirty('fileio_restart_overwrite_idx')
  state.dirty('fileio_volume_name')
  state.dirty('fileio_volume_frequency')
  state.dirty('fileio_volume_overwrite_idx')
  state.dirty('fileio_history_name')
  state.dirty('fileio_history_frequency')

# for the main card, we need to define variables in the UI elements and then create
# a state.change for them
#
###############################################################
# PIPELINE CARD : PHYSICS
###############################################################
def fileio_card():
    with ui_card(title="File I/O", ui_name="File I/O"):
        print("     ## File I/O Selection ##")

        with vuetify.VContainer(fluid=True, classes="pa-1 ma-1"):
          # ####################################################### #
          with vuetify.VRow():
            with vuetify.VCol(cols="4", classes="py-1 pl-0 pr-1"):
               vuetify.VSheet("filename",classes="grey pl-1",rounded=True)
            with vuetify.VCol(cols="3", classes="py-1 px-0"):
               vuetify.VSheet("frequency",classes="grey pl-1",rounded=True)
            with vuetify.VCol(cols="2", classes="py-1 pl-3 pr-1"):
               vuetify.VSheet("binary", classes="grey pl-1",rounded=True)
            with vuetify.VCol(cols="2", classes="py-1 pl-0 pr-0"):
               vuetify.VSheet("overwrite",classes="grey pl-1",rounded=True)

          with vuetify.VRow():
            with vuetify.VCol(cols="4", classes="py-1 pl-0 pr-1"):
              vuetify.VTextField(
                label="Restart",
                v_model=("fileio_restart_name", "restart_flow"),
                outlined=True,
                dense=True,
                hide_details=True,
              )
            with vuetify.VCol(cols="3",classes="py-1 px-0"):
              vuetify.VTextField(
                v_model=("fileio_restart_frequency", 200),
                label="Frequency",
                outlined=True,
                dense=True,
                hide_details=True,
              )
            with vuetify.VCol(cols="2",classes="py-1 pl-4 pr-0"):
              vuetify.VCheckbox(
                v_model=("fileio_restart_binary_idx", False),
                #label="binary",
                outlined=True,
                hide_details=True,
                dense=True,
            )
            with vuetify.VCol(cols="2",classes="py-1 pl-4 pr-0"):
              vuetify.VCheckbox(
                v_model=("fileio_restart_overwrite_idx", False),
                #label="overwrite",
                outlined=True,
                hide_details=True,
                dense=True,
            )


          with vuetify.VRow():
            with vuetify.VCol(cols="4",classes="py-1 pl-0 pr-1"):
              vuetify.VTextField(
                v_model=("fileio_volume_name", "flow"),
                label="Volume output",
                outlined=True,
                dense=True,
                hide_details=True,
              )
            with vuetify.VCol(cols="3",classes="py-1 px-0"):
              vuetify.VTextField(
                v_model=("fileio_volume_frequency", 100),
                label="Frequency",
                outlined=True,
                dense=True,
                hide_details=True,
              )
            #with vuetify.VCol(cols="2",classes="py-1 pl-4 pr-0"):
            #  vuetify.VCheckbox(
            #    v_model=("fileio_volume_binary_idx", False),
            #    #label="binary",
            #    outlined=True,
            #    hide_details=True,
            #    dense=True,
            #)
            with vuetify.VCol(cols="2",offset="2",classes="py-1 pl-4 pr-0"):
              vuetify.VCheckbox(
                v_model=("fileio_volume_overwrite_idx", False),
                #label="overwrite",
                outlined=True,
                hide_details=True,
                dense=True,
            )

          with vuetify.VRow():
            with vuetify.VCol(cols="4",classes="py-1 pl-0 pr-1"):
              vuetify.VTextField(
                v_model=("fileio_history_name", "history"),
                label="History",
                outlined=True,
                dense=True,
                hide_details=True,
              )
            with vuetify.VCol(cols="3",classes="py-1 px-0"):
              vuetify.VTextField(
                v_model=("fileio_history_frequency", 1),
                label="Frequency",
                outlined=True,
                dense=True,
                hide_details=True,
              )
#
@state.change("fileio_restart_name")
def update_material(fileio_restart_name, **kwargs):
    state.jsonData['RESTART_FILENAME']= fileio_restart_name
    state.dirty('jsonData')

# note that we currently support exactly 2 entries in OUTPUT_FILES, restart and paraview
@state.change("fileio_restart_frequency")
def update_material(fileio_restart_frequency, **kwargs):
    state.jsonData['OUTPUT_WRT_FREQ'][0]= fileio_restart_frequency
    state.dirty('jsonData')

# if binary, change the file type
@state.change("fileio_restart_binary")
def update_material(fileio_restart_binary, **kwargs):
    if bool(fileio_restart_binary)==True:
      state.jsonData['OUTPUT_FILES'][0]= "RESTART"
    else:
      state.jsonData['OUTPUT_FILES'][0]= "RESTART_ASCII"
    state.dirty('jsonData')

@state.change("fileio_restart_overwrite")
def update_material(fileio_restart_overwrite, **kwargs):
    state.jsonData['WRT_RESTART_OVERWRITE']= bool(fileio_restart_overwrite)
    state.dirty('jsonData')

#
@state.change("fileio_volume_name")
def update_material(fileio_volume_name, **kwargs):
    state.jsonData['VOLUME_FILENAME']= fileio_volume_name
    state.dirty('jsonData')

@state.change("fileio_volume_frequency")
def update_material(fileio_volume_frequency, **kwargs):
    state.jsonData['OUTPUT_WRT_FREQ'][1]= fileio_volume_frequency
    state.dirty('jsonData')

@state.change("fileio_volume_overwrite")
def update_material(fileio_volume_overwrite, **kwargs):
    state.jsonData['WRT_VOLUME_OVERWRITE']= bool(fileio_volume_overwrite)
    state.dirty('jsonData')
# if binary, change the file type
#@state.change("fileio_volume_binary")
#def update_material(fileio_restart_binary, **kwargs):
#    if bool(fileio_restart_binary)==True:
#      state.jsonData['OUTPUT_FILES'][0]= "RESTART"
#    else:
#      state.jsonData['OUTPUT_FILES'][0]= "RESTART_ASCII"
#    state.dirty('jsonData')


#
@state.change("fileio_history_name")
def update_material(fileio_history_name, **kwargs):
    state.jsonData['CONV_FILENAME']= fileio_history_name
    state.dirty('jsonData')

@state.change("fileio_history_frequency")
def update_material(fileio_history_frequency, **kwargs):
    state.jsonData['HISTORY_WRT_FREQ_INNER']= fileio_history_frequency
    state.dirty('jsonData')


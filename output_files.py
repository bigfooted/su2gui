from logger import log
from uicard import server
import zipfile, os
from io import BytesIO
from trame.widgets import vuetify
from trame.assets.remote import HttpFile

from pathlib import Path
BASE = Path(__file__).parent 

state, ctrl = server.state, server.controller

# show the material dialog cards
state.show_download_dialog_card = False

state.output_list = {
    'flow.vtm' : [True,'flow.vtm' ],
    "history.csv" : [True,"history.csv"],
    "restart.csv" : [True,"restart.csv"],
    "config_new.cfg" : [True,"config_new.cfg" ],
    'mesh.su2' : [True, 'mesh.su2'],
    'su2gui.log' : [True, 'su2gui.log'],
}

# Dialog card for selecting the output
def download_diagol_card():
    with vuetify.VDialog(position='{X:10,Y:10}',
                         width = 350,
                         transition="dialog-top-transition",
                         v_model=("show_download_dialog_card",False),
                         ):
        with vuetify.VCard():
            vuetify.VCardTitle("Select output files",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")
            
            
            with vuetify.VContainer(fluid=True, style = "padding-left: 20px;"):
            # ####################################################### #
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label=".VTM Filename",
                            v_model = ("vtm_filename", state.output_list["flow.vtm"][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_vtm_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="History Filename",
                            v_model = ("history_filename", state.output_list["history.csv"][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_history_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Config Filename",
                            v_model = ("config_filename", state.output_list["config_new.cfg"][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_cfg_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Restart Filename",
                            v_model = ("restart_filename", state.output_list["restart.csv"][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_restart_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="SU2 Mesh Filename",
                            v_model = ("su2_mesh_filename", state.output_list["mesh.su2"][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_su2_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                        
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Log Filename",
                            v_model = ("log_filename", state.output_list['su2gui.log'][1]),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_log_file", True),
                            
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                        
                with vuetify.VCol():
                    # Add a button to trigger the done action
                    with vuetify.VBtn("Download", 
                                 click=f"utils.download('output.zip', trigger('download_output_files'))"
                    ):
                        vuetify.VIcon("mdi-download-box-outline")

@ctrl.trigger("download_output_files")
def download_outputs():
    files_directory = BASE / "user" 

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_ref:
        for filename, list in state.output_list.items():
            if list[0]:
                file_path = os.path.join(files_directory, filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as f:
                        zip_ref.writestr(zinfo_or_arcname=list[1], data=f.read())
                else:
                    log("Warn", f"{file_path} does not exist and will not be included in the zip file.")
    
    zip_buffer.seek(0)  # Reset buffer position to the beginning
    update_download_dialog_card()
    log("info", f"Zip file downloaded successfully.")
    return zip_buffer.getvalue()


def update_download_dialog_card():
    state.show_download_dialog_card = not state.show_download_dialog_card
    
    
@state.change("output_vtm_file")
def update_output_vtm(output_vtm_file, **kwargs):
    state.output_list['flow.vtm'][0] = bool(output_vtm_file)
    

@state.change("output_history_file")
def update_output_history(output_history_file, **kwargs):
    state.output_list["history.csv"][0] = bool(output_history_file)
    

@state.change("output_cfg_file")
def update_output_cfg(output_cfg_file, **kwargs):
    state.output_list["config_new.cfg" ][0] = bool(output_cfg_file)
    

@state.change("output_restart_file")
def update_output_retstart(output_restart_file, **kwargs):
    state.output_list["restart.csv" ][0] = bool(output_restart_file)
    
@state.change("output_su2_file")
def update_output_su2(output_su2_file, **kwargs):
    state.output_list['mesh.su2'][0] = bool(output_su2_file)

@state.change("output_log_file")
def update_output_retstart(output_log_file, **kwargs):
    state.output_list['su2gui.log' ][0] = bool(output_log_file)
    

# Update Filename
@state.change("vtm_filename")
def update_output_vtm(vtm_filename, **kwargs):
    state.output_list['flow.vtm'][1] = str(vtm_filename)
    

@state.change("history_filename")
def update_output_history(history_filename, **kwargs):
    state.output_list["history.csv"][1] = str(history_filename)
    

@state.change("config_filename")
def update_output_cfg(config_filename, **kwargs):
    state.output_list["config_new.cfg" ][1] = str(config_filename)
    

@state.change("restart_filename")
def update_output_retstart(restart_filename, **kwargs):
    state.output_list["restart.csv" ][1] = str(restart_filename)
    

@state.change("su2_mesh_filename")
def update_output_su2(su2_mesh_filename, **kwargs):
    state.output_list['mesh.su2'][1] = str(su2_mesh_filename)

@state.change("log_filename")
def update_output_su2(log_filename, **kwargs):
    state.output_list['su2gui.log'][1] = str(log_filename)
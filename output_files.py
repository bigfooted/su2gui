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

output_list = {
    'flow.vtm' : False,
    "history.csv" : False,
    "restart.csv" : False,
    "config_new.cfg" : False,
    'mesh.su2' : False
}

# Dialog card for selecting the output
def download_diagol_card():
    with vuetify.VDialog(width=350,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_download_dialog_card",False)):
        with vuetify.VCard():
            vuetify.VCardTitle("Select Output Files",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")
            
            
            with vuetify.VContainer(fluid=True, classes="pa-1 ma-1"):
            # ####################################################### #
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label=".VTM File",
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_vtm_file", False),
                            #label="overwrite",
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="History File",
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_history_file", False),
                            #label="overwrite",
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Config File",
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_cfg_file", False),
                            #label="overwrite",
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Restart File",
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_restart_file", False),
                            #label="overwrite",
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="SU2 Mesh File",
                            outlined=True,
                            dense=True,
                            hide_details=True,
                        )
                    with vuetify.VCol():
                        vuetify.VCheckbox(
                            v_model=("output_su2_file", False),
                            #label="overwrite",
                            outlined=True,
                            hide_details=True,
                            dense=True,
                        )
                        
                with vuetify.VCol():
                    # Add a button to trigger the done action
                    vuetify.VBtn("Download", 
                                 click=f"utils.download('output.zip', trigger('download_output_files'))"
                    )

@ctrl.trigger("download_output_files")
def download_outputs():
    files_directory = BASE / "user" 

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_ref:
        for filename, include in output_list.items():
            if include:
                file_path = os.path.join(files_directory, filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as f:
                        zip_ref.writestr(filename, f.read())
                else:
                    print(f"Warning: {file_path} does not exist and will not be included in the zip file.")
    
    zip_buffer.seek(0)  # Reset buffer position to the beginning
    update_download_dialog_card()
    print(f"Zip file downloaded successfully.")
    return zip_buffer.getvalue()


def update_download_dialog_card():
    state.show_download_dialog_card = not state.show_download_dialog_card
    
    
@state.change("output_vtm_file")
def update_output_vtm(output_vtm_file, **kwargs):
    output_list['flow.vtm'] = bool(output_vtm_file)
    

@state.change("output_history_file")
def update_output_history(output_history_file, **kwargs):
    output_list["history.csv"] = bool(output_history_file)
    

@state.change("output_cfg_file")
def update_output_cfg(output_cfg_file, **kwargs):
    output_list["config_new.cfg" ] = bool(output_cfg_file)
    

@state.change("output_restart_file")
def update_output_retstart(output_restart_file, **kwargs):
    output_list["restart.csv" ] = bool(output_restart_file)
    

@state.change("output_su2_file")
def update_output_su2(output_su2_file, **kwargs):
    output_list['mesh.su2'] = bool(output_su2_file)
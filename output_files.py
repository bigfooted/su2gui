from uicard import server
import zipfile, os
from io import BytesIO
from trame.widgets import vuetify
from trame.assets.remote import HttpFile

from pathlib import Path
BASE = Path(__file__).parent 

state, ctrl = server.state, server.controller


# JavaScript to handle file download
# controller.js_call(
#     "utils.download",
#     trigger_name="download_file",
#     args=(
#         js.state.filename_cfg_export,  # File name to use for download
#         js.state.filename_cfg_export,  # File name for download
#         "text/plain"  # MIME type
#     ),
# )

# show the material dialog cards
state.show_download_dialog_card = False


# su2_filename = state.jsonData['MESH_FILENAME']

#  data for the card table
# output_list = {
#     state.fileio_volume_name : False,
#     state.history_name : False,
#     state.restart_name : False,
#     state.filename_cfg_export : False,
#     su2_filename : False
# }

output_list = {
    'flow.vtm' : False,
    "history.csv" : False,
    "restart.csv" : False,
    "config_new.cfg" : False,
    'mesh.su2' : False
}

# a function to get the checked states
# @state.change("table_data")
# def get_checked_states(table_data, **kwargs):
#     checked_dict = {row["text"]: row["checked"] for row in table_data}
#     print("Checked States:", checked_dict)
    # state.checked_dict = checked_dict  # Store the result in the application state
    

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

        # with vuetify.VContainer():
        # # Define the table with text and checkbox columns
        #     with vuetify.VRow():
        #         with vuetify.VCol():
        #             # Define the table with text and checkbox columns
        #             vuetify.VDataTable(
        #                 v_model=("table_data", rows),
        #                 headers=[
        #                     {"text": "Text", "value": "text"},
        #                     {"text": "Checkbox", "value": "checkbox"},
        #                 ],
        #                 items=("table_data",),
        #                 item_key="text",
        #                 scoped_slots={
        #                     "item.checkbox": lambda ctx: vuetify.VCheckbox(v_model=(f"table_data[{ctx['index']}].checked", ctx["item"]["checked"]))
        #                 },
        #             )
                with vuetify.VCol():
                    # Add a button to trigger the done action
                    vuetify.VBtn("Done", 
                                 click=f"utils.download('output.zip', trigger('download_output_files'))"
                    )



def update_download_dialog_card():
    state.show_download_dialog_card = not state.show_download_dialog_card
    
    
    
@state.change("output_vtm_file")
def update_output_vtm(output_vtm_file, **kwargs):
    output_list['flow.vtm'] = bool(output_vtm_file)
    # download_outputs(output_list, BASE)
    
@state.change("output_history_file")
def update_output_history(output_history_file, **kwargs):
    output_list["history.csv"] = bool(output_history_file)
    # download_outputs(output_list, BASE)


@state.change("output_cfg_file")
def update_output_cfg(output_cfg_file, **kwargs):
    output_list["config_new.cfg" ] = bool(output_cfg_file)
    # download_outputs(output_list, BASE)


@state.change("output_restart_file")
def update_output_retstart(output_restart_file, **kwargs):
    output_list["restart.csv" ] = bool(output_restart_file)
    # download_outputs(output_list, BASE)


@state.change("output_su2_file")
def update_output_su2(output_su2_file, **kwargs):
    output_list['mesh.su2'] = bool(output_su2_file)
    # download_outputs(output_list, BASE)


@ctrl.trigger("download_output_files")
def download_outputs():
    files_directory = BASE / "user" 
    zip_path = os.path.join(files_directory, "output.zip")
    if os.path.isfile(zip_path):
        os.remove(zip_path)
        print("deleted zip file")
            
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename, include in output_list.items():
            if include:
                file_path = os.path.join(files_directory, filename)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=filename)
                else:
                    print(f"Warning: {file_path} does not exist and will not be included in the zip file.")
        update_download_dialog_card()
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_ref:
        with zipfile.ZipFile(zip_path, 'r') as source_zip:
            for file_name in source_zip.namelist():
                with source_zip.open(file_name) as file:
                    zip_ref.writestr(file_name, file.read())
    
    zip_buffer.seek(0)  # Reset buffer position to the beginning
    print(f"Zip file {zip_path} created and downloaded successfully.")
    return zip_buffer.getvalue()

    
# server.js_call(
#     method="utils.download",
#     ref="download_output_files_trigger",
#     args=[
#         f"{BASE}/user/output.zip",  # Path to the zip file to be downloaded
#         "output.zip",  # File name for download
#         "application/zip"  # MIME type for zip files
#     ],
# )
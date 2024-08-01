from datetime import datetime
from uicard import server
import logging
from trame.widgets import vuetify, markdown

# Extract state and controller from the server
state, ctrl = server.state, server.controller

state.show_error_dialog_card = False
state.show_warn_dialog_card = False

state.md_content = ""
state.su2_logs = ""
state.error_msg = ""
state.warn_msg = ""

state.last_modified_su2_log_len = 0
state.last_modified_su2gui_log_len = 0



#################### LOGGING HANDLER ####################
# Configure the root logger to suppress logs from other modules
logging.basicConfig(
    filename="./user/su2gui.log",
    level=logging.WARNING,  # Suppress logs at levels lower than WARNING
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get the logger for the current module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Allow DEBUG logs for this module

# Ensure the logger uses the same formatter as the root logger
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
for handler in logger.handlers:
    handler.setFormatter(formatter)


class CustomHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        if record.levelno == logging.ERROR:
            handle_error(log_entry)
        if record.levelno == logging.WARN:
            handle_warn(log_entry)
        add_new_logs(log_entry)


# Add the custom handler to the root logger
custom_handler = CustomHandler()
custom_handler.setFormatter(formatter)
logging.getLogger().addHandler(custom_handler)


#################### LOGS -> SU2GUI TAB ####################
def log(type :str, message, **kwargs):
    """
    Appends a message to the "su2gui.log" file.

    Args:
        type (str) : Type of message to be appended, like INFO, ERROR, WARN, etc - Any
        message (str): The message to append to the log.
        detail (str) : Details of message, Not necessary 

    """

    message = str(message)
    message += "  \n" 
    if "detail" in kwargs:
        message+=kwargs.get("detail") + "  \n" 

    if type.upper() == "INFO":
       logger.info(message)
    elif type.upper() == "WARN":
       logger.warning(message)
    elif type.upper() == "ERROR":
       logger.error(message)
       find_error_message(message)
    elif type.upper() == "DEBUG":
       logger.debug(message)


# Add new logs to the markdown content in LOGS -> SU2GUI Tab
def add_new_logs(msg):
    state.md_content = (msg + state.md_content[:25000])


# Clear previous logs in the LOGS -> SU2GUI Tab and start fresh
def clear_logs():
    with open('user/su2gui.log', 'w') as f:
        f.write('')
    state.last_modified_su2gui_log_len = 0
    state.su2_logs = ""
    state.show_error_dialog_card = False


# Handle the error message for LOGS -> SU2GUI Tab
def handle_error(error_message):
    if state.show_error_dialog_card == False:
        state.error_msg = error_message
        state.show_error_dialog_card = True
    else:
        state.error_msg+=(error_message)

    # Also Printing the error message in terminal
    print(f"{error_message}")


# Handle the warning message for LOGS -> SU2GUI Tab
def handle_warn(warn_message):
    if state.show_warn_dialog_card == False:
        state.warn_msg = warn_message
        state.show_warn_dialog_card = True
    else:
        state.warn_msg+=(warn_message)

    # Also printing the warning message in terminal
    print(f"{warn_message}")



#################### LOGS -> SU2 TAB ####################
# Update the SU2 logs in the LOGS -> SU2 Tab
# called by asyn function start_countdown in solver.py
def update_su2_logs():
    file = 'user/su2.out'
    with open(file, 'r') as f:
        # Move the file pointer to the last read position
        f.seek(state.last_modified_su2_log_len)
        # Read the new content
        new_logs = f.read()
        # Update the last modified log length
        state.last_modified_su2_log_len += len(new_logs)
        # Update the state logs with the new content
        state.su2_logs = "```" + (state.su2_logs[3:-3] + new_logs)[-25000:] + "```"
        # Check for error messages in the new logs
        find_error_message(new_logs)


# find the error message in the su2 log file
# and display it in the error dialog card
def find_error_message(msg):
    error_found = False
    error_lines = []
    
    for line in msg.splitlines():
        if len(error_lines)>10:
            break
        if error_found:
            error_lines.append(line.strip())
        elif "error" in line.lower().split(' '):
            error_lines.append(line.strip())
            error_found = True
    
    if error_lines:
        error_message = "\n".join(error_lines)
        if state.show_error_dialog_card == False:
            state.error_msg = error_message
            state.show_error_dialog_card = True
        else:
            state.error_msg+=(error_message)

    return error_found



#################### DIALOG CARDS ####################
# popup window for Error messages
def Error_dialog_card():
    with vuetify.VDialog(width=800,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_error_dialog_card",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("ERROR",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        with vuetify.VContainer(fluid=True):
            markdown.Markdown(
                content = ('error_msg', state.error_msg), 
                style = "padding: 3rem; color: Red; background-color: white"
            )
            vuetify.VBtn("Close",click=(hide_error_dialog_card)
                        )

def hide_error_dialog_card():
    state.show_error_dialog_card = False
    state.error_msg = ""

# popup window for Warning messages
def Warn_dialog_card():
    with vuetify.VDialog(width=800,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_warn_dialog_card",False)):
      with vuetify.VCard():

        vuetify.VCardTitle("WARNING",
                           classes="grey lighten-1 py-1 grey--text text--darken-3")

        with vuetify.VContainer(fluid=True):
            markdown.Markdown(
                content = ('warn_msg', state.warn_msg), 
                style = "padding: 3rem; color: #ffcc00; background-color: white"
            )
            vuetify.VBtn("Close",click=(hide_warn_dialog_card)
                        )

def hide_warn_dialog_card():
    state.show_warn_dialog_card = False
    state.warn_msg = ""



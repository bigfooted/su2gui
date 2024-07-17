from datetime import datetime
from uicard import server
import logging

# Extract state and controller from the server
state, ctrl = server.state, server.controller

state.md_content = ""
state.su2_logs = ""

state.last_modified_su2_log_len = 0
state.last_modified_su2gui_log_len = 0

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


def log(type :str, message, **kwargs):
    """
    Appends a message to the "su2gui.log" file.

    Args:
        type (str) : Type of message to be appended, like INFO, ERROR, WARN, etc - Any
        message (str): The message to append to the log.
        detail (str) : Details of message, Not necessary 

    """

    # IMP : Give two white spaces before \n for new line
    #       "\n" will not work, "  \n" will work

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
    elif type.upper() == "DEBUG":
       logger.debug(message)
    
    # Capture the new log messages and update state.md_content
    file = 'user/su2gui.log'
    with open(file, 'r') as f:
        # Move the file pointer to the last read position
        f.seek(state.last_modified_su2gui_log_len)
        # Read the new content
        new_logs = f.read()
        # print(new_logs)
        # Update the last modified log length
        state.last_modified_su2gui_log_len += len(new_logs)
        # Update the state logs with the new content
        state.md_content = (new_logs + state.md_content[:25000])

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
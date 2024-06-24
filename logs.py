from datetime import datetime
from uicard import server
import logging

# Extract state and controller from the server
state, ctrl = server.state, server.controller

# Custom logging handler to capture the last log message
class MessageCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.last_message = ""

    def emit(self, record):
        log_entry = self.format(record)
        self.last_message = log_entry

# Create a custom handler instance
handler = MessageCaptureHandler()

# Configure the root logger to suppress logs from other modules
logging.basicConfig(
    filename="./user/su2gui.log",
    level=logging.WARNING,  # Suppress logs at levels lower than WARNING
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Ensure the custom handler uses the same formatter as the root logger
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Get the logger for the current module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Allow DEBUG logs for this module
logger.addHandler(handler)


def add_spaces_before_newlines(text):
  """
  Adds two spaces before each newline character in a string.
  This helps for adding new line as "\n" without two backspaces doesn't work

  Args:
      text: The input string.

  Returns:
      The modified string with two spaces before each newline.
  """
  text = text.replace('\n', '  \n')


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

    # add_spaces_before_newlines(message)
    message = str(message)
    message += "  \n" 
    if "detail" in kwargs:
        message+=kwargs.get("detail") + "  \n" 

    if type.upper() == "INFO":
       logger.info(message)
    if type.upper() == "WARN":
       logger.warning(message)
    if type.upper() == "ERROR":
       logger.error(message)
    
    # Capture the last log message and update state.md_content
    state.md_content += handler.last_message
    print(handler.last_message)




# def log(type, message, **kwargs):
#   """
#   Appends a message to the "su2gui.log" file.

#   Args:
#       type (str) : The type of message to be appended, like INFO, DEBUG, ERROR, WARN, etc
#       message (str): The message to append to the log.
#       detail (str) : Details of message, Not necessary 

#   """
  
#   timestamp = datetime.now().isoformat(sep=' ', timespec='microseconds')
#   message = f"{timestamp} [{type}]: {message}\n"
#   if "detail" in kwargs:
#     message+=kwargs.get("detail") + "\n" 

#   state.md_content += message
#   print(message)

#   try:
#     with open("./user/su2gui.log", "a") as f:
#       f.write(message + "\n")
#       f.close()
#   except FileNotFoundError:
#     print("Log file 'su2gui.log' not found. Creating a new one.")
#     with open("su2gui.log", "w") as f:  # Create a new file if it doesn't exist
#       f.write(message + "\n")
#   except Exception as e:
#     print(f"An error occurred while appending to log: {e}")

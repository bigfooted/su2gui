# monitor gittree menu

# note that in the main menu, we need to call add the following:
# 1) from monitor import *
# 2) call monitor_card() in SinglePageWithDrawerLayout
# 3) define a node in the gittree (pipeline)
# 4) define any global state variables that might be needed

# definition of ui_card
from uicard import ui_card, ui_subcard, server
from trame.widgets import vuetify
from su2_json import *

state, ctrl = server.state, server.controller

# monitoring points
#
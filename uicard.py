
#import os, copy
#import pandas as pd
#from trame.app import get_server
#from trame.ui.vuetify import SinglePageWithDrawerLayout
#from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.app import get_server


server = get_server()
#state, ctrl = server.state, server.controller


# Main definition of the card for all gittree items.
def ui_card(title, ui_name):
    with vuetify.VCard(v_show=f"active_ui == '{ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content

# subcard, appearing below the main card. Visible depending on the
# selection in the main card
def ui_subcard(title, sub_ui_name):
    with vuetify.VCard(v_show=f"active_sub_ui == '{sub_ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content

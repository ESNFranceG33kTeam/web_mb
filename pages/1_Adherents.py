"""
#############################################
#
# 1_Adherents.py
#
# Adherents page
#
#############################################
"""
import streamlit as st
from adherent import Adherent


st.set_page_config(
    page_title="Check",
    page_icon=":busts_in_silhouette:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.write("# Adherents")

my_adherents = Adherent()
my_adherents.get_data()

PAGES = {
    "List": [my_adherents.list_adherents, my_adherents.update_adherent],
    "New": [my_adherents.new_adherent],
}
selection = st.sidebar.radio(
    "Navigation adherent", list(PAGES.keys()), label_visibility="hidden"
)

if my_adherents.json_pd is None:
    st.warning("Data is empty !")
else:
    for page in PAGES[selection]:
        page()
        st.markdown("---")
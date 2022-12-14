"""
#############################################
#
# adherent.py
#
# object for adherent call
#
#############################################
"""
import json
from datetime import date
from datetime import datetime
import pandas as pd
import streamlit as st
from system import Call
from controllers.money import Money
from helpers import Configuration


class Adherent:
    """Adherent class.
    Everything about adherent object.
    """

    def __init__(self):
        """Init Adherent object."""
        self.endpoint = "auth/adherents"
        self.json_pd = None
        self.recom_adhesion_price = 5
        self.label = "adherent"
        self.req_code = 0

        # Put/Post adherent
        self.id_adh = 0
        self.firstname_adh = ""
        self.lastname_adh = ""
        self.email_adh = ""
        self.dateofbirth_adh = date(1970, 1, 1)
        self.student_adh = False
        self.university_adh = ""
        self.homeland_adh = ""
        self.speakabout_adh = ""
        self.newsletter_adh = False
        self.adhesion_price_adh = self.recom_adhesion_price

    def get_data(self):
        """Get adherent data."""
        get_list = Call()

        get_list.req_url(endpoint=self.endpoint, protocol="get")
        self.req_code = get_list.status_code

        if get_list.status_code != 200:
            st.warning(get_list.error)
            return

        if get_list.response is None:
            return

        for adh in get_list.response:
            del adh["created_at"]
            del adh["updated_at"]

        json_dec = json.dumps(get_list.response)
        self.json_pd = pd.read_json(json_dec)
        self.json_pd.set_index("id", inplace=True)

    def post_put_data(self, protocol: str):
        """Post or put adherent data.

        Args:
            protocol: protocol to use, can be `post` or `put`
        """
        post_put_adh = Call()

        data = {
            "firstname": f"{self.firstname_adh}",
            "lastname": f"{self.lastname_adh}",
            "email": f"{self.email_adh}",
            "dateofbirth": f"{self.dateofbirth_adh}",
            "student": self.student_adh,
            "university": f"{self.university_adh}",
            "homeland": f"{self.homeland_adh}",
            "speakabout": f"{self.speakabout_adh}",
            "newsletter": self.newsletter_adh,
        }

        if protocol == "put":
            self.endpoint = self.endpoint + "/" + str(self.id_adh)

        post_put_adh.req_url(endpoint=self.endpoint, data=data, protocol=protocol)
        self.req_code = post_put_adh.status_code

        if post_put_adh.status_code != 200:
            st.warning(post_put_adh.error)

    def list_adherents(self):
        """List adherents."""
        st.write("## List of Adherents !")

        if self.json_pd is None:
            st.warning("Data is empty !")
            return

        s_filter = st.checkbox("Search filters", False, key="adh_search")
        if s_filter:
            f_col, l_col, _ = st.columns([1, 1, 5])
            fname_filter = f_col.checkbox("Firstname", True, key="adh_fname")
            lname_filter = l_col.checkbox("Lastname", False, key="adh_lname")

            selected_firstname = st.selectbox(
                "Select firstname :",
                self.json_pd["firstname"],
                disabled=not fname_filter,
                key="adh_sfname",
            )
            selected_lastname = st.selectbox(
                "Select lastname :",
                self.json_pd["lastname"],
                disabled=not lname_filter,
                key="adh_slname",
            )

            s_fname = selected_firstname if fname_filter else ""
            s_lname = selected_lastname if lname_filter else ""

            if fname_filter and lname_filter:
                selected_rows = self.json_pd.loc[
                    (self.json_pd["firstname"] == s_fname)
                    & (self.json_pd["lastname"] == s_lname)
                ]
            elif fname_filter or lname_filter:
                selected_rows = self.json_pd.loc[
                    (self.json_pd["firstname"] == s_fname)
                    | (self.json_pd["lastname"] == s_lname)
                ]
            else:
                selected_rows = self.json_pd

            data_adh = selected_rows
        else:
            data_adh = self.json_pd

        st.write(data_adh)

    def update_adherent(self):
        """Update an adherent to the api."""
        st.write("## Update an Adherent")
        st.markdown(
            "If you want to auto complete most of the item, selected the `id` of the adherent."
        )

        if self.json_pd is None:
            st.warning("Data is empty !")
            return

        up_adh = st.checkbox("Update an Adherent ?", False)

        if up_adh:
            selected_indices = st.selectbox("Select rows:", self.json_pd.index)

            with st.form("Update", clear_on_submit=False):
                self.id_adh = st.number_input("id", selected_indices)
                self.firstname_adh = st.text_input(
                    "Firstname", self.json_pd.loc[selected_indices, "firstname"]
                )
                self.lastname_adh = st.text_input(
                    "Lastname", self.json_pd.loc[selected_indices, "lastname"]
                )
                self.email_adh = st.text_input(
                    "Email", self.json_pd.loc[selected_indices, "email"]
                )
                date_format = datetime.strptime(
                    self.json_pd.loc[selected_indices, "dateofbirth"], "%Y-%m-%d"
                )
                self.dateofbirth_adh = st.date_input("Date of birth", date_format)
                self.student_adh = st.checkbox(
                    "Student ?", self.json_pd.loc[selected_indices, "student"]
                )
                self.university_adh = st.selectbox(
                    "University",
                    Configuration().universities,
                    Configuration().universities.index(
                        self.json_pd.loc[selected_indices, "university"]
                    ),
                )
                self.homeland_adh = st.text_input(
                    "Homeland", self.json_pd.loc[selected_indices, "homeland"]
                )
                self.speakabout_adh = st.text_input(
                    "How does he learn about us ?",
                    self.json_pd.loc[selected_indices, "speakabout"],
                )
                self.newsletter_adh = st.checkbox(
                    "Newsletter ?", self.json_pd.loc[selected_indices, "newsletter"]
                )

                submitted = st.form_submit_button("Submit")
                if submitted:
                    if self.id_adh != 0 and len(self.firstname_adh) > 0:
                        self.post_put_data(protocol="put")
                        if self.req_code == 200:
                            st.success("Adherent updated ??????")
                    else:
                        st.warning(
                            """
                            You forget some info...

                            The `firstname`, `lastname` are **MANDATORY**.
                            """
                        )

    def new_adherent(self):
        """Create a new adherent."""
        st.write("## Create a new Adherent")

        with st.form("New adherent", clear_on_submit=True):
            self.firstname_adh = st.text_input("Firstname")
            self.lastname_adh = st.text_input("Lastname")
            self.email_adh = st.text_input("Email")
            self.dateofbirth_adh = st.date_input(
                "Date of birth", self.dateofbirth_adh, max_value=date.today()
            )
            self.student_adh = st.checkbox("Student ?")
            self.university_adh = st.selectbox(
                "University", Configuration().universities
            )
            self.homeland_adh = st.text_input("Homeland")
            self.speakabout_adh = st.text_input("How does she/he learned about us ?")

            st.markdown("---")
            self.newsletter_adh = st.checkbox("Newsletter")
            terms_adh = st.checkbox("I declare to accept the terms and conditions.")
            self.adhesion_price_adh = st.number_input(
                f"Adhesion price, the recommended price is {self.recom_adhesion_price}???",
                value=self.recom_adhesion_price,
            )

            submitted = st.form_submit_button("Submit")
            if submitted:
                if terms_adh and (
                    len(self.firstname_adh) > 0 and len(self.lastname_adh) > 0
                ):
                    # Post adherent
                    self.post_put_data(protocol="post")
                    # Post money
                    adh_money = Money()
                    adh_money.label = self.label
                    adh_money.price = self.adhesion_price_adh
                    adh_money.post_data()

                    if self.req_code == 200 and adh_money.req_code == 200:
                        st.success("Adherent and money operation added ??????")
                    else:
                        error_add_adh = (
                            "Add adherent : " + str(self.req_code)
                            if self.req_code != 200
                            else "Add adherent : OK"
                        )
                        error_add_mon = (
                            "Add money operation : " + str(adh_money.req_code)
                            if adh_money.req_code != 200
                            else "Add money operation : OK"
                        )
                        st.error(f"{error_add_adh} | {error_add_mon}")
                else:
                    st.warning(
                        """
                        You forget some info...

                        The `firstname`, `lastname`, `terms and conditions` are **MANDATORY**.
                        """
                    )

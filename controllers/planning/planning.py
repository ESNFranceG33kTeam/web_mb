"""
#############################################
#
# planning.py
#
# object for planning call
#
#############################################
"""
import os
import json
from datetime import date, time, datetime, timedelta
from calendar_view.calendar import Calendar
from calendar_view.core.event import Event
from calendar_view.core import data
import pandas as pd
import streamlit as st
from system import Call


class Planning:
    """Planning class.
    Everything about planning object.
    """

    def __init__(self):
        """Init Planning object."""
        self.endpoint = "auth/plannings"
        self.json_pd = None
        self.label = "planning"
        self.req_code = 0

        # Put/Post planning
        self.id_pla = 0
        self.name_pla = ""
        self.location_pla = "Mars"
        self.date_begins_pla = date(1970, 1, 1)
        self.date_end_pla = date(1970, 1, 1)
        self.hour_begins_pla = time(0, 0, 0)
        self.hour_end_pla = time(23, 59, 59)

        # Calendar view
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cal_pla = "{}/{}/".format(current_dir, "../../resources") + "cal_pla.png"

    def get_data(self):
        """Get planning data."""
        get_list = Call()

        get_list.req_url(endpoint=self.endpoint, protocol="get")
        self.req_code = get_list.status_code

        if get_list.status_code != 200:
            st.warning(get_list.error)
            return

        if get_list.response is None:
            return

        json_dec = json.dumps(get_list.response)
        self.json_pd = pd.read_json(json_dec)
        self.json_pd.set_index("id", inplace=True)
        self.json_pd["date_begins"] = pd.to_datetime(self.json_pd["date_begins"])
        self.json_pd["date_begins"] = self.json_pd["date_begins"].dt.strftime(
            "%Y-%m-%d"
        )
        self.json_pd["date_end"] = pd.to_datetime(self.json_pd["date_end"])
        self.json_pd["date_end"] = self.json_pd["date_end"].dt.strftime("%Y-%m-%d")

        self.json_pd["hour_begins"] = pd.to_datetime(self.json_pd["hour_begins"])
        self.json_pd["hour_begins"] = self.json_pd["hour_begins"].dt.strftime("%H:%M")
        self.json_pd["hour_end"] = pd.to_datetime(self.json_pd["hour_end"])
        self.json_pd["hour_end"] = self.json_pd["hour_end"].dt.strftime("%H:%M")

    def post_put_data(self, protocol: str):
        """Post or put planning data.

        Args:
            protocol: protocol to use, can be `post` or `put`
        """
        post_put_pla = Call()

        data_pla = {
            "name": f"{self.name_pla}",
            "location": f"{self.location_pla}",
            "date_begins": f"{self.date_begins_pla}",
            "date_end": f"{self.date_end_pla}",
            "hour_begins": f"{self.hour_begins_pla}",
            "hour_end": f"{self.hour_end_pla}",
        }

        if protocol == "put":
            self.endpoint = self.endpoint + "/" + str(self.id_pla)

        post_put_pla.req_url(endpoint=self.endpoint, data=data_pla, protocol=protocol)
        self.req_code = post_put_pla.status_code

        if post_put_pla.status_code != 200:
            st.warning(post_put_pla.error)

    def view_planning(self):
        """View all Planning."""
        st.write("### View all plannings")

        if self.json_pd is None:
            st.warning("Data is empty !")
            return

        def gen_cal():
            """Function to gen the calendar."""
            config = data.CalendarConfig(
                lang="en",
                title="Plannings",
                dates=f"{st.session_state['begin_cal']} - {st.session_state['end_cal']}",
                show_year=True,
                mode=None,
                legend=False,
            )
            events = []
            for name, date_begins, date_end, hour_begins, hour_end in zip(
                self.json_pd["name"],
                self.json_pd["date_begins"],
                self.json_pd["date_end"],
                self.json_pd["hour_begins"],
                self.json_pd["hour_end"],
            ):
                if date_begins != date_end:
                    events.append(
                        Event(
                            title=name,
                            day=date_begins,
                            start=hour_begins,
                            end=time(23, 59),
                        )
                    )
                    events.append(
                        Event(title=name, day=date_end, start=time(0, 00), end=hour_end)
                    )
                else:
                    events.append(
                        Event(name, day=date_begins, start=hour_begins, end=hour_end)
                    )

            data.validate_config(config)
            data.validate_events(events, config)
            calendar = Calendar.build(config)
            calendar.add_events(events)
            calendar.save(self.cal_pla)

        st.date_input("Date begins", value=date.today(), key="begin_cal")
        st.date_input(
            "Date end", value=(date.today() + timedelta(days=6)), key="end_cal"
        )

        if (
            st.checkbox("View plannings")
            and st.session_state["begin_cal"] != st.session_state["end_cal"]
            and st.session_state["begin_cal"] < st.session_state["end_cal"]
        ):
            gen_cal()
            st.image(self.cal_pla)

    def list_plannings(self):
        """List plannings."""
        st.write("## List of Plannings !")

        if self.json_pd is None:
            st.warning("Data is empty !")
            return

        s_filter = st.checkbox("Search filters", False)
        if s_filter:
            f_col, _, _ = st.columns([1, 1, 5])
            fname_filter = f_col.checkbox("Name", True)
            fold_filter = f_col.checkbox("Past", False)

            selected_name = st.selectbox(
                "Select name :",
                self.json_pd["name"],
                disabled=not fname_filter,
            )

            s_fname = selected_name if fname_filter else ""

            if fname_filter and fold_filter:
                selected_rows = self.json_pd.loc[
                    (self.json_pd["name"] == s_fname)
                    & (
                        pd.to_datetime(self.json_pd["date_end"])
                        <= pd.to_datetime("today")
                    )
                ]
            elif fname_filter or fold_filter:
                selected_rows = self.json_pd.loc[
                    (self.json_pd["name"] == s_fname)
                    | (
                        pd.to_datetime(self.json_pd["date_end"])
                        <= pd.to_datetime("today")
                    )
                ]
            else:
                selected_rows = self.json_pd.loc[
                    (
                        pd.to_datetime(self.json_pd["date_end"])
                        >= (pd.to_datetime("today") - pd.Timedelta("1 days"))
                    )
                ]

            data_pla = selected_rows
        else:
            data_pla = self.json_pd.loc[
                (
                    pd.to_datetime(self.json_pd["date_end"])
                    >= (pd.to_datetime("today") - pd.Timedelta("1 days"))
                )
            ]

        st.write(data_pla)

    def update_planning(self):
        """Update a planning to the api."""
        st.write("## Update a Planning")
        st.markdown(
            "If you want to auto complete most of the item, selected the `id` of the planning."
        )

        if self.json_pd is None:
            st.warning("Data is empty !")
            return

        up_pla = st.checkbox("Update a Planning ?", False)

        if up_pla:
            selected_indices = st.selectbox("Select rows:", self.json_pd.index)

            with st.form("Update", clear_on_submit=False):
                self.id_pla = st.number_input("id", selected_indices)
                self.name_pla = st.text_input(
                    "Name", self.json_pd.loc[selected_indices, "name"]
                )
                self.location_pla = st.text_input(
                    "Location", self.json_pd.loc[selected_indices, "location"]
                )
                date_begins_format = datetime.strptime(
                    self.json_pd.loc[selected_indices, "date_begins"], "%Y-%m-%d"
                )
                self.date_begins_pla = st.date_input("Date begins", date_begins_format)
                date_end_format = datetime.strptime(
                    self.json_pd.loc[selected_indices, "date_end"], "%Y-%m-%d"
                )
                self.date_end_pla = st.date_input("Date end", date_end_format)
                hour_begins_format = datetime.strptime(
                    self.json_pd.loc[selected_indices, "hour_begins"], "%H:%M"
                )
                self.hour_begins_pla = st.time_input("Hour begins", hour_begins_format)
                hour_end_format = datetime.strptime(
                    self.json_pd.loc[selected_indices, "hour_end"], "%H:%M"
                )
                self.hour_end_pla = st.time_input("Hour end", hour_end_format)

                submitted = st.form_submit_button("Submit")
                if submitted:
                    if self.id_pla != 0 and len(self.name_pla) > 0:
                        self.post_put_data(protocol="put")
                        if self.req_code == 200:
                            st.success("Planning updated ??????")
                        else:
                            error_up_eve = (
                                "Update planning : " + str(self.req_code)
                                if self.req_code != 200
                                else "Update planning : OK"
                            )
                            st.error(f"{error_up_eve}")
                    else:
                        st.warning(
                            """
                            You forget some info...

                            All fields are **MANDATORY**.
                            """
                        )

    def new_planning(self):
        """Create a new planning."""
        st.write("## Create a new Planning")

        with st.form("New planning", clear_on_submit=True):
            self.name_pla = st.text_input("Name")
            self.location_pla = st.text_input("Location")
            self.date_begins_pla = st.date_input("Date begins", value=date.today())
            self.date_end_pla = st.date_input("Date end", value=date.today())
            self.hour_begins_pla = st.time_input("Hour begins")
            self.hour_end_pla = st.time_input("Hour end")

            print("End : ", self.hour_end_pla)

            submitted = st.form_submit_button("Submit")
            if submitted:
                if len(self.name_pla) > 0 and len(self.location_pla) > 0:
                    # Post planning
                    self.post_put_data(protocol="post")

                    if self.req_code == 200:
                        st.success("Planning added ??????")
                    else:
                        error_add_eve = (
                            "Add planning : " + str(self.req_code)
                            if self.req_code != 200
                            else "Add planning : OK"
                        )
                        st.error(f"{error_add_eve}")
                else:
                    st.warning(
                        """
                        You forget some info...

                        The `name`, `location` are **MANDATORY**.
                        """
                    )

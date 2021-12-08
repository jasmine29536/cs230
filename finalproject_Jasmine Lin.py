"""
Class: CS230--Section 1
Name: Jasmine Lin
Description: (Final CS230 Project that reads in a csv file and then manipulates the data to show charts and maps.)
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. 
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import matplotlib.pyplot as plt


# read in data
def read_data():
    return pd.read_csv("bostoncrime2021_7000_samples.csv").set_index("INCIDENT_NUMBER")


# filter data
def filter_data(sel_districts, sel_offense, sel_hours):
    df = read_data()
    df = df.loc[df['DISTRICT'].isin(sel_districts)]
    df = df.loc[df['OFFENSE_DESCRIPTION'].isin(sel_offense)]
    df = df.loc[df['HOUR'] >= sel_hours]

    return df


def all_districts():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['DISTRICT'] not in lst:
            lst.append(row['DISTRICT'])

    return lst


def all_offenses():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['OFFENSE_DESCRIPTION'] not in lst:
            lst.append(row['OFFENSE_DESCRIPTION'])

    return lst


# counting frequency of a district
def count_districts(districts, df):
    return [df.loc[df["DISTRICT"].isin([district])].shape[0] for district in districts]


def district_hours(df):
    hours = [row['HOUR'] for ind, row in df.iterrows()]
    districts = [row['DISTRICT'] for ind, row in df.iterrows()]

    dict = {}
    for district in districts:
        dict[district] = []

    for i in range(len(hours)):
        dict[districts[i]].append(hours[i])

    return dict


def district_averages(dict_hours):
    dict = {}
    for key in dict_hours.keys():
        dict[key] = np.mean(dict_hours[key])

    return (dict)


# pie chart
def generate_pie_chart(counts, sel_districts):
    plt.figure()

    explodes = [0 for i in range(len(counts))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] = 0.25
    plt.pie(counts, labels=sel_districts, explode=explodes, autopct="%.2f")
    plt.title(f"Crime Frequency in Each District: {', '.join(sel_districts)}")

    return plt


def generate_bar_chart(dict_averages):
    plt.figure()
    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y)
    plt.xticks(rotation=45)
    plt.ylabel("Hour")
    plt.xlabel("Districts")
    plt.title(f"Average Hour Crime Occurs in Each Area: {', '.join(dict_averages.keys())}")

    return plt


def generate_map(df):
    map_df = df.filter(['OFFENSE_DESCRIPTION', 'Lat', 'Long'])

    view_state = pdk.ViewState(latitude=map_df["Lat"].median(),
                               longitude=map_df["Long"].median(),
                               zoom=12)
    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[Long, Lat]',
                      get_radius=120,
                      get_color=[255, 201, 14],
                      pickable=True)

    tool_tip = {'html': 'Incident:<br/> <b>{OFFENSE_DESCRIPTION}</b>',
                'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
    st.pydeck_chart(map)


def main():
    st.title("Data Visualization with Python")
    st.header("Welcome to this Boston Crime 2021 Data! ")
    st.caption("Please open the sidebar to begin.")

    st.sidebar.write("Please choose your options to display data.")
    districts = st.sidebar.multiselect("Select a district: ", all_districts())
    offense = st.sidebar.multiselect("Select an offense: ", all_offenses())
    hours = st.sidebar.slider("Hour", 1, 24)

    data = filter_data(districts, offense, hours)
    series = count_districts(districts, data)

    if len(districts) > 0 and len(offense) > 0 and hours >= 0:
        st.subheader("View a Map of Crimes")
        generate_map(data)
        st.write("This is the map of the districts chosen and any of the corresponding crimes."
                 "The crimes are shown on the map by a yellow dot and if the user hovers across the dot, "
                 "the Offense description pops up. The map can be zoomed in and out. ")

        st.subheader("View a Pie Chart")
        st.pyplot(generate_pie_chart(series, districts))
        st.write("The pie chart counts all of the crimes that were accounted for in the Boston Area's police forces."
                 "The pie is divided into the number of districts chosen by the user, and displays the percentage out of 100% "
                 "that each district has crimes compared to others.")

        st.subheader("View a Bar Chart")
        st.pyplot(generate_bar_chart(district_averages(district_hours(data))))
        st.write("The bar chart displays the average hour crime occurs in each area."
                 "The user has control over what time they want to cut off the reports. "
                 "If the user leaves the selection at one than all of the reports in a specific district are accounted for."
                 "If the user moves the slider to 18, than any crimes occuring before hour 18, will not be accounted for. "
                 "As the incidents are recorded using military time, there are 24 hours. "
                 "If the average is higher than 12.0 than there shows that crime is more likely to occur in the afternoon to night time."
                 "Whereas if the average is less than 12.0 than crime is more likely to occur in the early mornings."
                 "If the barchart is observed at each hour, then one could examine the difference in average hour of crime, "
                 "if there is a change, then that hour was crucial to the district, and vice versa.")

        st.caption("Created by Jasmine Lin"
                   "CS230: Final Project"
                   "Professor Masloff")


main()

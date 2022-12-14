import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components

FILE = "volcanoes_dataset.csv"
IMAGE = "Volcano Photo.jpeg"


def read_data(file):

    df = pd.read_csv(file)
    df = df.rename(columns={'Primary Volcano Type': 'Volcano Type',
                            'Activity Evidence': 'Activity', 'Dominant Rock Type': 'Rock Type'})

    return df


def map_maker(df):

    df_map = pd.DataFrame().assign(lat=df['Latitude'], lon=df['Longitude'], volcano=df['Volcano Name'])

    return df_map


def eruption_highest(df):
    df.replace('Unknown', None)
    df.dropna()
    df_eruptions = df['Last Known Eruption'].unique()
    list_eruptions = []
    for x in df_eruptions:
        if "BCE" not in x:
            list_eruptions.append(x)
    list_eruptions = list_eruptions[1:]
    most_recent_eruption = 0
    for i in range(len(list_eruptions)):
        if int(list_eruptions[i][:-3]) > most_recent_eruption:
            most_recent_eruption = int(list_eruptions[i][:-3])
    eruption_date = []
    for i in range(len(list_eruptions)):
        if int(list_eruptions[i][:-3]) == most_recent_eruption:
            eruption_date.append(list_eruptions[i])

    return eruption_date


def main():

    df = read_data(FILE)
    st.title(f"Final Project ------------ Marisa Geary")
    selected = option_menu(None, ["Home", "Data", "Map", 'Charts'],
                           icons=['house',
                                  'clipboard-data',
                                  "geo-alt",
                                  'graph-down'],
                           menu_icon="cast",
                           default_index=0,
                           orientation="horizontal")
    if selected == "Home":
        st.write("Hello there!  \n  In this project, I analyze and display data from a dataset containing information "
                 "about 1,413 different volcanoes around the world. Navigate around this project to view different "
                 "maps and charts I included. Enjoy!")
        st.image(IMAGE)

    if selected == "Data":
        st.write(df)
        st.title("Statistics")
        elevation = df['Elevation (m)'].unique()
        high = df["Elevation (m)"].idxmax()
        low = df["Elevation (m)"].idxmin()
        st.write(f"The volcano with the highest elevation is")
        st.write(df.iloc[[high]])
        st.write(f"The volcano with the lowest elevation is")
        st.write(df.iloc[[low]])
        eruption_date = eruption_highest(df)
        st.write("The most recent eruptions are")
        st.write(df.loc[df['Last Known Eruption'] == eruption_date[0]])

        if st.checkbox("Show code"):
            st.code("""
def eruption_highest(df):
    df.replace('Unknown', None)
    df.dropna()
    df_eruptions = df['Last Known Eruption'].unique()
    list_eruptions = []
    for x in df_eruptions:
        if "BCE" not in x:
            list_eruptions.append(x)
    list_eruptions = list_eruptions[1:]
    most_recent_eruption = 0
    for i in range(len(list_eruptions)):
        if int(list_eruptions[i][:-3]) > most_recent_eruption:
            most_recent_eruption = int(list_eruptions[i][:-3])
    eruption_date = []
    for i in range(len(list_eruptions)):
        if int(list_eruptions[i][:-3]) == most_recent_eruption:
            eruption_date.append(list_eruptions[i])

    return eruption_date

st.write(df)
st.title("Statistics")
elevation = df['Elevation (m)'].unique()
high = df["Elevation (m)"].idxmax()
low = df["Elevation (m)"].idxmin()
st.write(f"The volcano with the highest elevation is")
st.write(df.iloc[[high]])
st.write(f"The volcano with the lowest elevation is")
st.write(df.iloc[[low]])
eruption_date = eruption_highest(df)
st.write("The most recent eruptions are")
st.write(df.loc[df['Last Known Eruption'] == eruption_date[0]])

""")

    if selected == "Map":
        with st.sidebar:
            st.write("Select type of map.")
            chart_selection = st.selectbox("What data would you like to look at?", ["Location", "Heat"])
        if chart_selection == "Location":
            with st.sidebar:
                st.write("Select at least one region and at least one activity level to display relevant volcanic "
                         "eruptions on the map.")
                df['Activity'] = df['Activity'].replace(['Uncertain Evidence'], 'Evidence Uncertain')
                df['Activity'] = df['Activity'].replace(['Eruption Dated'], 'Confirmed Eruption')
                df['Activity'] = df['Activity'].replace(['Eruption Observed'], 'Confirmed Eruption')
                regions = df['Region'].unique()
                activity = df['Activity'].unique()
                select_region = st.multiselect("Sort by region:", regions)
                select_activity = st.multiselect("Sort by activity:", activity)
            regions_df = df.query('Region == @select_region and Activity == @select_activity')
            regions_map = map_maker(regions_df)
            st.map(regions_map)
            if st.checkbox("Show code"):
                st.code("""
df['Activity'] = df['Activity'].replace(['Uncertain Evidence'], 'Evidence Uncertain')
df['Activity'] = df['Activity'].replace(['Eruption Dated'], 'Confirmed Eruption')
df['Activity'] = df['Activity'].replace(['Eruption Observed'], 'Confirmed Eruption')
regions = df['Region'].unique()
activity = df['Activity'].unique()
select_region = st.multiselect("Sort by region:", regions)
select_activity = st.multiselect("Sort by activity:", activity)
regions_df = df.query('Region == @select_region and Activity == @select_activity')
regions_map = map_maker(regions_df)
st.map(regions_map)""")
        if chart_selection == "Heat":
            lat = df.Latitude.tolist()
            lng = df.Longitude.tolist()

            m = folium.Map(
                location=[0, 0],
                tiles='OpenStreetMap',
                zoom_start=3
            )
            HeatMap(list(zip(lat, lng))).add_to(m)
            m.save("heat_map.html")
            p = open("heat_map.html")
            components.html(p.read(), width=700, height=600)
            if st.checkbox("Show code"):
                st.code("""
lat = df.Latitude.tolist()
lng = df.Longitude.tolist()

m = folium.Map(
        location=[0, 0],
        tiles='OpenStreetMap',
        zoom_start=3
        )
HeatMap(list(zip(lat, lng))).add_to(m)
m.save("heat_map.html")
p = open("heat_map.html")
components.html(p.read(), width=700, height=800)""")

    if selected == 'Charts':
        chart_selection = st.selectbox("What data would you like to look at?", ["Rock Type", "Volcano Type"])
        if chart_selection == "Rock Type":
            rocks = df['Rock Type'].value_counts()
            data = rocks.values
            labels = rocks.index
            with st.sidebar:
                st.write("Select chart type below.")
                select_chart = st.selectbox("Select chart:", ['Bar', 'Pie'])

            if select_chart == "Pie":
                fig, ax = plt.subplots()
                ax.pie(data)
                ax.axis('equal')
                percents = 100 * data / sum(data)
                label_percent_pairs = [(label, f'{percent:.1f}%') for label, percent in zip(labels, percents)]
                plt.legend(label_percent_pairs, title='Rock Type Key', loc="best", fontsize='5')
                st.pyplot(fig)
                if st.checkbox("Show code"):
                    st.code("""
                fig, ax = plt.subplots()
ax.pie(data)
ax.axis('equal')
percents = 100 * data / sum(data)
label_percent_pairs = [(label, f'{percent:.1f}%') for label, percent in zip(labels, percents)]
plt.legend(label_percent_pairs, title='Rock Type Key', loc="best", fontsize='5')
st.pyplot(fig)""")

            if select_chart == "Bar":
                fig, ax = plt.subplots()
                ax.set_xticks(range(len(data)))
                ax.set_xticklabels(labels, rotation = 90)
                ax.set_xlabel('Rock Type')
                ax.set_ylabel('# of Rock Type')
                ax.set_title('Rock Types')
                bars = ax.bar(range(len(data)), data, color=['red', 'green', 'blue'])
                st.pyplot(fig)
                if st.checkbox("Show code"):
                    st.code("""
                fig, ax = plt.subplots()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(labels, rotation = 90)
ax.set_xlabel('Rock Type')
ax.set_ylabel('# of Rock Type')
ax.set_title('Rock Types')
bars = ax.bar(range(len(data)), data, color=['red', 'green', 'blue'])
st.pyplot(fig)""")

        if chart_selection == "Volcano Type":
            volcanoes = df['Volcano Type'].value_counts()
            data = volcanoes.values
            labels = volcanoes.index
            with st.sidebar:
                st.write("Select chart type below.")
                select_chart = st.selectbox("Select chart:", ['Bar', 'Line'])

            if select_chart == "Bar":
                fig, ax = plt.subplots()
                ax.set_xticks(range(len(data)))
                ax.set_xticklabels(labels, rotation=90)
                ax.set_xlabel('Volcano Type')
                ax.set_ylabel('# of Volcano Type')
                ax.set_title('Volcano Types')
                bars = ax.bar(range(len(data)), data, color=['red', 'green', 'blue'])
                st.pyplot(fig)
                if st.checkbox("Show code"):
                    st.code("""
fig, ax = plt.subplots()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(labels, rotation=90)
ax.set_xlabel('Volcano Type')
ax.set_ylabel('# of Volcano Type')
ax.set_title('Volcano Types')
bars = ax.bar(range(len(data)), data, color=['red', 'green', 'blue'])
st.pyplot(fig)
                    """)

            if select_chart == "Line":
                fig, ax = plt.subplots()
                ax.set_xticks(range(len(data)))
                ax.set_xticklabels(labels, rotation=90)
                ax.plot(range(len(data)), data, color="purple")
                ax.plot(range(len(data)), data, "o", color="black")
                ax.set_title('Volcano Types')
                ax.set_xlabel('Volcano Type')
                ax.set_ylabel('# of Volcano Type')
                st.pyplot(fig)
                if st.checkbox("Show code"):
                    st.code("""
fig, ax = plt.subplots()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(labels, rotation=90)
ax.plot(range(len(data)), data, color="purple")
ax.plot(range(len(data)), data, "o", color="black")
ax.set_title('Volcano Types')
ax.set_xlabel('Volcano Type')
ax.set_ylabel('# of Volcano Type')
st.pyplot(fig)""")


if __name__ == "__main__":
    main()

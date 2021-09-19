# https://docs.streamlit.io/en/stable/tutorial/create_a_data_explorer_app.html

# data explorer app using uber's pickups and dropoffs

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# wide mode
# st.set_page_config(layout="wide")

st.title("Uber Pickups in NYC")


# load data
DATE_COLUMN = "date/time"
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


# Create a text element and let the reader know the data is loading.
data_load_state = st.text("Loading data...")
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

# Maps function (overwrite)


def map_1(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=10,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )


if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)


# histogram of pickups per hour
st.subheader("Number of pickups by hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
st.bar_chart(hist_values)  # supports other libraries as well

# map - all pickups
st.subheader("Map of all pickups")
st.map(data)

# map - all pickups with density
st.subheader("Map of density of all pickups")
midpoint = (np.average(data["lat"]), np.average(data["lon"]))
map_1(data, midpoint[0], midpoint[1], 11)

# map - pickups for different hours based on slider
hour_to_filter = st.slider("hour", 0, 23, 17)  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f"Map of all pickups at {hour_to_filter}:00")
st.map(filtered_data)

la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12

st.subheader(f"La Guardia Airport at {hour_to_filter}:00")
map_1(data, la_guardia[0], la_guardia[1], zoom_level)

st.subheader(f"JFK at {hour_to_filter}:00")
map_1(data, jfk[0], jfk[1], zoom_level)

st.subheader(f"Newark at {hour_to_filter}:00")
map_1(data, newark[0], newark[1], zoom_level)
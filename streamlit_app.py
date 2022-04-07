import pandas as pd
import streamlit as app
from datetime import date
from datetime import timedelta
import requests
import json

nasa_potd = requests.get("https://api.nasa.gov/planetary/apod?api_key=jIUaYAKcKc59QEa9el6p1mFpiBBrRTjMY2rb99f5").json()
space_center_weather = requests.get("https://api.airvisual.com/v2/city?city=cocoa&state=florida&country=usa&key=b6cc269a-2d68-483b-b036-42132725e5ba").json()
spacex_past_launches = requests.get("https://api.spacexdata.com/v5/launches/past").json()

def map_creator(latitude,longitude):
    from streamlit_folium import folium_static
    import folium
    # center on the station
    f = folium.Figure(width=300, height=250)
    m = folium.Map(location=[latitude, longitude], zoom_start=2, max_bounds=True).add_to(f)
    # add marker for the station
    folium.Marker([latitude, longitude], popup="International Space Station", tooltip="International Space Station").add_to(m)
    # call to render Folium map in Streamlit
    folium_static(f)

app.title("SPACE!")

nasa_key = "jIUaYAKcKc59QEa9el6p1mFpiBBrRTjMY2rb99f5"
nasa_launch_location = {
    "latitude": 28.573469,
    "longitude": -80.651070
}
app.write("Current ISS Location")
iss_position = requests.get("http://api.open-notify.org/iss-now.json").json()
map_creator(iss_position["iss_position"]["latitude"], iss_position["iss_position"]["longitude"])

app.write("Fact of the day: {0}".format(nasa_potd["explanation"]))
app.image(nasa_potd["hdurl"], width=400)

space_center_temp = space_center_weather["data"]["current"]["weather"]["tp"]
space_center_humid = space_center_weather["data"]["current"]["weather"]["hu"]
space_station_weather = app.radio('Select a unit', options=('F', 'C'))
app.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
if space_station_weather == 'C':
    app.write("Kennedy Space Center Weather: {0} degrees with {1}% humidity".format(space_center_temp, space_center_humid))
elif space_station_weather == 'F':
    app.write("Kennedy Space Center Weather: {0} degrees with {1}% humidity".format((space_center_temp*1.8+32), space_center_humid))
else:
    app.write("Not available")

app.write("Timeline of Space X Launches")
launch_years = []
for i in spacex_past_launches:
    d = i["date_utc"]
    current_year = d[0:4]
    launch_years.append(current_year)
spacex_launches = {i:launch_years.count(i) for i in launch_years}
launch_data = pd.Series(spacex_launches)
app.bar_chart(launch_data)


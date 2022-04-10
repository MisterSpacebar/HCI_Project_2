import pandas as pd
import streamlit as app
from datetime import date
from datetime import datetime
import requests
import json

# make page wider
app.set_page_config(layout="wide")

# API requests on page load for non-dynamic routes
spacex_past_launches = requests.get("https://api.spacexdata.com/v5/launches/past").json()
spacex_all_launches = requests.get("https://api.spacexdata.com/v5/launches").json()

# master launch date list
spacex_launch_date_list = []

nasa_key = "jIUaYAKcKc59QEa9el6p1mFpiBBrRTjMY2rb99f5"
nasa_launch_location = {
    "latitude": 28.573469,
    "longitude": -80.651070
}

# makes a map
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

# displays ISS location in relation to globe
def international_space_station():
    app.write("Current ISS Location")
    iss_position = requests.get("http://api.open-notify.org/iss-now.json").json()
    map_creator(iss_position["iss_position"]["latitude"], iss_position["iss_position"]["longitude"])
    # custom CSS to make the outside div a little smaller
    styl = "<style> iframe[title='st.iframe'] {height:100%;width:100%}</style>"
    app.markdown(styl, unsafe_allow_html=True)

def spacex_date_select():
    # date formatting
    date_format = "%Y-%m-%d"
    date_today = date.today()
    # create an array of dates to quickly reference from and to
    launch_dates_now = [""]
    launch_dates_future = [""]
    for index in spacex_all_launches:
        date_temp = index["date_utc"]
        spacex_launch_date_list.append(date_temp[0:10])
        datetime_temp = datetime.strptime(date_temp[0:10],date_format).date()
        if datetime_temp < date_today: # past
            launch_dates_now.append(date_temp[0:10])
        elif datetime_temp > date_today: # future
            launch_dates_future.append(date_temp[0:10])
        else: # present
            launch_dates_now.append(date_temp[0:10])
    col1,col2 = app.columns([1,4])
    with col1:
        # ask user how they want to categorize search
        past_future = app.radio("Present or Future launches?",options=('Present','Future','All Launches'))
        # custom CSS to have the radio buttons in a line
        app.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        templist = [""]
        if past_future == 'Present':
            templist = launch_dates_now
        elif past_future == 'Future':
            templist = launch_dates_future
        else:
            for index in spacex_launch_date_list:
                templist.append(index)
    with col2:
        date_select = app.selectbox("Search or select a launch date (YYYY-MM-DD)...", templist)
    # return the date if true
    if date_select:
        app.write(date_select)
        return date_select
    elif date_select not in templist: # doesn't exist, try again
        app.write("This is not a date, please try again")

def nasa_fotd(api_key):
    nasa_potd = requests.get(
        "https://api.nasa.gov/planetary/apod?api_key={0}".format(api_key)).json()
    # separate image and info into columns
    col1, col2 = app.columns([1,2])
    with col1:
        app.image(nasa_potd["hdurl"], width=450)
    with col2:
        app.write("Fact of the day: {0}".format(nasa_potd["explanation"]))

def space_coast_weather():
    space_center_weather = requests.get(
        "https://api.airvisual.com/v2/city?city=cocoa&state=florida&country=usa&key=b6cc269a-2d68-483b-b036-42132725e5ba").json()
    space_center_temp = space_center_weather["data"]["current"]["weather"]["tp"]
    space_center_humid = space_center_weather["data"]["current"]["weather"]["hu"]
    space_station_weather = app.radio('Select a unit', options=('F', 'C'))
    # custom CSS to have the radio buttons in a line
    app.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    if space_station_weather == 'C':
        app.write("Kennedy Space Center Weather: {0} degrees with {1}% humidity".format(int(space_center_temp),
                                                                                        space_center_humid))
    elif space_station_weather == 'F':
        app.write(
            "Kennedy Space Center Weather: {0} degrees with {1}% humidity".format(int(space_center_temp * 1.8 + 32),
                                                                                  space_center_humid))
    else:
        app.write("Not available")

def past_launch_count():
    app.write("Timeline of Space X Launches")
    # count how many launches per pear by brute force
    launch_years = []
    for i in spacex_past_launches:
        d = i["date_utc"]
        current_year = d[0:4]
        launch_years.append(current_year)
    # turn array into object of 'year':'count'
    spacex_launches = {i: launch_years.count(i) for i in launch_years}
    launch_data = pd.Series(spacex_launches)
    # display chart
    app.bar_chart(launch_data)

app.title("SPACE!")

spacex_date_select()

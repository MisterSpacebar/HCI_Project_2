import pandas as pd
import streamlit as app
import streamlit.components.v1 as components
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
    f = folium.Figure(width=400, height=350)
    m = folium.Map(location=[latitude, longitude], zoom_start=2, max_bounds=True).add_to(f)
    # add marker for the station
    folium.Marker([latitude, longitude], popup="International Space Station", tooltip="International Space Station").add_to(m)
    # call to render Folium map in Streamlit
    folium_static(f)

# displays ISS location in relation to globe
def international_space_station():
    # header for component
    head1,head2 = app.columns(2)
    with head1:
        app.markdown("#### **Current Location of the ISS**")
    with head2:
        app.markdown("#### **People on the ISS**")
    iss_position = requests.get("http://api.open-notify.org/iss-now.json").json()
    iss_personel = requests.get("http://api.open-notify.org/astros.json").json()
    iss_personel = iss_personel['people']
    half = (len(iss_personel) // 2) # must be int
    # content
    col1, col2, col3 = app.columns([2, 1, 1])
    with col1: # ISS map
        map_creator(iss_position["iss_position"]["latitude"], iss_position["iss_position"]["longitude"])
        # custom CSS to make the outside div a little smaller
        styl = "<style> iframe[title='st.iframe'] {height:200%;width:100%}</style>"
        app.markdown(styl, unsafe_allow_html=True)
    with col2: # cut personnel in half
        # write directly to page
        for people in iss_personel[:half]:
            app.write(people['name'])
    with col3: # other half of personnel
        for people in iss_personel[half:]:
            app.write(people['name'])

def now_later_list():
    # structure output
    past_and_future = {'now':[""], 'later':[""]}
    # date formatting
    date_format = "%Y-%m-%d"
    date_today = date.today()
    # create date lists
    for index in spacex_all_launches:
        date_temp = index["date_utc"]
        spacex_launch_date_list.append(date_temp[0:10])
        # format temp variant to date format
        datetime_temp = datetime.strptime(date_temp[0:10],date_format)
        datetime_temp = datetime_temp.date()
        if datetime_temp < date_today: # past
            past_and_future['now'].append(date_temp[0:10])
        elif datetime_temp > date_today: # future
            past_and_future['later'].append(date_temp[0:10])
        else: # present
            past_and_future['now'].append(date_temp[0:10])
    # return object
    return past_and_future

def spacex_date_select():
    # split option and search and arrange them into same row
    col1,col2 = app.columns([1,4])
    with col1: # select past/present/future
        # ask user how they want to categorize search
        past_future = app.radio("Present or Future launches?",options=('Present','Future','All Launches'))
        # custom CSS to have the radio buttons in a line
        app.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        templist = now_later_list()
        if past_future == 'Present':
            templist = templist['now']
        elif past_future == 'Future':
            templist = templist['later']
        else:
            for index in spacex_launch_date_list:
                templist.append(index)
    with col2: # drop-down menu with search
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
    app.markdown("#### **Fact of the Day**")
    # separate image and info into columns
    col1, col2 = app.columns([1,2])
    with col1: # image
        app.image(nasa_potd["hdurl"], width=450)
    with col2: # factoid
        app.write(nasa_potd["explanation"])

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
    # turn array into object with 'year':'count'
    spacex_launches = {i: launch_years.count(i) for i in launch_years}
    launch_data = pd.Series(spacex_launches)
    # display chart
    app.bar_chart(launch_data)

app.title("SPACE!")

spacex_date_select()
nasa_fotd(nasa_key)
international_space_station()

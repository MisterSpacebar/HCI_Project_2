import pandas as pd
import streamlit as app
import streamlit.components.v1 as components
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json

# make page wider
app.set_page_config(layout="wide")

# API requests on page load for non-dynamic routes
spacex_past_launches = requests.get("https://api.spacexdata.com/v5/launches/past").json()
spacex_all_launches = requests.get("https://api.spacexdata.com/v5/launches").json()
# master launch date list
spacex_launch_date_list = []

# image not available photo
image_not_available = "https://cdn.discordapp.com/attachments/961742574408851497/964745979721048064/unknown.png"

nasa_key = "jIUaYAKcKc59QEa9el6p1mFpiBBrRTjMY2rb99f5"
#nasa_launch_location = { "latitude": 28.573469,"longitude": -80.651070 }

# makes a map
def map_creator(latitude,longitude):
    from streamlit_folium import folium_static
    import folium
    # figure will only adjust element size, NOT FOR THE ENTIRE DIV
    f = folium.Figure(width=400, height=350)
    m = folium.Map(location=[latitude, longitude], zoom_start=2, max_bounds=True).add_to(f)
    # add marker for the station location
    folium.Marker([latitude, longitude], popup="International Space Station", tooltip="International Space Station").add_to(m)
    # call to render Folium map in Streamlit
    folium_static(f)

# uses a slide selector to make a fake carousel for images
def slider_carousel(carousel_label,image_array,image_width):
    carousel = app.select_slider(carousel_label,options=image_array,format_func=lambda x:"")
    substring = "youtube.com"
    if substring in carousel: # filter for youtube video
        app.video(carousel)
    else: # regular images
        app.image(carousel,width=image_width)

# displays fact of the day
def nasa_fotd(api_key):
    nasa_potd = requests.get(
        "https://api.nasa.gov/planetary/apod?api_key={0}".format(api_key)).json()
    app.markdown("#### **Fact of the Day**")
    # separate image and info into columns
    col1, col2 = app.columns([1,2])
    with col1: # image
        app.image(nasa_potd["hdurl"], width=450)
    with col2: # factoid
        app.info(nasa_potd["explanation"])

# displays ISS location in relation to globe
def international_space_station():
    # header for component
    head1,head2,head3,head4 = app.columns([2,1,1,2])
    with head1:
        app.markdown("#### **Current Location of the ISS**")
    with head2:
        app.markdown("#### **People on the ISS**")
    with head4:
        app.markdown("#### **Ethnicity on the ISS**")
    iss_position = requests.get("http://api.open-notify.org/iss-now.json").json()
    iss_personel = requests.get("http://api.open-notify.org/astros.json").json()
    # only care about names for now
    iss_personel = iss_personel['people']
    half = (len(iss_personel) // 2) # must be int
    # content
    col1,col2,col3,col4 = app.columns([2,1,1,2])
    with col1: # ISS map
        map_creator(iss_position["iss_position"]["latitude"], iss_position["iss_position"]["longitude"])
        # custom CSS to make the outside div a little smaller
        # margin-bottom is semi-necessarily is there are elements under this element; can overlap
        app.markdown("<style> iframe[title='st.iframe'] {height:200%;width:100%;margin-bottom:25%}</style>", unsafe_allow_html=True)
    with col2: # cut personnel in half
        # write directly to page
        for people in iss_personel[:half]:
            app.write(people['name'])
    with col3: # other half of personnel
        for people in iss_personel[half:]:
            app.write(people['name'])
    with col4:
        # pie chart with ISS astronaut ethnicities
        ethnicities = []
        # isolate ethnicities by last name
        for astronaut in iss_personel:
            astronaut_name = astronaut["name"]
            # isolate last name
            astronaut_last_name = astronaut_name.split()
            astronaut_last_name = astronaut_last_name[-1]
            # retrieve data from server
            ethnic_get = requests.get("https://lldev.thespacedevs.com/2.2.0/astronaut/?search={0}".format(astronaut_last_name)).json()
            # only count successful matches
            if ethnic_get["count"]>0:
                ethnic = ethnic_get["results"][0]
                ethnicities.append(ethnic["nationality"])
        # turn array into object
        ethnic_object = {i: ethnicities.count(i) for i in ethnicities}
        # pair ethnicities with values
        labels = ethnic_object.keys()
        sizes = ethnic_object.values()
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=None, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        # draw pie chart
        app.pyplot(fig1)

def past_launch_count():
    app.markdown("#### **Timeline of SpaceX Launches**")
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
    # custom CSS to make the outside div a little smaller
    styl = "<style> div[data-testid='stArrowVegaLiteChart'] {width:1000px}</style>"
    app.markdown(styl, unsafe_allow_html=True)

def now_later_list():
    # structure output
    past_and_future = {'now':[], 'later':[]}
    # date format to YYYY-MM-DD
    date_format = "%Y-%m-%d"
    date_today = date.today()
    # create date lists
    for index in spacex_all_launches:
        date_temp = index["date_utc"]
        spacex_launch_date_list.append(date_temp[0:10])
        # format temp variant to date format
        datetime_temp = datetime.strptime(date_temp[0:10],date_format)
        datetime_temp = datetime_temp.date()
        # split future launches from past launches
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
    # initialize list of dates
    templist = now_later_list()
    with col1: # select past/present/future
        # ask user how they want to categorize search
        past_future = app.radio("Present or Future launches?",options=('Present','Future','All Launches'))
        # custom CSS to have the radio buttons in a line
        app.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        # segregate dates between future and existing dates
        if past_future == 'Present':
            templist = templist['now']
        elif past_future == 'Future':
            templist = templist['later']
        else:
            templist = []
            for index in spacex_launch_date_list:
                templist.append(index)
            # scrub duplicates dates
    with col2: # drop-down menu with search
        # scrub duplicates dates
        duplicate_catch = []
        for non_duplicate in templist:
            if non_duplicate not in duplicate_catch:
                duplicate_catch.append(non_duplicate)
        # re-set temporary list as new non-duplicate version
        templist = duplicate_catch
        templist.insert(0, "Search or select a launch date (YYYY-MM-DD)...")
        date_select = app.selectbox("Returning this element to its first item ('Search or select...') will return the entire site to its default page", templist)
    # return the date if true
    if date_select:
        # app.write(date_select)
        return date_select
    elif date_select not in templist: # doesn't exist, try again
        app.warning("This is not a date, please try again")

def spacex_payload_data(payload_id):
    payload_data = {}
    # request data from sever
    payload = requests.get("https://api.spacexdata.com/v4/payloads/{0}".format(payload_id)).json()
    # re-route response limit to what we might want
    if payload["name"]:
        payload_data["name"] = payload["name"]
    if payload["type"]:
        payload_data["type"] = payload["type"]
    if payload["mass_kg"] != 'null':
        payload_data["mass"] = payload["mass_kg"]
    # return object
    return payload_data

def spacex_crew_data(crew_ids):
    astronauts = []
    for crew in crew_ids:
        astronaut = {}
        # request crew data from server
        space_man = requests.get("https://api.spacexdata.com/v4/crew/{0}".format(crew)).json()
        # reconfigure only for data we care about
        astronaut["name"] = space_man["name"]
        astronaut["agency"] = space_man["agency"]
        astronaut["portrait"] = space_man["image"]
        astronaut["link"] = space_man["wikipedia"]
        # push to array
        astronauts.append(astronaut)
    # return array of astronaut data
    return astronauts

def spacex_launch_overview (date):
    launch_data = {} # returning an object
    for i in spacex_all_launches:
        # set up temporary variables
        astronauts = []
        temp_date = i["date_utc"]
        temp_date = temp_date[0:10]
        if temp_date == date:
            # checks for crew
            if i["crew"]:
                for crew in i["crew"]:
                    astronauts.append(crew["crew"])
            # checks for images of the launch
            if len(i["links"]["flickr"]["original"]) > 0:
                launch_data["images"] = i["links"]["flickr"]["original"]
            else:
                # no image available if no images
                launch_data["images"] = []
                launch_data["images"].append(image_not_available)
            # checks for mission uniform patch
            if i["links"]["patch"]["large"]:
                launch_data["patch"] = i["links"]["patch"]["large"]
            else:
                # no image available if no image
                launch_data["patch"] = image_not_available
            # set mission name
            launch_data["mission_name"] = i["name"]
            # set mission flight number
            launch_data["flight"] = i["flight_number"]
            # set flight details
            launch_data["details"] = i["details"]
            # payload ids, will need to individually parse
            launch_data["payload_id"] = i["payloads"]
            # flight article if there is one, otherwise null
            launch_data["link"] = i["links"]["article"]
            # flight youtube video if available
            if i["links"]["youtube_id"]:
                launch_data["video"] = i["links"]["youtube_id"]
            else:
                # video will be null if it doesn't exist
                launch_data["video"] = None
            # set crew ids, will need to individually parse
            if i["crew"]:
                launch_data["crew"] = astronauts
            else:
                launch_data["crew"] = "n/a"
    # return re-interpreted object
    return launch_data

def space_coast_weather(): # didn't end up being used
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

# writes onto page as links to wikipedia
def crew_display(crew_array):
    for astronaut in crew_array:
        app.write("[{0}]({1}) ({2})".format(astronaut["name"],astronaut["link"],astronaut["agency"]))

def payload_display(payload_array):
    for payload in payload_array:
        # fetch payload data
        payload_data = spacex_payload_data(payload)
        # write onto page if true
        # will send warning if not available
        if payload_data["name"]:
            app.write("Payload: ", payload_data["name"])
        else:
            app.warning("Payload name no available")
        if payload_data["type"]:
            app.write("Type: ", payload_data["type"])
        else:
            app.warning("Payload type data no available")
        if payload_data["mass"]:
            app.write("Weight: ", payload_data["mass"], "kg")
        else:
            app.warning("Mass data not Available")

#header_column1,header_column2 = app.columns([7,1])
#with header_column1:
#with header_column2:
#    if 'happy' not in app.session_state:
#        app.session_state.happy = False
#    app.session_state.happy = app.checkbox("Reset")

# would go into header_column1 otherwise but pseudo-state resets is currently non-functional
app.title("SPACE!")

date_select = spacex_date_select()
# declare all potential elements to be empty
launch_slider = app.empty()
launch_name = app.empty()
flight_number = app.empty()
flight_details = app.empty()
detail_warning = app.empty()
payload_title = app.empty()
display_payload = app.empty()
payload_warning = app.empty()
crew_title = app.empty()
display_crew = app.empty()
flight_crew_warning = app.empty()
# empty home page elements
fact_of_the_day = app.empty()
past_launch_graph = app.empty()
iss_location = app.empty()

# pseudo-state-like response is centered around selectbox
if date_select != "Search or select a launch date (YYYY-MM-DD)...":
    # retrieve data
    launch_date = spacex_launch_overview(date_select)
    # split information into columns to be more easily digestible
    col1,col2,col3= app.columns([2,2,1])
    # mission pictures
    with col1:
        images = []
        if launch_date["patch"]:
            images.append(launch_date["patch"])
        # attach images
        if launch_date["images"]:
            for image in launch_date["images"]:
                images.append(image)
        # attach youtube video
        if launch_date["video"]:
            images.append("https://www.youtube.com/watch?v={0}".format(launch_date["video"]))
        # create carousel
        launch_slider = slider_carousel("Images: {0}".format(len(images)),images,585)
    with col2:
        # title and flight number
        launch_name = app.markdown("#### **{0}**".format(launch_date["mission_name"]))
        flight_number = app.write("Flight Number: ",launch_date["flight"])
        # write details
        if launch_date["details"]:
            flight_details = app.write(launch_date["details"])
        else:
            detail_warning = app.warning("No summary available")
        # writes link to article about this launch
        if launch_date["link"]:
            flight_article = app.write("[Article]({0})".format(launch_date["link"]))
        else:
            article_warning = app.warning("No article link available")
        # write payload info
        if launch_date["payload_id"]:
            payload_title = app.markdown("##### **Payload Details**")
            display_payload = payload_display(launch_date["payload_id"])
        else:
            payload_warning = app.warning("No payload details")
    with col3:
        if launch_date["crew"] != "n/a":
            crew_title = app.markdown("#### **Mission Crew**")
            launch_crew = spacex_crew_data(launch_date["crew"])
            # display crew names as links
            display_crew = crew_display(launch_crew)
            # assemble crew photos
            launch_crew_portrait = []
            for portrait in launch_crew:
                launch_crew_portrait.append(portrait["portrait"])
            # display crew photos as carousel
            crew_carousel = slider_carousel("Crew",launch_crew_portrait,285)
        else:
            flight_crew_warning = app.warning("This mission was not crewed")
# returning first value (only non-date value) will return user to main page
elif date_select == "Search or select a launch date (YYYY-MM-DD)...":
    # returns to main page
    fact_of_the_day = nasa_fotd(nasa_key)
    past_launch_graph = past_launch_count()
    iss_location = international_space_station()
elif app.session_state.happy is True: # currently non-working
    fact_of_the_day = nasa_fotd(nasa_key)
    past_launch_graph = past_launch_count()
    iss_location = international_space_station()
    app.session_state.happy = False

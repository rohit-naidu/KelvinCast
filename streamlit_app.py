import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Load the CSV file for lat/lng data
csv_file_path = '/Users/raghavansrinivas/PycharmProjects/pythonProject/.venv/uszips.csv'  #REPLACE WITH YOUR OWN PATH!!!!!!!!!!!!!!
df = pd.read_csv(csv_file_path)

# Custom weather icons dictionary mapping forecast descriptions to icon URLs
WEATHER_ICON_MAP = {
    "Sunny": "https://www.awxcdn.com/adc-assets/images/weathericons/1.svg",
    "Partly Cloudy": "https://www.awxcdn.com/adc-assets/images/weathericons/3.svg",
    "Mostly Cloudy": "https://www.awxcdn.com/adc-assets/images/weathericons/4.svg",
    "Clear": "https://www.awxcdn.com/adc-assets/images/weathericons/2.svg",
    "Rain": "https://www.awxcdn.com/adc-assets/images/weathericons/12.svg",
    "Thunderstorm": "https://www.awxcdn.com/adc-assets/images/weathericons/15.svg",
    "Snow": "https://www.awxcdn.com/adc-assets/images/weathericons/22.svg",
    "Fog": "https://www.awxcdn.com/adc-assets/images/weathericons/11.svg",
    "Chance Drizzle": "https://www.awxcdn.com/adc-assets/images/weathericons/18.svg"
}

# Function to get latitude and longitude by city and state
def get_lat_lng_by_city(city, state_id):
    city, state_id = city.strip().title(), state_id.strip().upper()
    city_data = df[(df["city"] == city) & (df["state_id"] == state_id)].tail(1)

    if not city_data.empty:
        lat, lng = city_data['lat'].values[0], city_data['lng'].values[0]
        return lat, lng
    return None

# Function to get latitude and longitude by zip code
def get_lat_lng_by_zip(zipcode):
    zipcode = str(zipcode).strip()
    zip_data = df[df["zip"] == int(zipcode)].tail(1)

    if not zip_data.empty:
        lat, lng = zip_data['lat'].values[0], zip_data['lng'].values[0]
        return lat, lng
    return None

# Function to get the current weather using latitude and longitude
def get_current_weather_by_lat_lng(lat, lng):
    url = f"https://api.weather.gov/points/{lat},{lng}"
    response = requests.get(url)

    if response.status_code == 200:
        grid_data = response.json()
        forecast_url = grid_data['properties']['forecastHourly']
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']
            if periods:
                current_period = periods[0]
                return current_period['temperature'], current_period['shortForecast'], current_period['icon']
    return None, None, None

# Function to get the 7-day weather forecast
def get_7_day_forecast_by_lat_lng(lat, lng):
    url = f"https://api.weather.gov/points/{lat},{lng}"
    response = requests.get(url)

    if response.status_code == 200:
        grid_data = response.json()
        forecast_url = grid_data['properties']['forecast']
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']
            return periods
    return None

# Function to get the appropriate weather icon based on forecast description
def get_weather_icon(forecast):
    for condition, icon_url in WEATHER_ICON_MAP.items():
        if condition.lower() in forecast.lower():
            return f'<img src="{icon_url}" width="50">'
    return '<img src="https://example.com/icons/default.png" width="50">'

# Function to display weather forecast in a styled format
def display_7_day_forecast(forecast_data):
    st.markdown("### 7-Day Weather Forecast")
    for i in range(0, len(forecast_data), 2):  # Every 2 periods represent day and night
        day_data = forecast_data[i]
        night_data = forecast_data[i + 1]

        day_name = day_data['name'].split(' ')[0]
        start_time = day_data['startTime']
        date_obj = datetime.fromisoformat(start_time[:-6])
        formatted_date = date_obj.strftime('%A, %B %d, %Y')

        temp_high = day_data['temperature']
        temp_low = night_data['temperature']
        short_forecast = day_data['shortForecast']
        night_forecast = night_data['shortForecast']

        weather_icon = get_weather_icon(short_forecast)

        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #ddd; padding: 10px 0;">
            <div style="flex: 1;"><br>{formatted_date}</div>
            <div style="flex: 1; text-align: center;">{weather_icon}</div>
            <div style="flex: 2; text-align: center;">{temp_high}° / {temp_low}°</div>
            <div style="flex: 4;"><strong>{short_forecast}</strong><br>Night: {night_forecast}</div>
        </div>
        """, unsafe_allow_html=True)

# Function to display the main page
def main_page():
    st.title('Current Temperature and 7-Day Forecast')

    location_input = st.text_input("Enter a location (City, State or Zip Code):", "")

    if location_input:
        if location_input.isdigit():
            lat_lng = get_lat_lng_by_zip(location_input)
            if lat_lng:
                lat, lng = lat_lng
                st.write(f"Coordinates for Zip Code {location_input}: Latitude: {lat}, Longitude: {lng}")
            else:
                st.write(f"No data found for Zip Code {location_input}")
        else:
            try:
                city, state = location_input.split(',')
                lat_lng = get_lat_lng_by_city(city, state)
                if lat_lng:
                    lat, lng = lat_lng
                    st.write(f"Coordinates for {city.strip()}, {state.strip()}: Latitude: {lat}, Longitude: {lng}")
                else:
                    st.write(f"No data found for {city.strip()}, {state.strip()}")
            except ValueError:
                st.write("Please enter the location in 'City, State' format or as a valid Zip Code.")

        if lat_lng:
            current_temp, current_forecast, current_icon = get_current_weather_by_lat_lng(lat, lng)
            if current_temp is not None:
                st.markdown("### Current Weather")
                col1, col2 = st.columns([1, 3])
                with col1:
                    weather_icon = get_weather_icon(current_forecast)
                    st.markdown(weather_icon, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{current_temp}°F - {current_forecast}**")
            else:
                st.write("Could not fetch current weather.")

            forecast_data = get_7_day_forecast_by_lat_lng(lat, lng)
            if forecast_data:
                display_7_day_forecast(forecast_data)
            else:
                st.write("Could not fetch 7-day forecast.")

# Function for the Kelvin page
def kelvin_page():
    st.title("About Kelvin")

    # Section 1: What is Kelvin? / History of Kelvin
    st.markdown("<h2 style='color:green;'>What is Kelvin?</h2>", unsafe_allow_html=True)
    st.markdown("""
    The **Kelvin scale** is the base unit of temperature in the International System of Units (SI). 
    It is named after **William Thomson**, also known as **<span style='background-color:lightgray; color:red;'>Lord Kelvin</span>**, a British physicist and engineer who first proposed this absolute temperature scale in 1848. 
    The Kelvin scale starts at **<span style='background-color:lightgray; color:red;'>absolute zero</span>**, which is the point where all molecular motion stops, at **<span style='background-color:lightgray; color:red;'>0 K</span>**, equivalent to **<span style='background-color:lightgray; color:red;'>-273.15°C or -459.67°F</span>**.
    The Kelvin scale is particularly useful in scientific contexts because it directly relates to the amount of thermal energy present in a system, making it essential in disciplines like physics, chemistry, and engineering.
    """, unsafe_allow_html=True)

    # Section 2: Why Kelvin is Important
    st.markdown("<h2 style='color:green;'>Why is Kelvin Important?</h2>", unsafe_allow_html=True)
    st.markdown("""
    **<span style='background-color:lightgray; color:red;'>Kelvin</span>** is crucial because it provides an **<span style='background-color:lightgray; color:red;'>absolute measurement of temperature</span>** that is not relative to environmental factors, unlike Celsius and Fahrenheit.
    Here are some reasons why Kelvin is important:

    - **<span style='background-color:lightgray; color:red;'>Scientific Research</span>**: In fields like astrophysics, thermodynamics, and quantum mechanics, the Kelvin scale is the standard because it directly relates to the energy of particles.
    - **<span style='background-color:lightgray; color:red;'>Climate and Weather</span>**: In meteorological models, Kelvin is often used in measuring extreme temperatures and calculating thermal energy.
    - **<span style='background-color:lightgray; color:red;'>Manufacturing and Technology</span>**: Many industries that involve materials science or physics (e.g., semiconductor manufacturing) depend on precise temperature measurements in Kelvin for consistency and accuracy.
    """, unsafe_allow_html=True)

    # Section 3: Biggest Failures Due to Not Using Kelvin
    st.markdown("<h2 style='color:green;'>Fun Facts About Kelvin</h2>", unsafe_allow_html=True)
    st.markdown("""
    One of the most notable failures due to improper use of temperature units was the **<span style='background-color:lightgray; color:red;'>NASA Mars Climate Orbiter Mission</span>**.
    In 1999, the orbiter was lost because of a mix-up between metric and imperial units, leading to incorrect calculations for the spacecraft's trajectory.
    While the failure wasn't directly due to Kelvin, it emphasizes the importance of standardized units, including Kelvin, in scientific and engineering endeavors.

    Kelvin is widely used in various high-stakes projects, from satellite launches to climate modeling. Failing to use or convert between units correctly can have costly consequences, as the Mars Climate Orbiter incident demonstrated.
    """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "About Kelvin"])

# Logic for switching between pages
if page == "Home":
    main_page()
elif page == "About Kelvin":
    kelvin_page()

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from PIL import Image

# Load the CSV file for lat/lng data
csv_file_path = 'uszips.csv'  # Replace this with the correct path to your CSV file
df = pd.read_csv(csv_file_path)
WIND_ARROW_MAP = {
    "N": "↑",
    "NNE": "↑",
    "NE": "↗",
    "ENE": "↗",
    "E": "→",
    "ESE": "→",
    "SE": "↘",
    "SSE": "↘",
    "S": "↓",
    "SSW": "↓",
    "SW": "↙",
    "WSW": "↙",
    "W": "←",
    "WNW": "↖",
    "NW": "↖",
    "NNW": "↑"
}

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

# Function to convert Fahrenheit to Kelvin (without adding a new variable)
def convert_to_kelvin(temp_f):
    return (temp_f - 32) * 5.0 / 9.0 + 273.15

# Function to get city, state, latitude, and longitude by zip code
def get_city_state_lat_lng_by_zip(zipcode):
    zipcode = str(zipcode).strip()
    zip_data = df[df["zip"] == int(zipcode)].tail(1)

    if not zip_data.empty:
        city = zip_data['city'].values[0]
        state = zip_data['state_id'].values[0]
        lat = zip_data['lat'].values[0]
        lng = zip_data['lng'].values[0]
        return city, state, lat, lng
    return None

# Function to get latitude and longitude by city and state
def get_lat_lng_by_city(city, state_id):
    city, state_id = city.strip().title(), state_id.strip().upper()
    city_data = df[(df["city"] == city) & (df["state_id"] == state_id)].tail(1)

    if not city_data.empty:
        lat, lng = city_data['lat'].values[0], city_data['lng'].values[0]
        return lat, lng
    return None

# Function to get the current weather using latitude and longitude
def get_weather_by_lat_lng(lat, lng):
    url = f"https://api.weather.gov/points/{lat},{lng}"
    response = requests.get(url)

    if response.status_code == 200:
        grid_data = response.json()
        grid_x = grid_data['properties']['gridX']
        grid_y = grid_data['properties']['gridY']
        grid_id = grid_data['properties']['gridId']

        forecast_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly"
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']

            if periods:
                current_weather = periods[0]  # Get the latest weather data
                temperature = convert_to_kelvin(current_weather['temperature'])  # Convert to Kelvin
                wind_speed = current_weather['windSpeed']  # Wind speed
                wind_direction = current_weather.get('windDirection', "N/A")  # Wind direction
                humidity = current_weather.get('relativeHumidity', "N/A")  # Relative humidity
                precipitation_chance = current_weather.get('probabilityOfPrecipitation', "N/A")  # Precipitation probability

                return temperature, wind_speed, wind_direction, humidity, precipitation_chance
    return None, None, None, None, None

# Function to get the current time and date
def get_current_time_and_date():
    now = datetime.now()
    formatted_date = now.strftime("%a, %b %d")  # Format like "Mon, Sep 9"
    return formatted_date

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

def get_weather_icon(forecast):
    for condition, icon_url in WEATHER_ICON_MAP.items():
        if condition.lower() in forecast.lower():
            return f'<img src="{icon_url}" width="50">'
    return '<img src="https://example.com/icons/default.png" width="50">'


# Function to display weather forecast in a styled format
# Updated function to display weather forecast with icons
def display_7_day_forecast(forecast_data):
    st.markdown("### 7-Day Weather Forecast")

    for i in range(0, len(forecast_data), 2):  # Every 2 periods represent day and night
        day_data = forecast_data[i]
        night_data = forecast_data[i + 1]

        day_name = day_data['name'].split(' ')[0]
        start_time = day_data['startTime']
        date_obj = datetime.fromisoformat(start_time[:-6])
        formatted_date = date_obj.strftime('%A, %B %d, %Y')

        temp_high = convert_to_kelvin(day_data['temperature'])  # Convert to Kelvin
        temp_low = convert_to_kelvin(night_data['temperature'])  # Convert to Kelvin
        short_forecast = day_data['shortForecast']
        night_forecast = night_data['shortForecast']

        # Get the weather icon based on the forecast
        day_icon = get_weather_icon(short_forecast)
        night_icon = get_weather_icon(night_forecast)

        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #ddd; padding: 10px 0;">
            <div style="flex: 1;"><br>{formatted_date}</div>
            <div style="flex: 2; text-align: center;">{temp_high:.2f} K / {temp_low:.2f} K</div>
            <div style="flex: 4;"><strong>{short_forecast}</strong>   {day_icon}<br>Night: {night_forecast}    {night_icon}</div>
        </div>
        """, unsafe_allow_html=True)

# Main page function (Home)
def main_page():
    st.image(Image.open("/Users/Anay/Weather App/rsz_2.png"))

    # Input for the location with a default example "Berkeley, CA"
    location_input = st.text_input("Enter a location (City, State or Zip Code):", "Berkeley, CA")

    if location_input:
        # Initialize variables to avoid UnboundLocalError
        temperature, wind_speed, wind_direction, humidity, precipitation_chance = None, None, None, None, None

        # Create columns to display the information
        col1, col2, col3 = st.columns(3)

        with col1:
            # Check if the input is a Zip Code (all digits)
            if location_input.isdigit():
                city_state_lat_lng = get_city_state_lat_lng_by_zip(location_input)
                if city_state_lat_lng:
                    city, state, lat, lng = city_state_lat_lng
                    st.header(f"{city}, {state}")
                    st.info(f"Latitude: {lat}, Longitude: {lng}")
                else:
                    st.error(f"No data found for Zip Code {location_input}")
            else:
                # Handle city, state input and catch any errors
                try:
                    city, state = location_input.split(',')
                    lat_lng = get_lat_lng_by_city(city, state)
                    if lat_lng:
                        lat, lng = lat_lng
                        st.header(f"{city.strip()}, {state.strip()}")
                        st.info(f"Latitude: {lat}, Longitude: {lng}")
                    else:
                        st.error(f"No data found for {city.strip()}, {state.strip()}")
                except ValueError:
                    st.error("Please enter the location in the 'City, State' format or as a valid Zip Code.")

        with col2:
            # Get the current weather data
            if 'lat' in locals() and 'lng' in locals():
                temperature, wind_speed, wind_direction, humidity, precipitation_chance = get_weather_by_lat_lng(lat, lng)
                current_date = get_current_time_and_date()

                if temperature is not None:
                    # Display the temperature and wind speed in Kelvin
                    st.metric(label=current_date, value=f"{temperature:.2f} K", delta=f"Wind: {wind_speed}")
                else:
                    st.error("Could not fetch current weather information.")

        with col3:
            # Display wind direction, humidity, and precipitation in the third column
            if temperature is not None:
                st.write(f"**Wind Direction**: {WIND_ARROW_MAP.get(wind_direction, 'N/A')} {wind_direction}")
                st.write(f"**Relative Humidity**: {humidity['value']}%")
                st.write(f"**Chance of Precipitation**: {precipitation_chance['value']}%")

        # Display the 7-day forecast
        if temperature is not None:
            forecast_data = get_7_day_forecast_by_lat_lng(lat, lng)
            if forecast_data:
                display_7_day_forecast(forecast_data)
            else:
                st.error("Could not fetch 7-day forecast.")


# Kelvin Page (About Kelvin)
def kelvin_page():
    st.title("About Kelvin")

    # Section 1: What is Kelvin? / History of Kelvin
    st.markdown("<h2 style='color:#4CAF50;'>What is Kelvin?</h2>", unsafe_allow_html=True)
    st.markdown("""
    The **Kelvin scale** is the base unit of temperature in the International System of Units (SI). 
    It is named after **William Thomson**, also known as **<span style='background-color:#e0f7fa; color:#0d47a1;'>Lord Kelvin</span>**, a British physicist and engineer who first proposed this absolute temperature scale in 1848. 
    The Kelvin scale starts at **<span style='background-color:#e0f7fa; color:#0d47a1;'>absolute zero</span>**, which is the point where all molecular motion stops, at **<span style='background-color:#e0f7fa; color:#0d47a1;'>0 K</span>**, equivalent to **<span style='background-color:#e0f7fa; color:#0d47a1;'>-273.15°C or -459.67°F</span>**.
    The Kelvin scale is particularly useful in scientific contexts because it directly relates to the amount of thermal energy present in a system, making it essential in disciplines like physics, chemistry, and engineering.
    """, unsafe_allow_html=True)

    # Section 2: Why Kelvin is Important
    st.markdown("<h2 style='color:#4CAF50;'>Why is Kelvin Important?</h2>", unsafe_allow_html=True)
    st.markdown("""
    **<span style='background-color:#e0f7fa; color:#0d47a1;'>Kelvin</span>** is crucial because it provides an **<span style='background-color:#e0f7fa; color:#0d47a1;'>absolute measurement of temperature</span>** that is not relative to environmental factors, unlike Celsius and Fahrenheit.
    Here are some reasons why Kelvin is important:

    - **<span style='background-color:#e0f7fa; color:#0d47a1;'>Scientific Research</span>**: In fields like astrophysics, thermodynamics, and quantum mechanics, the Kelvin scale is the standard because it directly relates to the energy of particles.
    - **<span style='background-color:#e0f7fa; color:#0d47a1;'>Climate and Weather</span>**: In meteorological models, Kelvin is often used in measuring extreme temperatures and calculating thermal energy.
    - **<span style='background-color:#e0f7fa; color:#0d47a1;'>Manufacturing and Technology</span>**: Many industries that involve materials science or physics (e.g., semiconductor manufacturing) depend on precise temperature measurements in Kelvin for consistency and accuracy.
    """, unsafe_allow_html=True)

    # Section 3: Fun Facts About Kelvin
    st.markdown("<h2 style='color:#4CAF50;'>Fun Facts About Kelvin</h2>", unsafe_allow_html=True)
    st.markdown("""
    One of the most notable failures due to improper use of temperature units was the **NASA Mars Climate Orbiter Mission**.
    In 1999, the orbiter was lost because of a mix-up between metric and imperial units, leading to incorrect calculations for the spacecraft's trajectory.
    While the failure wasn't directly due to Kelvin, it emphasizes the importance of standardized units, including Kelvin, in scientific and engineering endeavors.
    """)


# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "About Kelvin"])

# Logic for switching between pages
if page == "Home":
    main_page()
elif page == "About Kelvin":
    kelvin_page()

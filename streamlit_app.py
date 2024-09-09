import streamlit as st
import requests

# Function to convert Fahrenheit to Kelvin
def fahrenheit_to_kelvin(temp_f):
    return (temp_f - 32) * 5/9 + 273.15

# Function to convert mph to m/s
def mph_to_mps(speed_mph):
    return speed_mph * 0.44704

# Function to get latitude and longitude from ZIP code using OpenCage API
def get_lat_lon_from_zip(zip_code):
    api_key = "5825e22ca6214c94a3c61e26b9b999f7"  # Your actual OpenCage API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={zip_code}&countrycode=us&key={api_key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['geometry']['lat']
            lon = data['results'][0]['geometry']['lng']
            return lat, lon
    return None, None

# Function to get weather data from NWS API using latitude and longitude
def get_weather_data(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(url)
    
    if response.status_code == 200:
        grid_url = response.json()['properties']['forecast']
        forecast_response = requests.get(grid_url)
        if forecast_response.status_code == 200:
            return forecast_response.json()
    return None

# Streamlit app with sidebar navigation
st.title("Climate Change Class Weather Page")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Latitude/Longitude", "Current Temperature", "Wind Speed", "5-Day Forecast"])  # Define 'page' here

zip_code = st.text_input("Enter a ZIP Code:", "94720")  # Default to UC Berkeley ZIP code

if zip_code:
    lat, lon = get_lat_lon_from_zip(zip_code)
    
    if lat and lon:
        weather_data = get_weather_data(lat, lon)

        # Show latitude and longitude
        if page == "Latitude/Longitude":
            st.write(f"### Latitude and Longitude")
            st.write(f"Latitude: {lat}, Longitude: {lon}")
        
        # Show current temperature
        elif page == "Current Temperature":
            if weather_data:
                current_weather = weather_data['properties']['periods'][0]
                high_temp = current_weather['temperature']
                high_temp_kelvin = fahrenheit_to_kelvin(high_temp)
                st.write(f"### Current Temperature")
                st.write(f"Current Temperature: {high_temp_kelvin:.2f} K")
            else:
                st.write("Could not fetch weather data. Please try again later.")
        
        # Show wind speed
        elif page == "Wind Speed":
            if weather_data:
                current_weather = weather_data['properties']['periods'][0]
                wind_speed = current_weather['windSpeed']
                wind_speed_mps = mph_to_mps(float(wind_speed.split()[0]))
                st.write(f"### Wind Speed")
                st.write(f"Wind Speed: {wind_speed_mps:.2f} m/s")
            else:
                st.write("Could not fetch weather data. Please try again later.")
        
        # Show 5-day forecast
        elif page == "5-Day Forecast":
            if weather_data:
                st.write("### 5-Day Forecast")
                for period in weather_data['properties']['periods'][0:5]:
                    period_name = period['name']
                    temp_kelvin = fahrenheit_to_kelvin(period['temperature'])
                    st.write(f"{period_name}: {temp_kelvin:.2f} K, {period['detailedForecast']}")
            else:
                st.write("Could not fetch weather data. Please try again later.")
    else:
        st.write("Could not fetch latitude and longitude for the given ZIP code.")

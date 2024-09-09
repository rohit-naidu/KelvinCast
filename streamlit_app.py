import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Load the CSV file for lat/lng data
csv_file_path = 'uszips.csv'  # Replace this with the correct path to your CSV file
df = pd.read_csv(csv_file_path)

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

# Function to get the current temperature using latitude and longitude
def get_current_temperature_by_lat_lng(lat, lng):
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
                current_temperature = periods[0]['temperature']  # Get the temperature from the latest forecast period
                return current_temperature
    return None

# Function to get the current date and time
def get_current_time_and_date():
    now = datetime.now()
    formatted_date = now.strftime("%a, %b %d")  # Format like "Mon, Sep 9"
    return formatted_date

# Streamlit app
st.title('Current Temperature and Date Widget')

# Input for the location
location_input = st.text_input("Enter a location (City, State or Zip Code):", "")

if location_input:
    # Check if the input is a Zip Code (all digits)
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

    # Get the current temperature and date
    if lat_lng:
        current_temperature = get_current_temperature_by_lat_lng(lat, lng)
        current_date = get_current_time_and_date()

        if current_temperature is not None:
            # Display the metric with the current temperature and date
            st.metric(label=current_date, value=f"{current_temperature} °F")
        else:
            st.write("Could not fetch current temperature.")

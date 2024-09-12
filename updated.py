# Function to display weather forecast in a table format
def display_7_day_forecast(forecast_data):
    st.markdown("### 7-Day Weather Forecast")
    
    # Create a table header
    table = """
    <table style="width:100%; border-collapse: collapse;">
        <thead>
            <tr>
                <th style="border: 1px solid #ddd; padding: 8px;">Date</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Weather Icon</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Temperature (Day/Night)</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Forecast (Day/Night)</th>
            </tr>
        </thead>
        <tbody>
    """

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

        weather_icon = get_weather_icon(short_forecast)

        # Add each row of the table
        table += f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{formatted_date}</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{weather_icon}</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{temp_high:.2f} K / {temp_low:.2f} K</td>
            <td style="border: 1px solid #ddd; padding: 8px;">Day: {short_forecast}<br>Night: {night_forecast}</td>
        </tr>
        """

    # Close the table
    table += "</tbody></table>"

    # Render the table
    st.markdown(table, unsafe_allow_html=True)

# Main page function (Home)
def main_page():
    st.image(Image.open("/Users/rohitnaidu/PycharmProjects/weather/rsz_2.png"))

    # Input for the location with a default example "Berkeley, CA"
    location_input = st.text_input("Enter a location (City, State or Zip Code):", "Berkeley, CA")

    if location_input:
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
                # Treat as City, State
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
                    st.error("Please enter the location in 'City, State' format or as a valid Zip Code.")

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
                st.write(f"**Wind Direction**: {WIND_ARROW_MAP[wind_direction]}{wind_direction}")
                st.write(f"**Relative Humidity**: {humidity['value']}%")
                st.write(f"**Chance of Precipitation**: {precipitation_chance['value']}%")

        # Display the 7-day forecast
        forecast_data = get_7_day_forecast_by_lat_lng(lat, lng)
        if forecast_data:
            display_7_day_forecast(forecast_data)
        else:
            st.error("Could not fetch 7-day forecast.")

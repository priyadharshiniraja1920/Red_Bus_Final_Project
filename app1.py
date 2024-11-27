import streamlit as st
import mysql.connector
import pandas as pd

# Function to fetch unique values for dropdowns
def fetch_unique_values(column_name):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",  # Replace with your MySQL password
            database="red_bus_details"
        )
        cursor = conn.cursor()
        query = f"SELECT DISTINCT {column_name} FROM bus_details"
        cursor.execute(query)
        result = [row[0] for row in cursor.fetchall()]
        conn.close()
        return result
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to fetch filtered bus details based on selected dropdown values
def fetch_filtered_buses(route_name, bus_name, bus_type, start_time, total_duration, price, ratings):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",  
            database="red_bus_details"
        )
        cursor = conn.cursor()

        # Construct SQL query with filters
        query = """
        SELECT Bus_name, Bus_type, Start_time, End_time, Total_duration,
               Price, Seats_Available, Ratings, Route_link, Route_name
        FROM bus_details WHERE 1=1
        """
        params = []

        if route_name:
            query += " AND Route_name = %s"
            params.append(route_name)
        if bus_name:
            query += " AND Bus_name = %s"
            params.append(bus_name)
        if bus_type:
            query += " AND Bus_type = %s"
            params.append(bus_type)
        if start_time:
            query += " AND Start_time = %s"
            params.append(start_time)
        if total_duration:
            query += " AND Total_duration = %s"
            params.append(total_duration)
        if price:
            query += " AND Price <= %s"
            params.append(price)
        if ratings:
            query += " AND Ratings >= %s"
            params.append(ratings)

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        # Define column names for the bus details table
        columns = [
            "Bus_name", "Bus_type", "Start_time", "End_time", "Total_duration",
            "Price", "Seats_Available", "Ratings", "Route_link", "Route_name"
        ]
        df = pd.DataFrame(result, columns=columns) if result else pd.DataFrame()

        conn.close()
        return df
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# Streamlit Page Configuration
st.set_page_config(layout="wide", page_title="Bus Filtering System")

# Title
st.title("🚌 Bus Filtering System")

# Fetch dropdown values
routes = fetch_unique_values("Route_name")
bus_names = fetch_unique_values("Bus_name")
bus_types = fetch_unique_values("Bus_type")
start_times = fetch_unique_values("Start_time")
durations = fetch_unique_values("Total_duration")
prices = fetch_unique_values("Price")
ratings = fetch_unique_values("Ratings")

# Dropdowns for Filters
selected_route = st.selectbox("Select Route", [""] + routes, index=0)
selected_bus_name = st.selectbox("Select Bus Name", [""] + bus_names, index=0)
selected_bus_type = st.selectbox("Select Bus Type", [""] + bus_types, index=0)
selected_start_time = st.selectbox("Select Start Time", [""] + start_times, index=0)
selected_duration = st.selectbox("Select Total Duration", [""] + durations, index=0)

# Price dropdown with available prices in the database
selected_price = st.selectbox("Select Maximum Price", [0] + sorted(prices), index=0)

# Ratings dropdown with available ratings in the database
selected_ratings = st.selectbox("Select Minimum Ratings", [0] + sorted(ratings), index=0)

# Button to fetch filtered data
st.header("Filtered Bus Details")
if st.button("Search"):
    filtered_buses = fetch_filtered_buses(
        selected_route,
        selected_bus_name,
        selected_bus_type,
        selected_start_time,
        selected_duration,
        selected_price,
        selected_ratings
    )
    if filtered_buses.empty:
        st.warning("No results found for the selected filters.")
    else:
        st.dataframe(filtered_buses)

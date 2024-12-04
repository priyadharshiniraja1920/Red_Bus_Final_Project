import streamlit as st
import mysql.connector
import pandas as pd

# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="red_bus_details"
)
cursor = conn.cursor()

# Fetch distinct states from the database
cursor.execute("SELECT DISTINCT State FROM bus_details")
states = [state[0] for state in cursor.fetchall()]

# Fetch route names based on the selected state
def get_routes_for_state(state):
    cursor.execute("SELECT DISTINCT Route_name FROM bus_details WHERE State = %s", (state,))
    routes = [route[0] for route in cursor.fetchall()]
    return routes

# Fetch distinct AC Status options from the database
cursor.execute("""
    SELECT DISTINCT 
        CASE 
            WHEN LOWER(Bus_type) LIKE '%ac%' THEN 'AC' 
            WHEN LOWER(Bus_type) LIKE '%non ac%' THEN 'NON AC' 
        END AS AC_Status 
    FROM bus_details 
    WHERE Bus_type IS NOT NULL
""")
ac_status_options = [status[0] for status in cursor.fetchall() if status[0]]

# Fetch distinct Seat Types from the database
cursor.execute("""
    SELECT DISTINCT 
        CASE 
            WHEN LOWER(Bus_type) LIKE '%seater%' THEN 'Seater' 
            WHEN LOWER(Bus_type) LIKE '%sleeper%' THEN 'Sleeper' 
        END AS Seat_Type 
    FROM bus_details 
    WHERE Bus_type IS NOT NULL
""")
seat_type_options = [seat_type[0] for seat_type in cursor.fetchall() if seat_type[0]]

# Fetch buses based on filters
def get_filtered_buses(state, route_name, ac_status, seat_type, price_range, min_rating):
    query = "SELECT * FROM bus_details WHERE 1=1"
    params = []
    
    if state:
        query += " AND State = %s"
        params.append(state)
    
    if route_name:
        query += " AND Route_name = %s"
        params.append(route_name)
    
    if ac_status:
        if ac_status == "AC":
            query += " AND LOWER(Bus_type) LIKE %s"
            params.append("%ac%")
        elif ac_status == "NON AC":
            query += " AND LOWER(Bus_type) LIKE %s"
            params.append("%non ac%")
    
    if seat_type:
        if seat_type == "Seater":
            query += " AND LOWER(Bus_type) LIKE %s"
            params.append("%seater%")
        elif seat_type == "Sleeper":
            query += " AND LOWER(Bus_type) LIKE %s"
            params.append("%sleeper%")
    
    if price_range:
        if price_range == "100 to 500":
            query += " AND Price BETWEEN 100 AND 500"
        elif price_range == "501 to 1000":
            query += " AND Price BETWEEN 501 AND 1000"
        elif price_range == "Above 1000":
            query += " AND Price > 1000"
    
    if min_rating:
        query += " AND Ratings >= %s"
        params.append(min_rating)
    
    cursor.execute(query, tuple(params))
    buses = cursor.fetchall()
    return buses

# Streamlit UI
st.title("Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit")

# State filter
state = st.selectbox("Select State", [""] + states)

# Route filter, dependent on State selection
if state:
    routes = get_routes_for_state(state)
    route_name = st.selectbox("Select Route", [""] + routes)
else:
    route_name = st.selectbox("Select Route", ["Select a State first"])

# AC Status filter (AC or NON AC)
ac_status = st.selectbox("Select AC Status", ["", "AC", "NON AC"])

# Seat Type filter (Seater or Sleeper)
seat_type = st.selectbox("Select Seat Type", ["", "Seater", "Sleeper"])

# Price filter (dropdown)
price_range = st.selectbox("Select Price Range", ["", "100 to 500", "501 to 1000", "Above 1000"])

# Ratings filter (slider)
min_rating = st.slider("Select Minimum Rating", 0, 5, 0)

# Filter the data based on selections
if state and (route_name or ac_status or seat_type or price_range or min_rating):
    buses = get_filtered_buses(state, route_name, ac_status, seat_type, price_range, min_rating)
    
    if buses:
        # Display bus details in a table format
        df = pd.DataFrame(buses, columns=["ID", "Bus_name", "Bus_type", "Start_time", "End_time", "Total_duration", "Price", "Seats_Available", "Ratings", "Route_link", "Route_name", "State"])
        st.dataframe(df)
    else:
        st.write("No buses found matching the selected filters.")
else:
    st.write("Please select at least one filter.")
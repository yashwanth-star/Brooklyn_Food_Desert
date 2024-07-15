import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import base64
import json
from shapely import wkt

# Function to add custom CSS for styling
def add_custom_css():
    st.markdown(
        """
        <style>
        .title {
            font-size: 48px;
            font-weight: bold;
        }
        .sidebar .sidebar-content {
            font-size: 24px;
        }
        .header {
            font-size: 36px;
            font-weight: bold;
        }
        .text {
            font-size: 24px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to create a Folium map
def create_map(data, map_type, year=None):
    m = folium.Map(location=[40.6782, -73.9442], zoom_start=12)  # Centered on Brooklyn
    if map_type == "LILA & Non-LILA Zones":
        folium.TileLayer('Stamen Toner').add_to(m)
    elif map_type == "Supermarket Coverage Ratio" or map_type == "Fast Food Coverage Ratio":
        if year:
            # Filter data based on the selected year
            filtered_data = data[data['Year'] == year]
            for _, row in filtered_data.iterrows():
                geometry = wkt.loads(row['geometry'])
                folium.GeoJson(geometry.__geo_interface__).add_to(m)
    return m

# Add custom CSS
add_custom_css()

# Title and Sidebar
st.markdown('<div class="title">Food Desert Analysis in Brooklyn</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar">Navigation</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar">Choose a page:</div>', unsafe_allow_html=True)

# Page Selection
page = st.sidebar.selectbox("Select Page", ["Home", "Data Visualization", "Comments", "Help"])

# Home Page
if page == "Home":
    st.markdown('<div class="header">Welcome to the Food Desert Analysis App</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">This app helps to analyze food desert regions in Brooklyn.</div>', unsafe_allow_html=True)

# Data Visualization Page
elif page == "Data Visualization":
    st.markdown('<div class="header">Data Visualization</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">Visualize different aspects of food deserts in Brooklyn.</div>', unsafe_allow_html=True)
    
    # Select map type
    map_type = st.sidebar.radio("Select from any 3 Maps", ["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])
    
    # Show year selection for "Supermarket Coverage Ratio" and "Fast Food Coverage Ratio"
    if map_type != "LILA & Non-LILA Zones":
        year = st.sidebar.radio("Food Policies", [2003, 2015, 2016, 2017, 2023])
    else:
        year = None
    
    # Load data
    try:
        if map_type == "Supermarket Coverage Ratio":
            data = pd.read_csv('supermarkets.csv')
        elif map_type == "Fast Food Coverage Ratio":
            data = pd.read_csv('fastfood.csv')
        else:
            data = pd.read_csv('LILAZones_geo.csv')
        st.markdown('<div class="text">Data loaded successfully!</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data = pd.DataFrame()

    # Create and display map
    if not data.empty:
        m = create_map(data, map_type, year)
        st_folium(m, width=700, height=500)

    # Download Options
    if st.sidebar.button("Download Data as CSV"):
        if not data.empty:
            csv = data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="food_desert_data.csv">Download CSV File</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
        else:
            st.sidebar.error("No data available to download.")

    # Sharing Feature
    if st.sidebar.button("Share App"):
        st.sidebar.markdown("Share this app using the link: [App Link](http://example.com)")

# Comments Page
elif page == "Comments":
    st.markdown('<div class="header">Comments</div>', unsafe_allow_html=True)
    st.text_area("Leave your comments here:")

# Help Page
elif page == "Help":
    st.markdown('<div class="header">Help and Tutorial</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">How to effectively use the app:</div>', unsafe_allow_html=True)
    st.markdown('1. Use the sidebar to select different map types and years.')
    st.markdown('2. Hover over areas to see detailed information.')
    st.markdown('3. Click on areas to see more details or navigate to other sections.')

# Display main map on the page
if page == "Home" or page == "Data Visualization":
    st.markdown('<div class="text">Select from the sidebar to visualize different data sets.</div>', unsafe_allow_html=True)

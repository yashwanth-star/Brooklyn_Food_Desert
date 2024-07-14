import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import base64
import shapely.wkt
import shapely.geometry
import json

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
        for _, row in data.iterrows():
            try:
                geom = shapely.wkt.loads(row['geometry'])
                geojson_data = shapely.geometry.mapping(geom)
                folium.GeoJson(
                    geojson_data,
                    tooltip=folium.GeoJsonTooltip(
                        fields=['Census Tract Area', 'NTA', 'Food Index', 'Median Family Income', 'Poverty Rate', 'SNAP Benefits'],
                        aliases=['Census Tract Area:', 'NTA:', 'Food Index:', 'Median Family Income:', 'Poverty Rate:', 'SNAP Benefits:'],
                    )
                ).add_to(m)
            except Exception as e:
                st.error(f"Error processing GeoJSON data: {e}")
                st.error(row['geometry'])
    else:
        if year:
            # Filter data based on the selected year
            filtered_data = data[data['Year'] == year]
            for _, row in filtered_data.iterrows():
                folium.Marker(location=[row['lat'], row['lon']], popup=row['popup_info']).add_to(m)
    return m

# Function to search and highlight a specific Census Tract Area
def search_census_tract(data, tract_area):
    tract_info = data[data['Census Tract Area'] == tract_area]
    if not tract_info.empty:
        try:
            geom = shapely.wkt.loads(tract_info.iloc[0]['geometry'])
            geojson_data = shapely.geometry.mapping(geom)
            m = folium.Map(location=[geom.centroid.y, geom.centroid.x], zoom_start=14)
            folium.GeoJson(
                geojson_data,
                tooltip=folium.GeoJsonTooltip(
                    fields=['Census Tract Area', 'NTA', 'Food Index', 'Median Family Income', 'Poverty Rate', 'SNAP Benefits'],
                    aliases=['Census Tract Area:', 'NTA:', 'Food Index:', 'Median Family Income:', 'Poverty Rate:', 'SNAP Benefits:'],
                )
            ).add_to(m)
            return m
        except Exception as e:
            st.error(f"Error processing GeoJSON data: {e}")
            st.error(tract_info.iloc[0]['geometry'])
            return None
    else:
        return None

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
    
    # Show year selection for all map types
    year = st.sidebar.radio("Food Policies", [2015, 2016, 2017, 2023])

    # Load data
    if map_type == "LILA & Non-LILA Zones":
        try:
            data = pd.read_csv('C:/Users/Akash J/Downloads/LILAZones_geo_corrected.csv')
            st.markdown('<div class="text">LILA Zones data loaded successfully!</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading LILA Zones data: {e}")
            data = pd.DataFrame()
    else:
        data = pd.DataFrame({
            'lat': [40.6782, 40.6792, 40.6802],
            'lon': [-73.9442, -73.9452, -73.9462],
            'popup_info': ['Info 1', 'Info 2', 'Info 3'],
            'Year': [2015, 2016, 2017]
        })

    # Create and display map
    if not data.empty:
        m = create_map(data, map_type, year)
        st_folium(m, width=700, height=500)

    # Search functionality for all map types
    search_query = st.sidebar.text_input("Search for Census Tract Area:")
    if st.sidebar.button("Search"):
        search_map = search_census_tract(data, search_query)
        if search_map:
            st_folium(search_map, width=700, height=500)
        else:
            st.sidebar.error("Census Tract Area not found.")

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

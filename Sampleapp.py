import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import base64
import geopandas as gpd  # New import for handling geospatial data
import matplotlib.pyplot as plt

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
def create_map(data, map_type, year):
    m = folium.Map(location=[40.6782, -73.9442], zoom_start=12)  # Centered on Brooklyn
    if map_type == "LILA & Non-LILA Zones":
        folium.TileLayer('Stamen Toner').add_to(m)
    elif map_type == "Supermarket Coverage Ratio":
        folium.TileLayer('Stamen Watercolor').add_to(m)
    else:
        folium.TileLayer('CartoDB positron').add_to(m)

    # Add sample markers (to be replaced with actual data)
    for _, row in data.iterrows():
        folium.Marker(location=[row['lat'], row['lon']], popup=row['popup_info']).add_to(m)
    return m

# Function to search for a census tract and zoom in
def search_census_tract(tract_number, gdf):
    try:
        tract = gdf[gdf['tract_number'] == tract_number]
        if not tract.empty:
            centroid = tract.geometry.centroid.iloc[0]
            m = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)
            folium.GeoJson(tract).add_to(m)
            folium.Marker(location=[centroid.y, centroid.x], popup=f"Census Tract: {tract_number}").add_to(m)
            return m, tract
        else:
            st.error("Census Tract not found.")
            return None, None
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

# Add custom CSS
add_custom_css()

# Title and Sidebar
st.markdown('<div class="title">Food Desert Analysis in Brooklyn</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar">Navigation</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar">Choose a page:</div>', unsafe_allow_html=True)

# Page Selection
page = st.sidebar.selectbox("Select Page", ["Home", "Data Visualization", "Data Analysis", "Comments", "Help"])

# Load geospatial data
gdf = gpd.read_file('path_to_census_tracts.geojson')  # Replace with actual path to geojson file
data = pd.read_csv('path_to_your_data.csv')  # Replace with actual data path

# Home Page
if page == "Home":
    st.markdown('<div class="header">Welcome to the Food Desert Analysis App</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">This app helps to analyze food desert regions in Brooklyn.</div>', unsafe_allow_html=True)

# Data Visualization Page
elif page == "Data Visualization":
    st.markdown('<div class="header">Data Visualization</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">Visualize different aspects of food deserts in Brooklyn.</div>', unsafe_allow_html=True)
    
    # Select map type and year
    map_type = st.sidebar.radio("Select from any 3 Maps", ["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])
    year = st.sidebar.radio("Food Policies", [2015, 2016, 2017, 2023])

    # Create and display map
    m = create_map(data, map_type, year)
    st_folium(m, width=700, height=500)

# Data Analysis Page
elif page == "Data Analysis":
    st.markdown('<div class="header">Data Analysis</div>', unsafe_allow_html=True)
    st

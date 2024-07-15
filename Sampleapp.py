import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import base64
import json
from shapely import wkt
from geopandas import GeoDataFrame

# Function to create a Folium map
def create_map(data, year):
    m = folium.Map(location=[40.6782, -73.9442], zoom_start=12)  # Centered on Brooklyn
    for _, row in data.iterrows():
        try:
            geojson_data = json.loads(row['geometry'])
            folium.GeoJson(
                geojson_data,
                tooltip=folium.GeoJsonTooltip(
                    fields=['GEOID', f'{year}_supermarket coverage ratio', f'{year}_rank'],
                    aliases=['GEOID:', f'Supermarket Coverage Ratio {year}:', f'Rank in {year}:'],
                )
            ).add_to(m)
        except Exception as e:
            st.error(f"Error processing GeoJSON data: {e}")
    return m

# Title and Sidebar
st.title("Food Desert Analysis in Brooklyn")
st.sidebar.header("Navigation")
st.sidebar.subheader("Choose a page:")

# Page Selection
page = st.sidebar.selectbox("Select Page", ["Home", "Data Visualization", "Comments", "Help"])

# Home Page
if page == "Home":
    st.header("Welcome to the Food Desert Analysis App")
    st.write("This app helps to analyze food desert regions in Brooklyn.")

# Data Visualization Page
elif page == "Data Visualization":
    st.header("Data Visualization")
    st.write("Visualize different aspects of food deserts in Brooklyn.")
    
    # Select map type
    map_type = st.sidebar.radio("Select Map", ["Supermarket Coverage Ratio"])
    
    # Show year selection for Supermarket Coverage Ratio
    year = st.sidebar.radio("Select Year", [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2017])
    
    # Load data
    try:
        data = pd.read_csv('supermarkets.csv')
        # Convert the 'geometry' column to proper GeoJSON format
        data['geometry'] = data['geometry'].apply(lambda x: json.dumps(wkt.loads(x).__geo_interface__))
        st.write("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data = pd.DataFrame()

    # Create and display map
    if not data.empty:
        m = create_map(data, year)
        st_folium(m, width=700, height=500)

    # Download Options
    if st.sidebar.button("Download Data as CSV"):
        if not data.empty:
            csv = data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="supermarket_coverage_data.csv">Download CSV File</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
        else:
            st.sidebar.error("No data available to download.")

    # Sharing Feature
    if st.sidebar.button("Share App"):
        st.sidebar.markdown("Share this app using the link: [App Link](http://example.com)")

# Comments Page
elif page == "Comments":
    st.header("Comments")
    st.text_area("Leave your comments here:")

# Help Page
elif page == "Help":
    st.header("Help and Tutorial")
    st.write("How to effectively use the app:")
    st.markdown("""
    1. Use the sidebar to select different map types and years.
    2. Hover over areas to see detailed information.
    3. Click on areas to see more details or navigate to other sections.
    """)

# Display main map on the page
if page == "Home" or page == "Data Visualization":
    st.write("Select from the sidebar to visualize different data sets.")

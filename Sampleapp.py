import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium, folium_static
from shapely import wkt
import base64

# Cache the data loading and processing function
@st.cache_data
def load_data():
    data = pd.read_csv('LILAZones_geo.csv')
    data['geometry'] = data['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84
    return gdf

# Cache the data loading and processing function for supermarkets
@st.cache_resource
def load_and_process_data(data_path):
    data = pd.read_csv(data_path)
    gdf = gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data['geometry']))
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf

# Load and process the data for supermarkets
supermarket_data_path = "supermarkets.csv"
gdf_supermarkets = load_and_process_data(supermarket_data_path)

# Load and process the data for fast food
fast_food_data_path = "Fast Food Restaurants.csv"
gdf_fast_food = load_and_process_data(fast_food_data_path)

# Function to create a folium map for a given year and optionally filter by rank for supermarkets
def create_supermarket_map(year, selected_rank=None):
    # Create a base map
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)  # Centered around New York
    
    # Add data to the map
    year_column = f'{year}_supermarket coverage ratio'
    rank_column = f'{year}_rank'
    
    # Check if columns exist
    if year_column not in gdf_supermarkets.columns or rank_column not in gdf_supermarkets.columns:
        st.error(f"Column '{year_column}' or '{rank_column}' does not exist in the data.")
        return m
    
    # Filter GeoDataFrame if a specific rank is selected
    gdf_filtered = gdf_supermarkets.copy()
    if selected_rank and selected_rank != 'All':
        gdf_filtered = gdf_filtered[gdf_filtered[rank_column] == selected_rank]
    
    folium.Choropleth(
        geo_data=gdf_filtered,
        name='choropleth',
        data=gdf_filtered,
        columns=['GEOID', year_column],
        key_on='feature.properties.GEOID',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Supermarket Coverage Ratio'
    ).add_to(m)
    
    # Add tooltips
    folium.GeoJson(
        gdf_filtered,
        style_function=lambda x: {'fillColor': '#ffffff00', 'color': '#00000000', 'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=['TRACTCE', year_column, rank_column],
            aliases=['Census Tract Area', f'{year} Supermarket Coverage Ratio', 'Rank'],
            localize=True
        )
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

# Function to create a folium map for a given year and optionally filter by rank for fast food
def create_fast_food_map(year, selected_rank=None):
    # Create a base map
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)  # Centered around New York
    
    # Add data to the map
    year_column = f'{year}_Fast Food Coverage Ratio'
    rank_column = f'{year}_rank'
    
    # Check if columns exist
    if year_column not in gdf_fast_food.columns or rank_column not in gdf_fast_food.columns:
        st.error(f"Column '{year_column}' or '{rank_column}' does not exist in the data.")
        return m
    
    # Filter GeoDataFrame if a specific rank is selected
    gdf_filtered = gdf_fast_food.copy()
    if selected_rank and selected_rank != 'All':
        gdf_filtered = gdf_filtered[gdf_filtered[rank_column] == selected_rank]
    
    folium.Choropleth(
        geo_data=gdf_filtered,
        name='choropleth',
        data=gdf_filtered,
        columns=['GEOID', year_column],
        key_on='feature.properties.GEOID',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Fast Food Restaurant Coverage Ratio'
    ).add_to(m)
    
    # Add tooltips
    folium.GeoJson(
        gdf_filtered,
        style_function=lambda x: {'fillColor': '#ffffff00', 'color': '#00000000', 'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=['TRACTCE', year_column, rank_column],
            aliases=['Census Tract Area', f'{year} Fast Food Coverage Ratio', 'Rank'],
            localize=True
        )
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

# Function to display tooltip info in a styled format
def display_tooltip_info(gdf_filtered, year, coverage_ratio_col):
    if not gdf_filtered.empty:
        for _, row in gdf_filtered.iterrows():
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #f9f9f9;">
                    <h4 style="color: #2E7D32;">Census Tract Area: {row['TRACTCE']}</h4>
                    <p><span style="color: #D32F2F;">{year}: </span>{row[coverage_ratio_col]}</p>
                    <p><span style="color: #1976D2;">Rank: </span>{row[f'{year}_rank']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Main function to create the app
def main():
    st.sidebar.title("Navigation")
    page_icons = {
        "Home": "🏠",
        "Data Analysis": "📊",
        "Data Visualization": "📈",
        "Comments": "💬",
        "Guide": "📖"
    }

    pages = ["Home", "Data Analysis", "Data Visualization", "Comments", "Guide"]
    selection = st.sidebar.radio("Go to", pages, format_func=lambda page: f"{page_icons[page]} {page}")

    st.title(selection)

    if selection == "Home":
        st.write("Welcome to the Food Desert Analysis App")
        st.write("This app helps to analyze food desert regions in Brooklyn.")
    
    elif selection == "Data Analysis":
        st.write("Data analysis content goes here.")

    elif selection == "Data Visualization":
        # Map selection using tabs
        tabs = st.tabs(["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])

        with tabs[0]:
            st.header("LILA & Non-LILA Zones")
            gdf = load_data()

            search_query_nta = st.selectbox(
                "Search for NTA Name:",
                options=["All"] + gdf['NTA Name'].unique().tolist()
            )

            search_query_tract = st.selectbox(
                "Search for Census Tract Area:",
                options=["All"] + (gdf[gdf['NTA Name'] == search_query_nta]['Census Tract Area'].unique().tolist() if search_query_nta != "All" else gdf['Census Tract Area'].unique().tolist())
            )

            if search_query_nta != "All" and search_query_tract != "All":
                filtered_gdf = gdf[(gdf['NTA Name'] == search_query_nta) & (gdf['Census Tract Area'] == search_query_tract)]
            elif search_query_nta != "All":
                filtered_gdf = gdf[gdf['NTA Name'] == search_query_nta]
            else:
                filtered_gdf = gdf

            m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)
            folium.GeoJson(
                filtered_gdf,
                style_function=lambda feature: {
                    'fillColor': 'red

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Load the data
@st.cache
def load_data():
    data = pd.read_csv('LILAZones_geo.csv')
    data['geometry'] = data['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    return gdf

# Main function to create the app
def main():
    st.title("LILA Zones Map")

    # Load data
    gdf = load_data()

    # Create a folium map centered around the data
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

    # Add the GeoDataFrame to the map
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': 'red',
            'color': 'red',
            'weight': 1,
            'fillOpacity': 0.6,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Census Tract Area', 'NTA Name', 'Status'],
            aliases=['Census Tract Area', 'NTA Name', 'Status'],
            localize=True
        )
    ).add_to(m)

    # Display the map
    st_folium(m, width=800, height=600)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely import wkt
import base64

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv('LILAZones_geo.csv')
    data['geometry'] = data['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84
    return gdf

# Main function to create the app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Data Visualization", "Comments", "Data Analysis", "Guide"])

    if page == "Home":
        st.title("Welcome to the Food Desert Analysis App")
        st.write("This app helps to analyze food desert regions in Brooklyn.")
    
    elif page == "Data Visualization":
        st.title("Data Visualization")

        # Map selection
        map_type = st.sidebar.radio("Select Map Type", ["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])
        gdf = load_data()

        if map_type == "LILA & Non-LILA Zones":
            st.header("LILA & Non-LILA Zones")

            search_query = st.sidebar.selectbox(
                "Search for NTA Name:",
                options=["All"] + gdf['NTA Name'].unique().tolist()
            )
            
            if search_query != "All":
                filtered_gdf = gdf[gdf['NTA Name'] == search_query]
                if not filtered_gdf.empty:
                    row = filtered_gdf.iloc[0]
                    st.subheader(f"Details for {row['NTA Name']}")
                    st.write(f"**Food Index:** {row['Food Index']}")
                    st.write(f"**Median Family Income:** {row[' Median Family Income ']}")
                    st.write(f"**Poverty Rate:** {row['Education below high school diploma (Poverty Rate)']}")
                    st.write(f"**SNAP Benefits:** {row['SNAP Benefits %']}")
            else:
                filtered_gdf = gdf

            m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)
            folium.GeoJson(
                filtered_gdf,
                style_function=lambda feature: {
                    'fillColor': 'red',
                    'color': 'red',
                    'weight': 1,
                    'fillOpacity': 0.6,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['NTA Name', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %'],
                    aliases=['NTA Name:', 'Food Index:', 'Median Family Income:', 'Poverty Rate:', 'SNAP Benefits:'],
                    localize=True
                )
            ).add_to(m)
            st_folium(m, width=800, height=600)

        elif map_type == "Supermarket Coverage Ratio":
            st.header("Supermarket Coverage Ratio")
            # Your implementation for Supermarket Coverage Ratio map

        elif map_type == "Fast Food Coverage Ratio":
            st.header("Fast Food Coverage Ratio")
            # Your implementation for Fast Food Coverage Ratio map

        # Share App button with Gmail link
        share_text = "Check out this Food Desert Analysis App!"
        app_link = "https://samplefooddesert01.streamlit.app/"
        mailto_link = f"mailto:?subject=Food Desert Analysis App&body={share_text}%0A{app_link}"
        st.sidebar.markdown(f'<a href="{mailto_link}" target="_blank"><button style="background-color:green;color:white;border:none;padding:10px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;">Share App via Email</button></a>', unsafe_allow_html=True)

        # Download CSV button
        csv = gdf.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="LILAZones_geo.csv"><button style="background-color:blue;color:white;border:none;padding:10px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;">Download CSV</button></a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    elif page == "Comments":
        st.title("Comments")
        st.text_area("Leave your comments here:")

    elif page == "Data Analysis":
        st.title("Data Analysis")
        st.write("Data analysis content goes here.")

    elif page == "Guide":
        st.title("Guide")
        st.write("How to use the app content goes here.")

if __name__ == "__main__":
    main()

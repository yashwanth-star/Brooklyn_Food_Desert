import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely import wkt

# Function to load and process data
@st.cache_data
def load_data():
    data = pd.read_csv('LILAZones_geo.csv')
    data['geometry'] = data['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84
    return gdf

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Main function to create the app
def main():
    st.title("Food Desert Analysis in Brooklyn")
    
    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.selectbox("Select Page", ["Home", "Data Visualization", "Comments", "Data Analysis", "Guide"])

    if page == "Home":
        st.header("Welcome to the Food Desert Analysis App")
        st.write("This app helps to analyze food desert regions in Brooklyn.")
    
    elif page == "Data Visualization":
        st.header("Data Visualization")
        st.write("Visualize different aspects of food deserts in Brooklyn.")
        
        # Sidebar for map selection with radio buttons
        map_option = st.sidebar.radio("Choose a map:", ["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])

        if map_option == "LILA & Non-LILA Zones":
            st.subheader("LILA & Non-LILA Zones")
            
            # Load data
            gdf = load_data()

            # Convert DataFrame to CSV
            csv = convert_df_to_csv(gdf)

            # Create a download button in the sidebar
            st.sidebar.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name='LILAZones_geo.csv',
                mime='text/csv',
            )

            # Create a search option with suggestions for NTA names including "All"
            nta_names = ["All"] + list(gdf['NTA Name'].unique())
            selected_nta = st.sidebar.selectbox("Search for NTA Name:", nta_names)

            # Filter the data based on the selected NTA name
            if selected_nta != "All":
                filtered_gdf = gdf[gdf['NTA Name'] == selected_nta]
            else:
                filtered_gdf = gdf

            # Create a folium map centered around the data
            m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

            # Add the GeoDataFrame to the map
            folium.GeoJson(
                filtered_gdf,
                style_function=lambda feature: {
                    'fillColor': 'red',
                    'color': 'red',
                    'weight': 1,
                    'fillOpacity': 0.6,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[
                        'NTA Name', 'Food Index', 
                        ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %'
                    ],
                    aliases=[
                        'NTA Name:', 'Food Index:', 
                        'Median Family Income (USD):', 'Poverty Rate (%):', 'SNAP Benefits (%):'
                    ],
                    localize=True
                )
            ).add_to(m)

            # Display the map
            st_folium(m, width=800, height=600)

            # Display the tooltip information below the map if a specific NTA name is selected
            if selected_nta != "All":
                st.markdown(f"## Details for {selected_nta}")
                info = filtered_gdf[['NTA Name', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %']].iloc[0]
                st.markdown(f"""
                    **NTA Name:** {info['NTA Name']}  
                    **Food Index:** {info['Food Index']}  
                    **Median Family Income (USD):** {info[' Median Family Income ']}  
                    **Poverty Rate (%):** {info['Education below high school diploma (Poverty Rate)']}  
                    **SNAP Benefits (%):** {info['SNAP Benefits %']}  
                """)

            # Add a beautified share button
            st.sidebar.markdown("## Share App")
            shareable_link = "https://samplefooddesert01.streamlit.app/"
            share_button_html = f"""
            <a href="{shareable_link}" target="_blank">
                <button style="
                    background-color: #4CAF50; /* Green */
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 12px;
                ">
                    Share this app
                </button>
            </a>
            """
            st.sidebar.markdown(share_button_html, unsafe_allow_html=True)

        elif map_option == "Supermarket Coverage Ratio":
            st.subheader("Supermarket Coverage Ratio")
            # Placeholder for Supermarket Coverage Ratio functionality
            st.write("Supermarket Coverage Ratio functionality to be added.")
        
        elif map_option == "Fast Food Coverage Ratio":
            st.subheader("Fast Food Coverage Ratio")
            # Placeholder for Fast Food Coverage Ratio functionality
            st.write("Fast Food Coverage Ratio functionality to be added.")
    
    elif page == "Comments":
        st.header("Comments")
        st.text_area("Leave your comments here:")
    
    elif page == "Data Analysis":
        st.header("Data Analysis")
        st.write("Analyze the food desert data.")
    
    elif page == "Guide":
        st.header("Guide")
        st.write("How to effectively use the app:")
        st.markdown('1. Use the sidebar to select different map types and years.')
        st.markdown('2. Hover over areas to see detailed information.')
        st.markdown('3. Click on areas to see more details or navigate to other sections.')

if __name__ == "__main__":
    main()

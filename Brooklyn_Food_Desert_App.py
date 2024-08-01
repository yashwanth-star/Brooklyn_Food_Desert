import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from shapely import wkt
import base64

# Cache the data loading and processing function
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['geometry'] = data['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84
    return gdf

# Load and process the data
lila_data_path = 'LILAZones_geo.csv'
gdf_lila = load_data(lila_data_path)

supermarket_data_path = "supermarkets.csv"
gdf_supermarkets = load_data(supermarket_data_path)

fast_food_data_path = "Fast Food Restaurants.csv"
gdf_fast_food = load_data(fast_food_data_path)

# Function to create a folium map for a given year and optionally filter by rank
def create_map(gdf, year, coverage_ratio_col, rank_col, selected_rank=None, legend_name="Coverage Ratio"):
    # Create a base map
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)  # Centered around New York
    
    # Check if columns exist
    if coverage_ratio_col not in gdf.columns or rank_col not in gdf.columns:
        st.error(f"Column '{coverage_ratio_col}' or '{rank_col}' does not exist in the data.")
        return m
    
    # Filter GeoDataFrame if a specific rank is selected
    gdf_filtered = gdf.copy()
    if selected_rank and selected_rank != 'All':
        gdf_filtered = gdf_filtered[gdf_filtered[rank_col] == selected_rank]
    
    folium.Choropleth(
        geo_data=gdf_filtered,
        name='choropleth',
        data=gdf_filtered,
        columns=['TRACTCE', coverage_ratio_col],
        key_on='feature.properties.TRACTCE',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_name
    ).add_to(m)
    
    # Add tooltips
    folium.GeoJson(
        gdf_filtered,
        style_function=lambda x: {'fillColor': '#ffffff00', 'color': '#00000000', 'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=['TRACTCE', coverage_ratio_col, rank_col],
            aliases=['Census Tract Area', f'{year} {legend_name}', 'Rank'],
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
            
            search_query_nta = st.selectbox(
                "Search for NTA Name:",
                options=["All"] + gdf_lila['NTA Name'].unique().tolist()
            )

            # Filter the GeoDataFrame based on the selected NTA Name
            if search_query_nta != "All":
                filtered_gdf = gdf_lila[gdf_lila['NTA Name'] == search_query_nta]
            else:
                filtered_gdf = gdf_lila

            search_query_tract = st.selectbox(
                "Search for Census Tract Area:",
                options=["All"] + filtered_gdf['Census Tract Area'].unique().tolist()
            )

            # Update the filtering logic to highlight the selected Census Tract Area
            if search_query_tract != "All":
                filtered_gdf = gdf_lila[gdf_lila['Census Tract Area'] == search_query_tract]
                # Ensure NTA dropdown is updated according to selected Census Tract Area
                search_query_nta = st.selectbox(
                    "Search for NTA Name:",
                    options=["All"] + filtered_gdf['NTA Name'].unique().tolist(),
                    index=1 if search_query_nta == "All" else 0
                )
            elif search_query_nta != "All":
                filtered_gdf = gdf_lila[gdf_lila['NTA Name'] == search_query_nta]
            else:
                filtered_gdf = gdf_lila

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
                    fields=['Census Tract Area', 'NTA Name', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %'],
                    aliases=['Census Tract Area:', 'NTA Name:', 'Food Index:', 'Median Family Income:', 'Poverty Rate:', 'SNAP Benefits:'],
                    localize=True
                )
            ).add_to(m)
            folium_static(m, width=800, height=600)

            def display_info(details):
                for i, row in details.iterrows():
                    st.markdown(f"""
                        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; margin: 20px 0; background-color: #f9f9f9;">
                            <h4 style="color: #2E8B57;">{row['NTA Name']} - Census Tract Area: {row['Census Tract Area']}</h4>
                            <p><strong style="color: #FF6347;">Food Index:</strong> {row['Food Index']}</p>
                            <p><strong style="color: #4682B4;">Median Family Income:</strong> {row[' Median Family Income ']}</p>
                            <p><strong style="color: #8A2BE2;">Poverty Rate:</strong> {row['Education below high school diploma (Poverty Rate)']}</p>
                            <p><strong style="color: #DAA520;">SNAP Benefits:</strong> {row['SNAP Benefits %']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            if search_query_nta != "All":
                if search_query_tract == "All":
                    details = filtered_gdf[['NTA Name', 'Census Tract Area', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %']]
                    st.subheader(f"Details for {search_query_nta}")
                    display_info(details)
                else:
                    details = filtered_gdf[['NTA Name', 'Census Tract Area', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %']]
                    display_info(details)

        with tabs[1]:
            st.header("Supermarket Coverage Ratio")
            
            # Add a select slider for the years
            years = list(range(2003, 2018))  # Adjust this range based on your data
            year = st.select_slider(
                "Select Year",
                options=years,
                value=min(years),
                format_func=lambda x: f"{x}",
                key="supermarket_year_slider"
            )

            # Add a select box for Rank search
            rank_options = ['All'] + sorted([rank for rank in gdf_supermarkets[f'{year}_rank'].dropna().unique() if rank.isdigit()], key=int)
            selected_rank = st.selectbox(f"Select a Rank for the year {year} or 'All':", rank_options, key="supermarket_rank_select")

            # Create and display the map
            m = create_map(gdf_supermarkets, year, f'{year}_supermarket coverage ratio', f'{year}_rank', selected_rank, "Supermarket Coverage Ratio")
            folium_static(m)

            # Display the tooltip information below the map if a specific rank is selected
            if selected_rank != 'All':
                filtered_gdf = gdf_supermarkets[gdf_supermarkets[f'{year}_rank'] == selected_rank]
                display_tooltip_info(filtered_gdf, year, f'{year}_supermarket coverage ratio')

        with tabs[2]:
            st.header("Fast Food Coverage Ratio")
            
            # Add a select slider for the years
            years = list(range(2003, 2018))  # Adjust this range based on your data
            year = st.select_slider(
                "Select Year",
                options=years,
                value=min(years),
                format_func=lambda x: f"{x}",
                key="fast_food_year_slider"
            )

            # Add a select box for Rank search
            rank_options = ['All'] + sorted([rank for rank in gdf_fast_food[f'{year}_rank'].dropna().unique() if rank.isdigit()], key=int)
            selected_rank = st.selectbox(f"Select a Rank for the year {year} or 'All':", rank_options, key="fast_food_rank_select")

            # Create and display the map
            m = create_map(gdf_fast_food, year, f'{year}_Fast Food Coverage Ratio', f'{year}_rank', selected_rank, "Fast Food Coverage Ratio")
            folium_static(m)

            # Display the tooltip information below the map if a specific rank is selected
            if selected_rank != 'All':
                filtered_gdf = gdf_fast_food[gdf_fast_food[f'{year}_rank'] == selected_rank]
                display_tooltip_info(filtered_gdf, year, f'{year}_Fast Food Coverage Ratio')

        # Share App button with Gmail link
        share_text = "Check out this Food Desert Analysis App!"
        app_link = "https://samplefooddesert01.streamlit.app/"
        mailto_link = f"mailto:?subject=Food Desert Analysis App&body={share_text}%0A{app_link}"
        st.sidebar.markdown(f'<a href="{mailto_link}" target="_blank"><button style="background-color:green;color:white;border:none;padding:10px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;">Share App via Email</button></a>', unsafe_allow_html=True)

        # Download CSV button
        csv = gdf_lila.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="LILAZones_geo.csv"><button style="background-color:blue;color:white;border:none;padding:10px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;">Download CSV</button></a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    elif selection == "Comments":
        st.write("Leave your comments here:")
        st.text_area("Comments:")

    elif selection == "Guide":
        st.write("How to use the app content goes here.")

if __name__ == "__main__":
    main()

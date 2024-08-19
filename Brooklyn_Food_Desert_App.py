import streamlit as st
from PIL import Image
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from shapely import wkt
import base64
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
# Set page configuration
st.set_page_config(page_title="Food Deserts in Brooklyn", layout="wide")

# Title of the homepage
st.markdown("<h2 style='text-align: center;'>Evaluating Solutions to Ameliorate the Impact of Food Deserts in Brooklyn Using AI</h2>", unsafe_allow_html=True)

# Display the new Brooklyn image
brooklyn_image = Image.open("pexels-mario-cuadros-1166886-2706653.jpg")
st.image(brooklyn_image, use_column_width=True, caption='Brooklyn, NY')

# Add the descriptive text below the image
st.markdown("""
### Understanding Food Deserts

According to the USDA, a food desert is defined as a census tract that meets both low-income and low-access criteria, including:

1. **A poverty rate greater than or equal to 20 percent,** or median family income not exceeding 80 percent of the statewide (rural/urban) or metro-area (urban) median family income.
2. **At least 500 people or 33 percent of the population located more than 1 mile (urban) or 10 miles (rural) from the nearest supermarket or large grocery store.**

Our analysis of the Food Access Research Atlas 2019 aimed to identify census tracts that meet this definition of food deserts (LILA zones). However, the dataset did not reveal any census tracts classified as food deserts.

To delve deeper, we explored various sources such as community blog posts, research papers, and news articles to understand how these census tracts are identified and categorized as food or non-food deserts. While the Food Access Research Atlas provided limited insights, other sources pointed us toward key features to consider when classifying a census tract as a food desert. Factors like **SNAP benefits, poverty rates, and income levels** frequently appeared in areas recognized as food deserts.

To create a comprehensive dataset, we explored the repository of datasets provided on the NaNDA (National Neighborhood Data Archive) website, which included demographic characteristics, socioeconomic characteristics, grocery level, etc., along with the Food Access Research Atlas. After experimenting with various combinations of variables, we selected a set of variables to input into clustering algorithms like **K-Means, Gaussian Mixture, and DB Scan.**
""")

# Create two columns for the new text and infographic
col1, col2 = st.columns([1, 1])  # Adjust proportions if needed

with col1:
    # Add the new descriptive text in the first column
    st.markdown("""
    ### Clustering Algorithms and Model Selection

    The selected variables were normalized within a range of 0-100 before being processed by these algorithms. Among them, **DB Scan** emerged as the most effective clustering model, with a silhouette score of 0.56.

    The variables included in the final model were:
    1. **SNAP Benefits:** The proportion of households using SNAP benefits to purchase food.
    2. **Population Earning Less Than $40K.**
    3. **Proportion of Population with Less Than a High School Diploma.**
    4. **Food Index:** A derived variable representing food accessibility.

    The **Food Index** was calculated by combining the number of supermarkets, coffee shops, fast food restaurants, and the poverty rate. We used a weighted average, assigning weights of +0.4 to supermarkets, +0.1 to coffee shops, and -0.5 to fast-food restaurants. These were then combined with the poverty rate to assess healthy food accessibility across Brooklyn's census tracts. The negative weight for fast food restaurants reflects their status as less healthy food options compared to supermarkets and coffee shops.
    """)

with col2:
    # Display the infographic in the second column
    infographic_image = Image.open("12.6 % of households in Brooklyn rely on SNAP (S.png")
    st.image(infographic_image, use_column_width=True)

# Main function to create the app
def main():
    st.sidebar.title("Navigation")
    page_icons = {
        "Home": "🏠",
        "Data Analysis": "📊",
        "Data Visualization": "📈",
        "Food Policy Reports": "📄",
        "Comments": "💬",
        "Guide": "📖"
    }

    pages = ["Home", "Data Analysis", "Data Visualization", "Food Policy Reports", "Comments", "Guide"]
    selection = st.sidebar.radio("Go to", pages, format_func=lambda page: f"{page_icons[page]} {page}")

    st.title(selection)

    if selection == "Home":
        # All content for the home page is defined above, so no need to add anything here
        pass

    elif selection == "Data Analysis":
        run_data_analysis()

    elif selection == "Data Visualization":
        # Map selection using tabs
        tabs = st.tabs(["LILA & Non-LILA Zones", "Supermarket Coverage Ratio", "Fast Food Coverage Ratio"])

        with tabs[0]:
            st.header("LILA & Non-LILA Zones")

            # Initial filter
            nta_options = ["All"] + gdf_lila['NTA Name'].unique().tolist()
            nta_selected = st.selectbox("Search for NTA Name:", nta_options)

            # Filter the GeoDataFrame based on the selected NTA Name
            if nta_selected != "All":
                filtered_gdf = gdf_lila[gdf_lila['NTA Name'] == nta_selected]
            else:
                filtered_gdf = gdf_lila

            # Census Tract Area filter based on the filtered GeoDataFrame
            tract_options = ["All"] + filtered_gdf['Census Tract Area'].unique().tolist()
            tract_selected = st.selectbox("Search for Census Tract Area:", tract_options)

            # Update the filtering logic to highlight the selected Census Tract Area
            if tract_selected != "All":
                filtered_gdf = gdf_lila[gdf_lila['Census Tract Area'] == tract_selected]
                # Ensure NTA dropdown is updated according to selected Census Tract Area
                nta_options = ["All"] + filtered_gdf['NTA Name'].unique().tolist()
                nta_selected = nta_options[1] if nta_selected == "All" else nta_selected
            elif nta_selected != "All":
                filtered_gdf = gdf_lila[gdf_lila['NTA Name'] == nta_selected]
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

            if nta_selected != "All":
                if tract_selected == "All":
                    details = filtered_gdf[['NTA Name', 'Census Tract Area', 'Food Index', ' Median Family Income ', 'Education below high school diploma (Poverty Rate)', 'SNAP Benefits %']]
                    st.subheader(f"Details for {nta_selected}")
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

    elif selection == "Food Policy Reports":
        st.title("Food Policy Reports")

        # Video
        video_file = open('3245641-uhd_3840_2160_25fps.mp4', 'rb')
        video_bytes = video_file.read()
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        video_html = f'''
        <video autoplay loop muted width="100%">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        '''
        st.markdown(video_html, unsafe_allow_html=True)

        # Link to Food Policy Reports page
        st.markdown(
            '''
            <a href="https://www.nyc.gov/site/foodpolicy/reports-and-data/food-metrics-report.page" target="_blank" class="btn btn-primary" style="text-decoration: none;">
                <button style="background-color: #0044cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                    Visit Food Policy Reports
                </button>
            </a>
            ''',
            unsafe_allow_html=True
        )

        # Content
        st.markdown("""
        ## Importance of Food Policy Reports

        Food policy reports are essential tools for shaping a sustainable and equitable food system. These reports, provided by the New York City Council, offer comprehensive data and insights into various aspects of food production, distribution, and consumption. They help policymakers, stakeholders, and the public understand the current state of the food landscape and the impact of food policies.

        ### Why Food Policy Reports Matter

        1. **Data-Driven Decision Making**: Food policy reports compile critical data from multiple sources, offering a detailed analysis of food-related issues. This information is crucial for making informed decisions that affect food security, nutrition, and public health.

        2. **Tracking Progress**: These reports track the progress of food-related initiatives and programs over time. By evaluating trends and outcomes, policymakers can assess the effectiveness of existing policies and identify areas needing improvement.

        3. **Addressing Food Insecurity**: Food policy reports highlight the prevalence and causes of food insecurity. By understanding the root causes, policymakers can implement targeted strategies to ensure that all community members have access to nutritious and affordable food.

        4. **Promoting Healthy Eating**: The reports provide insights into dietary trends and health outcomes, guiding initiatives that promote healthy eating habits. They support programs aimed at reducing diet-related diseases, such as obesity and diabetes, by increasing access to healthy food options.

        5. **Sustainability and Justice**: Food policy reports emphasize the importance of creating a sustainable and just food system. They address environmental impacts, food waste, and social equity, advocating for practices that protect the planet and ensure fair treatment for all workers within the food supply chain.

        6. **Public Awareness and Engagement**: By making food policy reports accessible to the public, these documents foster greater awareness and engagement. Citizens can better understand the challenges and opportunities within the food system and participate in shaping policies that affect their communities.

        ### Explore Our Reports

        To learn more about these initiatives and their impact, explore our comprehensive food policy reports provided by the New York City Council:

        - [2023 Food Standards Compliance Report & 2023 Food by the Numbers](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/Food%20Standards%20FY23%20Compliance%20Report_Final.pdf)
        - [2022 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/Food%20Metrics%20Report%20FY%202022_FINAL.pdf)
        - [2021 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/Food-Metrics-Report-2021.pdf)
        - [2020 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/food_metrics_report_2020-two_page_spread.pdf)
        - [2019 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/Food-Policy-Report-2019.pdf)
        - [2018 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/2018-Food-Metrics-Report.pdf)
        - [2017 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/2017-Food-Metrics-Report-Corrected.pdf)
        - [2016 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/2016-Food-Metrics-Report.pdf)
        - [2015 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/2015-food-metrics-report.pdf)
        - [2014 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/2014-food-metrics-report.pdf)
        - [2013 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/ll52-food-metrics-report-2013.pdf)
        - [2012 Food Metrics Report](https://www.nyc.gov/assets/foodpolicy/downloads/pdf/ll52-food-metrics-report-2012.pdf)

        Food policy reports are invaluable resources provided by the New York City Council that guide our journey toward a healthier, more equitable, and sustainable food system. By leveraging the data and insights provided in these reports, we can implement effective policies and initiatives that benefit everyone.
        """)

    elif selection == "Comments":
        st.write("Leave your comments here:")
        st.text_area("Comments:")

    elif selection == "Guide":
        st.write("How to use the app content goes here.")

if __name__ == "__main__":
    main()

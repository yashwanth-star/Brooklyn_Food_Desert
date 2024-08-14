import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from shapely import wkt
import base64
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

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

# Function to handle data analysis page
def run_data_analysis():
    # Load the datasets
    socioeconomics_df = pd.read_csv('dataset_socioeconomics.csv')
    convStores_df = pd.read_csv('dataset_convStores.csv')
    eating_df = pd.read_csv('dataset_eating.csv')
    corrPlot_df = pd.read_csv('dataset_forCorrPlot.csv')

    st.title("Interactive Data Analysis Page")

    ### 1. Family Income vs Race (2016-2020)
    st.header("Family Income vs Race (2016-2020)")

    # Rename columns for better display names
    socioeconomics_df.columns = ['ALL', 'White', 'Black', 'Hispanic']

    # Filter options
    races = list(socioeconomics_df.columns)  # Convert Index to list
    selected_races = st.multiselect('Select races to display', races, default=races)

    # Filter the dataframe
    filtered_income_df = socioeconomics_df[selected_races]

    # Create the plot
    fig1 = px.box(filtered_income_df, 
                 labels={'value': 'Family Income', 'variable': 'Race'},
                 title='Family Income vs Race (2016-2020)')

    # Display the plot in Streamlit
    st.plotly_chart(fig1)

    # Explanation
    st.markdown("""
    #### Explanation:
    This boxplot visualizes the distribution of family incomes across different racial groups between 2016 and 2020. Each box represents the interquartile range (IQR), showing the median and spread of the data. The whiskers indicate variability outside the upper and lower quartiles, while points beyond the whiskers are outliers. This visualization helps in identifying income disparities among various racial groups.
    """)

    ### 2. Employment in Convenience Stores Over Time
    st.header("Employment in Convenience Stores Over Time")

    # Rename columns for better display names
    convStores_df = convStores_df.rename(columns={
        'count_emp_4453': 'Alcohol',
        'count_emp_453991': 'Cigarettes',
        'count_emp_445120': 'Food stores'
    })

    # Filter options
    years_conv = convStores_df['year'].unique()
    selected_years_conv = st.slider('Select years for convenience stores', min_value=int(years_conv.min()), max_value=int(years_conv.max()), value=(int(years_conv.min()), int(years_conv.max())), key='slider_conv')

    # Filter the dataframe
    filtered_convStores_df = convStores_df[(convStores_df['year'] >= selected_years_conv[0]) & (convStores_df['year'] <= selected_years_conv[1])]

    # Create the plot
    fig2 = px.line(filtered_convStores_df, x='year', y=['Alcohol', 'Cigarettes', 'Food stores'],
                  labels={'value': 'Employment Count', 'year': 'Year'},
                  title='Employment in Convenience Stores Over Time')

    # Display the plot in Streamlit
    st.plotly_chart(fig2)

    # Explanation
    st.markdown("""
    #### Explanation:
    This line chart illustrates the trends in employment across different types of stores, including convenience stores, other general stores, and grocery stores over several years. The x-axis represents the years, while the y-axis represents the count of employees. The lines demonstrate how employment levels have changed over time, helping to identify growth or decline trends in these sectors.
    """)

    ### 3. Employment in Eating Establishments Over Time
    st.header("Employment in Eating Establishments Over Time")

    # Rename columns for better display names
    eating_df = eating_df.rename(columns={
        'count_emp_722511': 'Restaurants',
        'count_emp_722513': 'Fast-foods',
        'count_emp_722515': 'Snack places',
        'count_emp_722410': 'Drinking places'
    })

    # Filter options
    years_eating = eating_df['year'].unique()
    selected_years_eating = st.slider('Select years for eating establishments', min_value=int(years_eating.min()), max_value=int(years_eating.max()), value=(int(years_eating.min()), int(years_eating.max())), key='slider_eating')

    # Filter the dataframe
    filtered_eating_df = eating_df[(eating_df['year'] >= selected_years_eating[0]) & (eating_df['year'] <= selected_years_eating[1])]

    # Create the plot
    fig3 = px.line(filtered_eating_df, x='year', y=['Restaurants', 'Fast-foods', 'Snack places', 'Drinking places'],
                  labels={'value': 'Employment Count', 'year': 'Year'},
                  title='Employment in Eating Establishments Over Time')

    # Display the plot in Streamlit
    st.plotly_chart(fig3)

    # Explanation
    st.markdown("""
    #### Explanation:
    This line chart displays employment trends in various eating establishments, such as full-service restaurants, limited-service restaurants, snack and nonalcoholic beverage bars, and caterers over time. The x-axis denotes the years, and the y-axis indicates the count of employees. This plot helps in understanding how employment in different types of eating establishments has evolved, highlighting periods of growth or decline.
    """)

    ### 4. Employment in Convenience Stores, Liquor, and Tobacco Stores
    st.header("Employment in Convenience Stores, Liquor, and Tobacco Stores")

    # Create the grouped bar plot
    bar_width = 0.2
    years = convStores_df['year']
    r1 = range(len(years))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]

    # Create the plot
    fig4 = go.Figure(data=[
        go.Bar(name='Alcohol', x=years, y=convStores_df['Alcohol'], marker_color='blue', width=bar_width),
        go.Bar(name='Food stores', x=years, y=convStores_df['Food stores'], marker_color='red', width=bar_width),
        go.Bar(name='Cigarettes', x=years, y=convStores_df['Cigarettes'], marker_color='green', width=bar_width)
    ])

    # Update layout
    fig4.update_layout(barmode='group', xaxis_tickangle=-45, title='Mean Count by Year for Different Categories', xaxis_title='Year', yaxis_title='Mean Count')

    # Display the plot in Streamlit
    st.plotly_chart(fig4)

    # Explanation
    st.markdown("""
    #### Explanation:
    This grouped bar plot visualizes the mean count of employees in convenience stores, liquor stores, and tobacco stores over several years. Each group of bars represents a different year, and within each group, there are bars for alcohol, food stores, and cigarettes. This plot helps in understanding the employment trends in these specific categories over time.
    """)

    ### 5. Employment in Eating & Drinking Data
    st.header("Employment in Eating & Drinking Data")

    # Create the grouped bar plot
    bar_width = 0.35
    years = eating_df['year']
    indices = range(len(years))
    r1 = indices
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]
    r4 = [x + bar_width for x in r3]

    # Create the plot
    fig5 = go.Figure(data=[
        go.Bar(name='Restaurants', x=years, y=eating_df['Restaurants'], marker_color='green', width=bar_width),
        go.Bar(name='Fast-foods', x=years, y=eating_df['Fast-foods'], marker_color='red', width=bar_width),
        go.Bar(name='Snack places', x=years, y=eating_df['Snack places'], marker_color='purple', width=bar_width),
        go.Bar(name='Drinking places', x=years, y=eating_df['Drinking places'], marker_color='orange', width=bar_width)
    ])

    # Update layout
    fig5.update_layout(barmode='group', xaxis_tickangle=-45, title='Mean Count by Year for Different Categories', xaxis_title='Year', yaxis_title='Mean Count')

    # Display the plot in Streamlit
    st.plotly_chart(fig5)

    # Explanation
    st.markdown("""
    #### Explanation:
    This grouped bar plot visualizes the mean count of employees in various types of eating and drinking establishments over several years. Each group of bars represents a different year, and within each group, there are bars for restaurants, fast-foods, snack places, and drinking places. This plot helps in understanding the employment trends in these specific categories over time.
    """)

    ### 6. Correlation Heatmap
    st.header("Correlation Heatmap")

    # Filter options
    columns = list(corrPlot_df.columns)  # Convert Index to list
    selected_columns = st.multiselect('Select columns for correlation', columns, default=columns)

    # Filter the dataframe
    filtered_corr_df = corrPlot_df[selected_columns]

    # Create the correlation heatmap
    corr = filtered_corr_df.corr()
    fig6 = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        annotation_text=corr.round(2).values,
        colorscale='Viridis'
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig6)

    # Explanation
    st.markdown("""
    #### Explanation:
    This correlation heatmap visualizes the relationships between different variables in the dataset. Each cell in the heatmap shows the correlation coefficient between two variables, with colors representing the strength and direction of the correlation. Positive correlations are shown in one color gradient, while negative correlations are in another. This plot is useful for identifying which variables are strongly related, aiding in data analysis and decision-making.
    """)

    # Baseline Analysis Median Family Income
    st.header("Baseline Analysis Median Family Income")
    st.image('Baseline Analysis_Med Family Income.png', use_column_width=True)

    st.markdown("""
    ### Review and Interpretation of Baseline Analysis of Median Family Income for Brooklyn

    #### Overview:
    The supplementary data set includes median family income data by tracts in both East and West Bedford-Stuyvesant and other parts of Brooklyn. The data is arranged in a way that marks different tracts against the county’s highest and average median family incomes. Here's a breakdown of the key columns and their significance:

    - **TRACTCE**: This corresponds to the census tract code given only to that particular census tract.
    - **NTA Name**: This is the name of the tabulation area of the neighbourhood that has been developed at the census tract level.
    - **Median Family Income (USD)**: The income of families in each tract stated in USD.
    - **Relative Scale (Highest Median Family Income = 100)**: This represents the column of the relative scale of median family income, and is the median family income divided by the largest median family income in the database. A value of 100 embodies the highest median family income while all other states take whole number proportions according to this state.
    - **Relative Scale (Average Median Family Income = 100)**: As in the previous column, except that values were divided by the average median family income as a scaling factor.
    - **Income Deviation from Baseline (100 = Highest Median Family Income)**: This depicts the extent to which each tract’s median by family income is above or below the median by family income of the counties with the highest median by family income standardized to 100.
    - **Income Deviation from Baseline (100 = Average Median Family Income)**: This means the extent of departure from the average median family income index.

    #### Let's look at an example to illustrate these metrics:

      **Tract 28100 (Bedford-Stuyvesant East):**
      - **Median Family Income**: $25,625
      - **Relative Scale (Highest)**: 10. Calculation of the figure is as follows, $25,625 being one hundred percent, and twenty-five percent of this figure is $6,406.25. Therefore, an acceptable measure.
      - **Relative Scale (Average)**: 34. It is calculated as 34% of the average of median family incomes.
      - **Income Deviation (Highest)**: 89.75
      - **Income Deviation (Average)**: 65.90

    #### Analysing the Data:
    - **Income Distribution**:
      - **High-Income Areas**: As seen earlier, relative scales and income deviations are higher for tracts with higher median family income, about 40,000 or more, as observed in the tracts of Bedford-Stuyvesant (East) and Bensonhurst.
      - **Low-Income Areas**: Of the tracts, notably those located in Brownsville and East New York, tracts with lower medians, exhibit smaller relative scales and substantial negative income differential vis-a-vis the highest and the average medians.

    - **Relative Scales**:
      - **Highest Median Scale**: This is an illustration of how the income of each tract compares to the highest income in the dataset. For instance, Bedford-Stuyvesant (East) at $87,750 has a scale of 35. 10, indicating it's 35. Table 3 revealed that the spending was 1% of the highest median income.
      - **Average Median Scale**: This results in a wider view of the organization by benchmarking every tract’s income against a per capita income. Places with such values close or above 100 have a higher income level in relation to the overall median income.

    - **Income Deviation**:
      - **Positive Deviation**: Points to places where the median income that suggest the existing population has moved beyond the calculated baseline (highest or average). For example, the variation of Bensonhurst is 78. Thus, highest median can be established to be as at 056 with twenty-six. Hence, being 994 from the average, it is richer than many other areas.
      - **Negative Deviation**: This means that some of the features show that a particular location has a median income below the established baseline. Brownsville can be seen to be with a negative deviation which could indicate a problem in the economy in that particular region.

    - **Colour Coding**:
      - **Green**: Locations with values above the origin zero sign reflecting good economic conditions in the region.
      - **Yellow/Orange**: Moderate to slight positive deviations, which stand for the regions that have the average level of economic conditions.
      - **Red**: The additional five large negative disparities are underlined: economically disadvantaged areas.

    #### Key Insights:
    - **Income Variability within Neighbourhoods**:
      - **Bedford-Stuyvesant**: Even in certain areas such as Bedford-Stuyvesant you could have the eastern part of that area and the western part, and they will be completely different from each other. Bedford-Stuyvesant East (e. g. , Tract 28501) on average produces a higher median family income compared to Bedford-Stuyvesant West (e. g. , Tract 25902). Such a situation implies that there is a considerable economic dissimilarity within a comparatively compact region, which imply that even within well-defined communities there can be levels of relative wealth and pauperism.
      - **Brownsville**: Brownsville also demonstrates that most of the tracts average anemic median family income throughout the study, with for example tracts 90800 and 92000 among the lowest aural family incomes in the dataset. Such homogeneity suggests systematic economic problems which, perhaps, need area-based strategies of treatment.

    - **Potential Causes of Economic Disparity**:
      - **Historical Factors**: Places that reported lower median family income may currently or in the future feel the impacts of the historical redlining, ability of direct investments, and access to opportunities. For example, such areas as Brownsville and East New York have been facing these problems; their present state of economic development also cannot be considered rosy.
      - **Access to Education and Employment**: This can make higher income areas to have better education facilities and employment so as to meet the demands of the community. On the other hand, there may be lack of proper education facilities and job opportunities in that area, hence the population remains in the same status of poverty.
      - **Housing and Living Costs**: May be the regions with higher cost of living would of course have higher median family incomes, as only well-off families can afford to live there. However, there may be the areas of comparatively low living costs where the majority of families could be sedentary renters with low income, distorting the median income levels.

    #### Application in Food Desert Analysis and Health Implications:
    - **Correlation with Health Outcomes**: They can be explained by poor access to healthy food among people with low income living in failing areas and experience high rates of obesity, diabetes, high blood pressure. The management of income differences can therefore be seen to have a favourable effect on public health.
    - **Community-Based Solutions**: To reduce the food desert problem at the community level Pico-projects like community gardens, farmer’s markets as well as cooperative grocery stores can be adopted in order to quickly solve the issue. These initiatives apart from enhancing uptake of nutritional foods also enhance participates’ participation and ability to bear with the situation.
    - **Partnerships with Retailers**: These measures advocate for substantial grocery retailers to commence selling their products in areas that currently lack such firms through incentives that get rid of the food desert. PPPs are the most efficient in fight against food deserts.

    #### Further Insights:
    - **Economic Development Programs**: Programs that illustrate policy based on economic development considerations should pay especial emphasis on employment opportunities for the citizens, education, and housing in the lower-income districts. These initiatives can assist help economically disadvantaged areas rise and improve.
    - **Infrastructure and Public Services**: Opp. Spending on public transport, health, education and other social infrastructure amenities can go a long way in uplifting the living standards of the less affluent neighbourhoods. Those places can also be improved by making sure that they are well served with transport links for employment.
    - **Support for Local Businesses**: Supporting local entrepreneurship that can be done through issuing grants, offering credits or simply providing training will help activate lower income districts. Promoting small business can foster employment and also can work as a catalyst to financial stability.

    #### Conclusion:
    Using median family income data, we dissect Brooklyn’s tracts and established considerable differences that call for interventions. Redressing these imbalances through serious, inclusive economic development deploys for people, effective, quality public services, community development projects, etc. can meanwhile revolutionize the quality of lives of the affected populations. Also, investing in the priority areas known as food deserts can increase associated access of healthy food items and therefore benefit health of a nation’s people. This analysis can act as an important guide for policy makers, researchers and communal leaders who are involved in the process of striving for economic and social justice in Brooklyn.
    """)

# Main function to create the app
def main():
    st.sidebar.title("Navigation")
    page_icons = {
        "Home": "🏠",
        "Data Analysis": "📊",
        "Data Visualization": "📈",
        "Comments": "💬",
        "Guide": "📖",
        "Food Policy Reports": "📄"
    }

    pages = ["Home", "Data Analysis", "Data Visualization", "Comments", "Guide", "Food Policy Reports"]
    selection = st.sidebar.radio("Go to", pages, format_func=lambda page: f"{page_icons[page]} {page}")

    st.title(selection)

    if selection == "Home":
        st.write("Welcome to the Food Desert Analysis App")
        st.write("This app helps to analyze food desert regions in Brooklyn.")
    
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

    elif selection == "Comments":
        st.write("Leave your comments here:")
        st.text_area("Comments:")

    elif selection == "Guide":
        st.write("How to use the app content goes here.")

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

if __name__ == "__main__":
    main()

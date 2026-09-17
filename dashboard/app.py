"""
AHADI Technical Assessment Dashboard.
Interactive Streamlit UI for exploring Kenya demographic projections.
"""
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Kenya Demographics Explorer", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    csv_path = os.path.join("data", "processed", "kenya_population_by_county.csv")
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    return pd.read_csv(csv_path)

@st.cache_data
def load_geojson():
    geojson_path = os.path.join("data", "raw", "gadm41_KEN_2.json")
    if not os.path.exists(geojson_path):
        return None
    # Dissolve subcounties into single county polygons so the full map renders
    gdf = gpd.read_file(geojson_path)
    county_col = 'NAME_1' if 'NAME_1' in gdf.columns else 'NAME_2'
    gdf_dissolved = gdf.dissolve(by=county_col).reset_index()
    return json.loads(gdf_dissolved.to_json())

df = load_data()
geojson = load_geojson()

if df.empty:
    st.warning("Data not found. Please run the ETL pipeline first.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")
selected_year = st.sidebar.selectbox("Year", sorted(df['year'].unique(), reverse=True))
selected_county = st.sidebar.selectbox("County (Optional)", ["All"] + sorted(df['county'].unique().tolist()))

indicators = {
    "Total Population": "total_population",
    "Children Under 5": "children_under_5",
    "Elderly 65+": "elderly_65plus",
    "Dependency Ratio": "dependency_ratio",
    "Child Dependency Ratio": "child_dependency_ratio",
    "Elderly Dependency Ratio": "elderly_dependency_ratio",
    "Sex Ratio": "sex_ratio"
}
selected_indicator_label = st.sidebar.selectbox("Map Indicator", list(indicators.keys()))
selected_indicator_col = indicators[selected_indicator_label]

# Filter dataset
df_filtered = df[df['year'] == selected_year]

# --- HEADER KPIs (WEIGHTED CALCULATIONS) ---
if selected_county == "All":
    tot_pop = df_filtered['total_population'].sum()
    tot_children = df_filtered['children_under_5'].sum()
    tot_working = df_filtered['working_age'].sum()
    tot_elderly = df_filtered['elderly_65plus'].sum()
    
    kpi_tot_pop = tot_pop
    kpi_dep_ratio = ((tot_children + tot_elderly) / tot_working * 100) if tot_working > 0 else 0
    kpi_children = tot_children
    kpi_pct_children = (tot_children / tot_pop * 100) if tot_pop > 0 else 0
    kpi_elderly = tot_elderly
    kpi_pct_elderly = (tot_elderly / tot_pop * 100) if tot_pop > 0 else 0
    kpi_sex_ratio = df_filtered['sex_ratio'].mean()
    
    pyramid_pop = {'elderly': tot_elderly, 'working': tot_working, 'children': tot_children}
else:
    row = df_filtered[df_filtered['county'] == selected_county].iloc[0]
    kpi_tot_pop = row['total_population']
    kpi_dep_ratio = row['dependency_ratio']
    kpi_children = row['children_under_5']
    kpi_pct_children = row['pct_children']
    kpi_elderly = row['elderly_65plus']
    kpi_pct_elderly = row['pct_elderly']
    kpi_sex_ratio = row['sex_ratio']
    
    pyramid_pop = {'elderly': row['elderly_65plus'], 'working': row['working_age'], 'children': row['children_under_5']}

st.title(f"Kenya Population Demographics ({selected_year})")
st.markdown("Explore age-structure and dependency metrics for public health resource allocation.")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Population", f"{kpi_tot_pop:,.0f}")
col2.metric("Dependency Ratio", f"{kpi_dep_ratio:.1f}")
col3.metric("Children (<5)", f"{kpi_children:,.0f}", f"{kpi_pct_children:.1f}% of total")
col4.metric("Elderly (65+)", f"{kpi_elderly:,.0f}", f"{kpi_pct_elderly:.1f}% of total")
col5.metric("Sex Ratio", f"{kpi_sex_ratio:.1f}")

st.divider()

# --- MAIN VISUALIZATIONS ---
map_col, chart_col = st.columns([3, 2])

with map_col:
    st.subheader(f"{selected_indicator_label} by County")
    if geojson:
        color_scale = "RdYlBu_r" if "ratio" in selected_indicator_col else "Viridis"
        
        fig_map = px.choropleth_map(
            df_filtered,
            geojson=geojson,
            locations='county',
            featureidkey="properties.NAME_1",
            color=selected_indicator_col,
            color_continuous_scale=color_scale,
            map_style="carto-positron",
            zoom=5.0, center={"lat": 0.0236, "lon": 37.9062},
            opacity=0.75,
            hover_name="county",
            hover_data=["total_population", "dependency_ratio", "pct_children"]
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.error("GeoJSON boundaries not found.")

with chart_col:
    st.subheader("Demographic Structure (3-Tier Pyramid)")
    structure_data = pd.DataFrame({
        'Age Group': ['Elderly (65+)', 'Working Age (15-64)', 'Children (<5)'],
        'Population': [pyramid_pop['elderly'], pyramid_pop['working'], pyramid_pop['children']]
    })
    fig_bar = px.bar(structure_data, x='Population', y='Age Group', orientation='h', color='Age Group')
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Top 5 Counties Comparison")
    top_5 = df_filtered.nlargest(5, selected_indicator_col)
    fig_comp = px.bar(top_5, x='county', y=selected_indicator_col, color=selected_indicator_col, color_continuous_scale="Viridis")
    st.plotly_chart(fig_comp, use_container_width=True)

# --- PUBLIC HEALTH CONTEXT ---
st.divider()
st.subheader("Interpretation & Public Health Context")
st.markdown("""
**Dependency Ratios & Resource Allocation:**
* **High Child Population (Dependency):** Counties with elevated `pct_children` and `child_dependency_ratio` require direct prioritization for pediatric care, routine immunizations (measles, pentavalent), and maternal health services.
* **Aging Populations:** Counties showing increased `pct_elderly` signify demographic shifts requiring health systems to scale chronic disease management (hypertension, diabetes) and geriatric services.
* **Economic Implications:** High overall `dependency_ratio` indicates a smaller working-age economic base supporting dependents, placing structural pressure on county-level health financing and universal health coverage schemes (SHIF).

**Policy Recommendations:**
1. **Demographic-Stratified Supply Chains:** Direct essential medicine allocation based on cohort-specific headcounts rather than aggregate population totals alone.
2. **Community Health Strategy:** Deploy and upskill Community Health Promoters (CHPs) tailored to county demographic profiles (e.g., growth monitoring in child-heavy counties vs. NCD screening in aging counties).
""")
# main.py for Tapiwa Mhondiwa - Bakers Inn Offline Despatch KPI Dashboard
# Author: Tapiwa Mhondiwa
# Description: Local Streamlit dashboard with sidebar logo, navigation, date/area/route filters, KPIs, charts, and tables

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: black;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIG ---
st.set_page_config(page_title="Bakers Inn Despatch Dashboard", layout="wide")

# --- SIDEBAR ---
st.sidebar.image("bakers Inn logo.png", use_container_width=True)
page = st.sidebar.radio("Navigate", ["Summary Page", "Bread SKUs", "Biscuits & Loading Compliance"])

# --- LOAD DATA ---
orders_df = pd.read_excel("JUNE 2025 ORDERS CONSOLIDATED.xlsx", sheet_name="Orders")
despatch_df = pd.read_excel("2025 June Superlinx Daily Despatch Tracker.xlsx", sheet_name="Template")
date_index_df = pd.read_excel("DATE INDEX.xlsx", sheet_name="Sheet2")

# --- DATA CLEANING ---
for df in [orders_df, despatch_df, date_index_df]:
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

# --- FILTERS ---
st.sidebar.subheader("Filters")
# Date Filter
date_option = st.sidebar.selectbox("Select Date Filter", ["Daily", "Monthly"])
if date_option == "Daily":
    selected_date = st.sidebar.date_input("Select Date", datetime.today())
    filtered_index = date_index_df[date_index_df['DATE'] == pd.to_datetime(selected_date)]
else:
    months = date_index_df['MONTH'].dropna().unique()
    selected_month = st.sidebar.selectbox("Select Month", months)
    filtered_index = date_index_df[date_index_df['MONTH'] == selected_month]

# Route Filter
routes = date_index_df['ROUTE'].dropna().unique()
selected_routes = st.sidebar.multiselect("Select Routes", routes, default=list(routes))

# Area Filter
areas = orders_df['AREA'].dropna().unique()
selected_areas = st.sidebar.multiselect("Select Areas", areas, default=list(areas))

# --- MERGE DATA ---
filtered_links = filtered_index[filtered_index['ROUTE'].isin(selected_routes)]['LINK']
orders_filtered = orders_df[(orders_df['LINK'].isin(filtered_links)) & (orders_df['AREA'].isin(selected_areas))]
despatch_filtered = despatch_df[despatch_df['LINK'].isin(filtered_links)]

# --- KPI Calculations ---
bread_columns = ['BI White', 'BI Brown', 'BI Whole Wheat', 'Mr Chingwa', 'Mrs Chingwa', 'Dr Chingwa']
biscuit_columns = ['MUNCHIE COOKIES 150G', 'MUNCHIE COOKIES 1KG', 'MUNCHIE COOKIES 2KG']

if page == "Summary Page":
    st.title("📊 Bakers Inn Despatch Summary Dashboard")

    total_orders = orders_filtered[bread_columns].sum().sum()
    total_loaded = despatch_filtered[bread_columns].sum().sum()
    dc_percent = (despatch_filtered['DEPARTURE COMPLIANCE STATUS'].eq("On-time").mean()) * 100
    order_fill = (total_loaded / total_orders * 100) if total_orders > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{int(total_orders):,}")
    col2.metric("Total Loaded", f"{int(total_loaded):,}")
    col3.metric("Departure Compliance %", f"{dc_percent:.1f}%")
    col4.metric("Order Fill %", f"{order_fill:.1f}%")

    # Product Mix %
    product_mix = orders_filtered[bread_columns].sum()
    fig_mix = px.pie(values=product_mix.values, names=product_mix.index, title="Product Mix %")
    st.plotly_chart(fig_mix, use_container_width=True)

    # Bar Chart by SKU
    sku_df = pd.DataFrame({
        'SKU': bread_columns,
        'Ordered': [orders_filtered[col].sum() for col in bread_columns],
        'Loaded': [despatch_filtered[col].sum() for col in bread_columns]
    })
    fig_bar = px.bar(sku_df, x='SKU', y=['Ordered', 'Loaded'], barmode='group', title="Orders vs Loaded by SKU")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Table by Area
    area_table = orders_filtered.groupby('AREA')[bread_columns].sum().sum(axis=1).reset_index(name='Total Ordered')
    area_table['Total Loaded'] = despatch_filtered.groupby('AREA')[bread_columns].sum().sum(axis=1).reindex(area_table['AREA']).values
    area_table['Variance'] = area_table['Total Ordered'] - area_table['Total Loaded']
    st.dataframe(area_table)

elif page == "Bread SKUs":
    st.title("🍞 Bread SKUs Performance")
    st.write("Analysis of Bakers Bread and Chingwa Brands.")
    sku_df = pd.DataFrame({
        'SKU': bread_columns,
        'Ordered': [orders_filtered[col].sum() for col in bread_columns],
        'Loaded': [despatch_filtered[col].sum() for col in bread_columns]
    })
    fig_bread = px.bar(sku_df, x='SKU', y=['Ordered', 'Loaded'], barmode='group', title="Bread SKUs Ordered vs Loaded")
    st.plotly_chart(fig_bread, use_container_width=True)
    st.dataframe(sku_df)

elif page == "Biscuits & Loading Compliance":
    st.title("🍪 Biscuits & Loading Compliance")

    # Biscuits Analysis
    biscuits_df = pd.DataFrame({
        'SKU': biscuit_columns,
        'Ordered': [orders_filtered[col].sum() for col in biscuit_columns],
        'Loaded': [despatch_filtered[col].sum() for col in biscuit_columns]
    })
    fig_biscuit = px.bar(biscuits_df, x='SKU', y=['Ordered', 'Loaded'], barmode='group', title="Biscuits Ordered vs Loaded")
    st.plotly_chart(fig_biscuit, use_container_width=True)
    st.dataframe(biscuits_df)

    # Loading Compliance
    compliance_counts = despatch_filtered['LOADING COMPLIANCE STATUS'].value_counts()
    fig_compliance = px.pie(values=compliance_counts.values, names=compliance_counts.index, title="Loading Compliance Distribution")
    st.plotly_chart(fig_compliance, use_container_width=True)

st.markdown("---")
st.caption("✅ Bakers Inn Automated Despatch Dashboard | WRL Project - Tapiwa Mhondiwa")
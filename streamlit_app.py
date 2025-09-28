#-----------------------------------------------------------------------------------------------------
# Call library, esp. streamlit
#-----------------------------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np #number

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

import requests
from io import StringIO

import warnings
warnings.filterwarnings('ignore')

#-----------------------------------------------------------------------------------------------------
# --- Page configuration
#-----------------------------------------------------------------------------------------------------
st.set_page_config(
   page_title="Telco Customer Churn Analysis", # @browser
   page_icon="📊",
   layout="wide",
   initial_sidebar_state="expanded"
)

#-----------------------------------------------------------------------------------------------------
# Retrieve the data: Telco_customer_churn.csv @github
#-----------------------------------------------------------------------------------------------------
@st.cache_data # to enhance performance
def load_data():
    url = "https://raw.githubusercontent.com/daudrusyadnurdin/marketing-analysis/master/Telco_customer_churn.csv"
    return pd.read_csv(url)

df = load_data()

# Special case: handling data type conversion
df['Total Charges'] = pd.to_numeric(df['Total Charges'], errors='coerce')

#-----------------------------------------------------------------------------------------------------
# App banner and title & description
#-----------------------------------------------------------------------------------------------------

# Gambar header dari GitHub (RAW URL)
header_image_url = "https://raw.githubusercontent.com/daudrusyadnurdin/marketing-analysis/master/telco-business.jpg"
st.image(header_image_url, use_container_width=True)

st.title("📊 Telco Customer Churn Analysis")
st.markdown("""
            The telecommunications industry is highly competitive, making customer churn a particular concern, 
            given the increasingly high cost of acquiring new customers. 
            Companies strive to reduce this churn rate as much as possible, thereby increasing cost efficiency. 
            The following is a simulation of a churn analysis for a telecommunications company in California, USA.
""")

#-----------------------------------------------------------------------------------------------------
# Filtering parameter
#-----------------------------------------------------------------------------------------------------
# Sidebar filters
st.sidebar.header("Filtering parameters")

# Geographic filters
flt_city = st.sidebar.multiselect("City", 
                                    options=df['City'].unique()
                                 )

# Demographic filters
flt_gender = st.sidebar.multiselect("Gender", 
                                       options=df['Gender'].unique()
                                    )
flt_sr_citizen = st.sidebar.multiselect("Senior Citizen", 
                                          options=df['Senior Citizen'].unique()
                                       )

# Tenure months range
min_tenure, max_tenure = int(df['Tenure Months'].min()), int(df['Tenure Months'].max())
rg_tenure = st.sidebar.slider(
    "Tenure Months",
    min_value=min_tenure,
    max_value=max_tenure,
    value=(min_tenure, max_tenure)
)

# Monthly charges range
min_monchrg, max_monchrg = float(df['Monthly Charges'].min()), float(df['Monthly Charges'].max())
rg_monthly_charges = st.sidebar.slider(
    "Monthly Charges ($)",
    min_value=min_monchrg,
    max_value=max_monchrg,
    value=(min_monchrg, max_monchrg)
)

#-----------------------------------------------------------------------------------------------------
# Select the data based on filtering parameters
#-----------------------------------------------------------------------------------------------------
df_selected = df.copy()

# Apply multiselect filters only if a selection has been made for that filter
# City, Gender & Senior Citizen
if flt_city:
   df_selected = df_selected[df_selected["City"].isin(flt_city)]
if flt_gender:
   df_selected = df_selected[df_selected["Gender"].isin(flt_gender)]
if flt_sr_citizen:
   df_selected = df_selected[df_selected["Senior Citizen"].isin(flt_sr_citizen)]

# Always apply the slider filter
# Tenure
df_selected = df_selected[
   (df_selected["Tenure Months"] >= rg_tenure[0]) &
   (df_selected["Tenure Months"] <= rg_tenure[1])
]
# Monthly Charges
df_selected = df_selected[
   (df_selected["Monthly Charges"] >= rg_monthly_charges[0]) &
   (df_selected["Monthly Charges"] <= rg_monthly_charges[1])
]

# Display error message if no data is selected
if df_selected.empty:
   st.warning("No data available for the selected filters. Please adjust your selection.")
   st.stop() # Halts the app execution

#-----------------------------------------------------------------------------------------------------
# Dashboard & reporting
#-----------------------------------------------------------------------------------------------------
#-------------------------------------
# KPI
#-------------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_customers = len(df_selected)
churn_customers = df_selected['Churn Label'].value_counts().get('Yes', 0)
total_revenue = df_selected['Total Charges'].sum()
churn_revenue = df_selected[df_selected['Churn Label'] == 'Yes']['Total Charges'].iloc[0] if 'Yes' in df_selected['Churn Label'].values else 0

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Total Churn", f"{churn_customers:,}")
with col3:
    st.metric("Churn Rate", f"{(churn_customers/total_customers)*100:.1f}%")
with col4:
    st.metric("Total Revenue", f"${total_revenue:,.0f}")
with col5:
    st.metric("Revenue at Risk", f"${churn_revenue:,.0f}")
with col6:
    st.metric("% Revenue at Risk", f"{(churn_revenue/total_revenue)*100:.4f}%")

st.markdown("---")

#-------------------------------------
# Churn reason
#-------------------------------------
st.subheader("📊 Total Churn by Reason in California - USA")

# --- Buat Figure ---
fig, ax = plt.subplots(figsize=(12, 9))  

# --- Data ---
df_cr = (
    df_selected.groupby("Churn Reason")["Churn Value"]
      .sum()
      .reset_index()
      .sort_values(by="Churn Value")
)

# --- Plot Horizontal Bar ---
ax.barh(
    df_cr["Churn Reason"],
    df_cr["Churn Value"],
    color=[
        'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey',
        'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey',
        'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey', 'lightgrey',
        'lightgrey', 'lightgrey', 'lightsalmon', 'salmon', 'tomato'
    ]
)

# --- Judul & Label ---
ax.set_ylabel("Churn Reason")
ax.set_xlabel("Total Churn")

# --- Grid & Style ---
ax.grid(axis="x", ls="--", color="lavender")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()

# --- Tampilkan di Streamlit ---
st.pyplot(fig)


#---------------------------------------------
# Dashboard and report
#---------------------------------------------
# Define consistent chart size for columns
# CHART_WIDTH = 6
# CHART_HEIGHT = 5
# CHART_SIZE = (CHART_WIDTH, CHART_HEIGHT)

# viz_col1, viz_col2 = st.columns(2)

# with viz_col1:
#     st.subheader("👥 Customer Churn Distribution")
    
#     # Pie Chart
#     fig1, ax1 = plt.subplots(figsize=CHART_SIZE)
    
#     churn_counts = df['Churn Label'].value_counts()
    
#     # Pie chart dengan styling yang better
#     colors = ['#2ecc71', "#e7e43c"]  # Green for No Churn, Red for Churn
#     explode = (0, 0.05)  # Mild explode untuk emphasis
    
#     wedges, texts, autotexts = ax1.pie(
#         churn_counts.values,
#         labels=churn_counts.index,
#         autopct='%1.1f%%',
#         startangle=90,
#         colors=colors,
#         explode=explode,
#         textprops={'fontsize': 9}
#     )
    
#     # Improve text styling
#     for autotext in autotexts:
#         autotext.set_color('white')
#         autotext.set_fontweight('bold')
#         autotext.set_fontsize(8)
    
#     st.pyplot(fig1, use_container_width=True)

# with viz_col2:
#     st.subheader("💰 Revenue Impact")
    
#     # Bar Chart
#     fig2, ax2 = plt.subplots(figsize=CHART_SIZE)
    
#     colors_bar = ['#2ecc71', '#e74c3c']  # Same color scheme as pie chart
    
#     bars = ax2.bar(
#         df_bar_chrn['Churn Label'],
#         df_bar_chrn['Total Charges'] / 1000,
#         color=colors_bar,
#         width=0.6,
#         alpha=0.8,
#         edgecolor='black',
#         linewidth=0.5
#     )
    
#     # Styling
#     ax2.set_xlabel("Churn Status", fontsize=10, fontweight='bold')
#     ax2.set_ylabel("Total Charges ($ Thousands)", fontsize=10, fontweight='bold')
    
#     # Grid and annotations
#     ax2.grid(axis='y', alpha=0.3, linestyle='--')
#     ax2.set_axisbelow(True)
    
#     # Annotations dengan positioning yang better
#     max_value = df_bar_chrn['Total Charges'].max() / 1000
#     for bar in bars:
#         height = bar.get_height()
#         ax2.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.03,
#                 f'${height:,.0f}K', 
#                 ha='center', va='bottom', 
#                 fontweight='bold', fontsize=9,
#                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
#     # Remove spines dan adjust layout
#     for spine in ['top', 'right']:
#         ax2.spines[spine].set_visible(False)
    
#     # Adjust y-axis limit untuk space annotations
#     ax2.set_ylim(0, max_value * 1.15)
    
#     plt.tight_layout()
#     st.pyplot(fig2, use_container_width=True)


#-----------------------------------------------------------------------------------------------------
# --- Display sample of raw data
#-----------------------------------------------------------------------------------------------------
with st.expander("View Sample of Raw Data"):
   st.dataframe(df)
   st.markdown(f"**Data Dimensions:** {df.shape[0]} rows, {df.shape[1]} columns")


#-----------------------------------------------------------------------------------------------------
# Some additional information of this work
#-----------------------------------------------------------------------------------------------------
st.markdown("---")
st.write("Data Source: [Telco Customer Churn Dataset](https://github.com/daudrusyadnurdin/marketing-analysis)")
st.write("") 
st.write("This assignment was created with reference to the previous assignment, namely: " \
         "**Day 13 - Fundamentals of Data Visualization**, with several modifications adapted to the environment in Streamlit. "\
         "Based on the dataset's structure, no date information was found. This data represents a snapshot of customer status (churn/non-churn) at a telco company in California, USA."
         )

#---The End-------------------------------------------------------------------------------------------

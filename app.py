import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import random
import time

from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------
# Streamlit Page Configuration
# ----------------------------------------------.-----
st.set_page_config(
    page_title="Titanic A/B Testing🚢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------
# Title & Brief Introduction
# ---------------------------------------------------
st.title("Titanic A/B Testing Experiment 🚢")

st.markdown("""
My app conducts an A/B testing experiment using the **Titanic** dataset. 
The objective is to find out which chart better helps answer the core question.
""")

# ---------------------------------------------------
# Business Question
# ---------------------------------------------------
business_question = (
    "Which combination of passenger class and gender is most strongly associated with higher survival rates?"
)
st.subheader("Business Question")
st.markdown(f"{business_question}")

# ---------------------------------------------------
# Data Loading Function (Using st.connection)
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    try:
        # Create a connection to the Google Sheet
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Fetch the spreadsheet ID from secrets instead of hardcoding
        spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]

        # Read the data using that secret ID
        data = conn.read(spreadsheet=spreadsheet_id)
        st.success("Data successfully loaded from Google Sheet using secrets!")
    except Exception as e:
        st.warning("Error loading Google Sheet. Falling back to Seaborn's Titanic dataset.")
        st.warning(f"**Error details**: {e}")
        data = sns.load_dataset('titanic')
    return data


data = load_data()

# ---------------------------------------------------
# Chart Definitions
# ---------------------------------------------------
def chart1(data):
    """
    Chart 1: Survival Rate by Passenger Class and Gender
    """
    survival_rate = data.groupby(['pclass', 'sex'])['survived'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='pclass', y='survived', hue='sex', data=survival_rate, palette="Set2", ax=ax)
    ax.set_title("Survival Rate by Passenger Class and Gender", fontsize=14, fontweight='bold')
    ax.set_xlabel("Passenger Class", fontsize=12)
    ax.set_ylabel("Survival Rate", fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    plt.tight_layout()
    return fig

def chart2(data):
    """
    Chart 2: Heatmap of Survival Rate by Passenger Class and Gender
    """
    pivot_data = data.pivot_table(values='survived', index='pclass', columns='sex', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        pivot_data, annot=True, cmap="YlGnBu", fmt=".2f", 
        cbar_kws={'label': 'Survival Rate'}, ax=ax
    )
    ax.set_title("Heatmap of Survival Rate by Passenger Class and Gender", fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

# ---------------------------------------------------
# Session State Initialization
# ---------------------------------------------------
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'chart_displayed' not in st.session_state:
    st.session_state.chart_displayed = False
if 'selected_chart' not in st.session_state:
    st.session_state.selected_chart = None
if 'answered' not in st.session_state:
    st.session_state.answered = False

# ---------------------------------------------------
# Instructions Section
# ---------------------------------------------------
st.header("Experiment Instructions")
st.markdown("""
1. Click **"Show a chart"** to randomly display one of the two charts.
2. Study the chart to answer the business question.
3. When you're ready, click **"I answered your question"** to record your response time.
""")

# ---------------------------------------------------
# Show Chart Button
# ---------------------------------------------------
if not st.session_state.chart_displayed:
    if st.button("Show a chart", type="primary"):
        st.session_state.start_time = time.time()
        st.session_state.selected_chart = random.choice(['chart1', 'chart2'])
        st.session_state.chart_displayed = True
        st.rerun()

# ---------------------------------------------------
# Display the Selected Chart & Response Timing
# ---------------------------------------------------
if st.session_state.chart_displayed and st.session_state.selected_chart:
    st.subheader("Your Randomly Selected Chart")
    
    if st.session_state.selected_chart == 'chart1':
        st.pyplot(chart1(data))
    else:
        st.pyplot(chart2(data))
    
    # Handle "I answered..." button
    if not st.session_state.answered:
        if st.button("I answered your question"):
            if st.session_state.start_time:
                st.session_state.elapsed_time = time.time() - st.session_state.start_time
            else:
                st.error("Start time not recorded. Please try again.")
            st.session_state.answered = True  # Set answered to True regardless
    
    # Display success message and "Go Back" button if answered
    if st.session_state.answered:
        if hasattr(st.session_state, 'elapsed_time') and st.session_state.elapsed_time is not None:
            st.success(f"**It took you {st.session_state.elapsed_time:.2f} seconds to answer the question!**")
        
        # Display Go Back button
        if st.button("Go Back"):
            # Reset all states
            st.session_state.chart_displayed = False
            st.session_state.start_time = None
            st.session_state.selected_chart = None
            st.session_state.answered = False
            if hasattr(st.session_state, 'elapsed_time'):
                del st.session_state.elapsed_time
            st.rerun()

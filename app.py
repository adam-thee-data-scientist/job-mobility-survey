import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

h# %% [1] PAGE CONFIG & CSS
st.set_page_config(
    page_title="AI Research Portfolio",
    layout="centered"
)

# Refined CSS: This forces the radio buttons to be perfectly centered in 5 equal columns
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Force the radio group to distribute its 5 options exactly like a table row */
    div[role="radiogroup"] {
        display: flex;
        justify-content: space-between;
        width: 100% !important;
        gap: 0px;
    }
    div[role="radiogroup"] > label {
        flex: 1; /* Each label takes exactly 20% width */
        justify-content: center;
        margin: 0px !important;
    }
    /* Align the question text vertically with the dots */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION (Same as your code)
conn = st.connection("gsheets", type="gsheets")

# %% [3] UPGRADE 1: TABULAR MATRIX UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):
    # We use a [3, 5] ratio. 3 for the question, 5 for the response area.
    
    # --- 1. THE HEADER ROW ---
    # We create a single container for headers to match the radio group width
    h_col1, h_col2 = st.columns([3, 5])
    with h_col2:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; text-align: center; margin-bottom: -15px;">
            <div style="flex: 1; font-weight: bold; font-size: 11px;">Strongly<br>Disagree</div>
            <div style="flex: 1; font-weight: bold; font-size: 11px;">Somewhat<br>Disagree</div>
            <div style="flex: 1; font-weight: bold; font-size: 11px;">Neither</div>
            <div style="flex: 1; font-weight: bold; font-size: 11px;">Somewhat<br>Agree</div>
            <div style="flex: 1; font-weight: bold; font-size: 11px;">Strongly<br>Agree</div>
        </div>
        """, unsafe_allow_html=True)

    # --- 2. THE QUESTION ROWS ---
    questions = [
        "I feel confident identifying when an AI-generated output is factually incorrect.",
        "My current core technical skills will remain relevant for the next 3 years.",
        "I use AI for tasks not explicitly part of my official job description."
    ]
    
    responses = []
    for q_idx, q_text in enumerate(questions):
        st.divider() # Optional: Adds a subtle "table line" between questions
        r_col1, r_col2 = st.columns([3, 5])
        with r_col1:
            st.write(q_text)
        with r_col2:
            selection = st.radio(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                key=f"q_{q_idx}",
                horizontal=True,
                label_visibility="collapsed"
            )
            responses.append(selection)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Submit Response")

# %% [4] LOGIC (Keep your existing GSheets logic here)
if submitted:
    # ... your existing logic to save data ...
    st.success("Success!")

# %% [5] DATA VISUALIZATION & DOWNLOAD
st.divider()
st.header("Real-time Results")

try:
    # TTL set to 600 seconds (10 mins) for automatic updates
    data = conn.read(worksheet="Sheet1", ttl=600)
    
    if not data.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Responses", len(data))
        col2.metric("Avg Trust Score", round(data['trust_score'].mean(), 1))
        col3.metric("Avg Skill Confidence", round(data['skill_score'].mean(), 1))
        
        st.bar_chart(data['level'].value_counts())
        
        # Download Data Button
        st.subheader("Export Research Data")
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Responses as CSV",
            data=csv,
            file_name=f"survey_results_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("The sheet is empty. Be the first to submit!")
except Exception as e:
    st.warning("Connect your Google Sheet to see results here.")
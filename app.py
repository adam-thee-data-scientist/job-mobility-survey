import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & CSS
st.set_page_config(
    page_title="AI Research Portfolio",
    layout="centered"
)

# Refined CSS for perfect alignment
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* This forces the 5 radio options to each take up exactly 1/5th of the row */
            div[role="radiogroup"] {
                display: flex;
                width: 100% !important;
                justify-content: space-around;
            }
            div[role="radiogroup"] > label {
                flex: 1;
                justify-content: center;
                display: flex;
            }
            /* Removes extra padding that can shift the row */
            div[data-testid="stHorizontalBlock"] {
                align-items: center;
                gap: 0px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# %% [3] UPGRADE 1: TABULAR MATRIX UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):
    headers = ["Strongly Disagree", "Somewhat Disagree", "Neither", "Somewhat Agree", "Strongly Agree"]
    questions = [
        "I feel confident identifying when an AI-generated output is factually incorrect.",
        "My current core technical skills will remain relevant for the next 3 years.",
        "I use AI for tasks not explicitly part of my official job description."
    ]

    # 1. Header Row: Using [3, 1, 1, 1, 1, 1]
    # The '3' is for the question, and the five '1s' are the columns
    h_cols = st.columns([3, 1, 1, 1, 1, 1])
    h_cols[0].write("") 
    for i, header in enumerate(headers):
        h_cols[i+1].markdown(f"<p style='text-align:center; font-size:11px; line-height:1.2;'><b>{header}</b></p>", unsafe_allow_html=True)

    # 2. Question Rows: Using [3, 5]
    # The '5' perfectly covers the same space as the five '1s' above
    responses = []
    for q_idx, q_text in enumerate(questions):
        r_cols = st.columns([3, 5]) 
        r_cols[0].markdown(f"<div style='font-size:14px; padding-top:10px;'>{q_text}</div>", unsafe_allow_html=True)
        
        with r_cols[1]:
            selection = st.radio(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                key=f"q_{q_idx}",
                horizontal=True,
                label_visibility="collapsed"
            )
        responses.append(selection)

    st.markdown("<br>", unsafe_allow_html=True) # Adds a little space before button
    submitted = st.form_submit_button("Submit Response")

# %% [4] UPGRADE 1: LOGIC
if submitted:
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # Ensure these keys match your Google Sheet column headers exactly
        "trust_score": responses[0],
        "skill_score": responses[1],
        "adoption_score": responses[2]
    }
    
    try:
        # Use the connection to add the data
        conn.create(worksheet="Sheet1", data=[new_entry])
        st.success("Data recorded successfully!")
        st.balloons()
    except Exception as e:
        st.error(f"Error: {e}")

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
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Forces the radio buttons and headers to use the same 5-column grid */
            div[role="radiogroup"], .header-container {
                display: grid !important;
                grid-template-columns: repeat(5, 1fr);
                width: 100%;
                gap: 0px;
            }
            
            /* Centers the dots and the text labels */
            div[role="radiogroup"] > label, .header-item {
                justify-content: center;
                display: flex;
                text-align: center;
                align-items: center;
            }
            
            /* Tightens vertical spacing for a table look */
            [data-testid="stVerticalBlock"] {
                gap: 0.5rem;
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

    # 1. Header Row
    # We use a [3, 5] split to match the question rows exactly
    h_cols = st.columns([3, 5])
    h_cols[0].write("") # Empty corner
    
    # We build the 5 headers inside the SECOND column using a single HTML string
    header_html = f"""
    <div class='header-container'>
        {"".join([f"<div class='header-item' style='font-size:11px; font-weight:bold;'>{h}</div>" for h in headers])}
    </div>
    """
    h_cols[1].markdown(header_html, unsafe_allow_html=True)

    # 2. Question Rows
    responses = []
    for q_idx, q_text in enumerate(questions):
        r_cols = st.columns([3, 5]) 
        r_cols[0].markdown(f"<div style='font-size:14px; padding-top:5px;'>{q_text}</div>", unsafe_allow_html=True)
        
        with r_cols[1]:
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
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & CSS
st.set_page_config(
    page_title="AI Research Portfolio",
    layout="centered"
)

# Custom CSS to force the "Table" look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Spreads the radio buttons across the available width */
            div[role="radiogroup"] {
                justify-content: space-between;
                width: 100%;
            }
            /* Centers the radio dots */
            div[data-testid="stHorizontalBlock"] {
                align-items: center;
            }
            </style>
            """
# CRITICAL: This line must be here to activate the CSS!
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

    # 1. Create the Header Row (Question placeholder + 5 labels)
    header_cols = st.columns([2.5, 1, 1, 1, 1, 1])
    header_cols[0].write("") # Empty corner
    for i, header in enumerate(headers):
        header_cols[i+1].markdown(f"<p style='text-align:center; font-size:12px;'><b>{header}</b></p>", unsafe_allow_html=True)

    # 2. Create the Question Rows
    responses = []
    for q_idx, q_text in enumerate(questions):
        # We use [2.5, 5] so the second column spans the space of the 5 headers above
        row_cols = st.columns([2.5, 5]) 
        row_cols[0].write(q_text)
        
        with row_cols[1]:
            selection = st.radio(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                key=f"q_{q_idx}",
                horizontal=True,
                label_visibility="collapsed"
            )
        responses.append(selection)

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
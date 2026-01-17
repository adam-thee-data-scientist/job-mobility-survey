import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & PERSISTENT CSS
st.set_page_config(page_title="AI Research Portfolio", layout="wide")

# This new CSS forces the radio buttons to spread out across the whole column
matrix_style = """
<style>
    /* 1. Hide Streamlit Branding (Per your request) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 2. THE NEW APPROACH: Flexbox Spreading */
    /* This targets the container of the radio dots */
    div[role="radiogroup"] {
        display: flex !important;
        justify-content: space-between !important;
        width: 100% !important;
    }
    
    /* This makes each individual dot/number occupy equal space */
    div[role="radiogroup"] > label {
        flex: 1 !important;
        justify-content: center !important;
        margin-right: 0px !important;
    }

    /* 3. Header Alignment */
    .matrix-header {
        display: flex;
        justify-content: space-between;
        text-align: center;
        margin-bottom: 10px;
    }
    .header-item {
        flex: 1;
        font-weight: bold;
        font-size: 12px;
        line-height: 1.1;
    }
</style>
"""
st.markdown(matrix_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
# Initialize to prevent NameError
submitted = False 

try:
    # FIXED: Using the class GSheetsConnection directly fixes image_9bd5c7.png
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Connection Setup Error: {e}")

# %% [3] MATRIX SURVEY UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):
    # Split: 40% Question, 60% Matrix
    col_q, col_m = st.columns([4, 6])
    
    with col_m:
        # Header Row using Flexbox to match the radio dots
        st.markdown("""
        <div class="matrix-header">
            <div class="header-item">Strongly<br>Disagree</div>
            <div class="header-item">Somewhat<br>Disagree</div>
            <div class="header-item">Neither</div>
            <div class="header-item">Somewhat<br>Agree</div>
            <div class="header-item">Strongly<br>Agree</div>
        </div>
        """, unsafe_allow_html=True)

    questions = [
        "I feel confident identifying when an AI-generated output is factually incorrect.",
        "My current core technical skills will remain relevant for the next 3 years.",
        "I use AI for tasks not explicitly part of my official job description."
    ]
    
    responses = []
    for i, q_text in enumerate(questions):
        st.divider()
        r_col_q, r_col_m = st.columns([4, 6])
        
        with r_col_q:
            st.markdown(f"<div style='padding-top:10px;'>{q_text}</div>", unsafe_allow_html=True)
            
        with r_col_m:
            # The CSS above will now force these dots to spread across the whole 60% width
            choice = st.radio(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                key=f"q_{i}",
                horizontal=True,
                label_visibility="collapsed"
            )
            responses.append(choice)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Submit Response")

# %% [4] SUBMISSION LOGIC
if submitted:
    new_data = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trust_score": responses[0],
        "skill_score": responses[1],
        "adoption_score": responses[2]
    }])
    
    try:
        existing_data = conn.read(worksheet="Sheet1")
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("Success! Responses recorded.")
        st.balloons()
    except Exception as e:
        st.error(f"Submission failed. Check your Sheet connection: {e}")

# %% [5] COMMUNITY RESULTS
st.divider()
st.header("Community Progress")
try:
    data = conn.read(worksheet="Sheet1", ttl=5)
    if not data.empty:
        st.metric("Total Contributors", len(data))
except:
    st.info("Live results will appear once the Google Sheet is linked.")
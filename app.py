import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & PERSISTENT CSS
st.set_page_config(page_title="AI Research Portfolio", layout="wide")

# This CSS forces the radio buttons and headers into a synchronized 5-column grid
matrix_style = """
<style>
    /* 1. Hide Streamlit Branding (Per your request) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 2. The Magic Alignment: Force Radio Buttons into 5 equal columns */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(5, 1fr) !important;
        width: 100% !important;
        gap: 0px !important;
    }
    
    /* Center the radio dot and number within its grid cell */
    div[role="radiogroup"] > label {
        justify-content: center !important;
        align-items: center !important;
        padding: 10px 0px !important;
        margin: 0px !important;
    }

    /* 3. Header Grid: Match the Radio Group exactly */
    .matrix-header {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        text-align: center;
        margin-bottom: 5px;
    }
    .header-label {
        font-weight: bold;
        font-size: 12px;
        line-height: 1.2;
    }
</style>
"""
st.markdown(matrix_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
# FIXED: Using GSheetsConnection class to resolve image_9bd5c7.png error
conn = st.connection("gsheets", type=GSheetsConnection)

# %% [3] MATRIX SURVEY UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):
    # Main layout: 40% for question text, 60% for the matrix area
    col_q, col_m = st.columns([4, 6])
    
    with col_m:
        # Header Row using the CSS grid class defined above
        st.markdown("""
        <div class="matrix-header">
            <div class="header-label">Strongly<br>Disagree</div>
            <div class="header-label">Somewhat<br>Disagree</div>
            <div class="header-label">Neither</div>
            <div class="header-label">Somewhat<br>Agree</div>
            <div class="header-label">Strongly<br>Agree</div>
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
            st.write(f"**{q_text}**")
            
        with r_col_m:
            # The CSS above targets this radio group to spread it across the 5 columns
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
        st.success("Success! Your perspective has been added.")
        st.balloons()
    except Exception as e:
        st.error(f"Sheet Update Failed: {e}")

# %% [5] LIVE RESULTS
st.divider()
st.header("Community Progress")
try:
    data = conn.read(worksheet="Sheet1", ttl=5)
    if not data.empty:
        st.metric("Total Contributors", len(data))
except:
    st.info("Results will appear once the Google Sheet is connected.")
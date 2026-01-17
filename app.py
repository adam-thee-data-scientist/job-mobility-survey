import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & PERSISTENT CSS
st.set_page_config(page_title="AI Research Portfolio", layout="wide")

matrix_style = """
<style>
    /* 1. Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 2. MATRIX GRID ALIGNMENT */

    /* Header row */
    .matrix-header {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        text-align: center;
        font-weight: bold;
        font-size: 12px;
        line-height: 1.1;
        margin-bottom: 10px;
        width: 100%;
    }

    /* Radio button row */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(5, 1fr) !important;
        width: 100% !important;
    }

    /* Individual radio option */
    div[role="radiogroup"] > label {
        justify-content: center !important;
        margin: 0 !important;
    }

    /* Remove Streamlit internal padding */
    div[role="radiogroup"] label > div {
        margin: auto !important;
    }
</style>
"""
st.markdown(matrix_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
submitted = False

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Connection Setup Error: {e}")

# %% [3] MATRIX SURVEY UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):

    # 40% Question / 60% Matrix
    col_q, col_m = st.columns([4, 6])

    # Header row
    with col_m:
        st.markdown("""
        <div class="matrix-header">
            <div>Strongly<br>Disagree</div>
            <div>Somewhat<br>Disagree</div>
            <div>Neither</div>
            <div>Somewhat<br>Agree</div>
            <div>Strongly<br>Agree</div>
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
            st.markdown(
                f"<div style='padding-top:10px;'>{q_text}</div>",
                unsafe_allow_html=True
            )

        with r_col_m:
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

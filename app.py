import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & CSS
st.set_page_config(
    page_title="AI Research Portfolio",
    layout="centered"
)

# REFINED CSS: This locks the radio buttons and headers into a perfect 5-column grid
hide_st_style = """
    <style>
    /* 1. Hide Streamlit Branding (Your request) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 2. Force the Radio Buttons into 5 equal columns */
    /* Target the container that holds the radio options */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(5, 1fr) !important;
        gap: 0px !important;
        width: 100% !important;
    }
    
    /* Center the circle and the number within each grid cell */
    div[role="radiogroup"] > label {
        justify-content: center !important;
        align-items: center !important;
        margin-right: 0px !important;
        padding: 5px 0px !important;
        flex: 1 !important;
    }

    /* 3. Improve vertical alignment for the question text */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
# FIXED: Using the Class 'GSheetsConnection' directly to fix the StreamlitAPIException
conn = st.connection("gsheets", type=GSheetsConnection)

# %% [3] MATRIX SURVEY UI
st.subheader("AI Workplace Sentiment")

with st.form("matrix_survey"):
    # Header Row: We use a [3, 5] ratio. 3 for questions, 5 for the matrix.
    h_col1, h_col2 = st.columns([3, 5])
    with h_col2:
        # We use a matching 5-column grid for the text headers
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); text-align: center; margin-bottom: -10px;">
            <div style="font-weight: bold; font-size: 11px; line-height: 1.1;">Strongly<br>Disagree</div>
            <div style="font-weight: bold; font-size: 11px; line-height: 1.1;">Somewhat<br>Disagree</div>
            <div style="font-weight: bold; font-size: 11px; line-height: 1.1;">Neither</div>
            <div style="font-weight: bold; font-size: 11px; line-height: 1.1;">Somewhat<br>Agree</div>
            <div style="font-weight: bold; font-size: 11px; line-height: 1.1;">Strongly<br>Agree</div>
        </div>
        """, unsafe_allow_html=True)

    questions = [
        "I feel confident identifying when an AI-generated output is factually incorrect.",
        "My current core technical skills will remain relevant for the next 3 years.",
        "I use AI for tasks not explicitly part of my official job description."
    ]
    
    responses = []
    for q_idx, q_text in enumerate(questions):
        st.divider() # Creates a "table line" between questions
        r_col1, r_col2 = st.columns([3, 5])
        with r_col1:
            st.markdown(f"<div style='font-size: 14px;'>{q_text}</div>", unsafe_allow_html=True)
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

# %% [4] SUBMISSION LOGIC
if submitted:
    new_data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "trust_score": [responses[0]],
        "skill_score": [responses[1]],
        "adoption_score": [responses[2]]
    }
    df_new = pd.DataFrame(new_data)
    
    try:
        # Append data to the sheet
        existing_data = conn.read(worksheet="Sheet1")
        updated_df = pd.concat([existing_data, df_new], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("Responses recorded!")
        st.balloons()
    except Exception as e:
        st.error(f"Spreadsheet Error: {e}")

# %% [5] RESULTS VISUALIZATION
st.divider()
st.header("Real-time Results")

try:
    data = conn.read(worksheet="Sheet1", ttl=5)
    if not data.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Responses", len(data))
        if 'trust_score' in data.columns:
            c2.metric("Avg Trust", round(data['trust_score'].mean(), 1))
            c3.metric("Avg Skill", round(data['skill_score'].mean(), 1))
    else:
        st.info("No data yet.")
except:
    st.warning("Connect your Google Sheet to see live results.")
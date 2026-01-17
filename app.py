import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG
st.set_page_config(page_title="AI Research Portfolio", layout="wide")

# Hide Header/Footer (Your persistent request)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    /* Remove vertical padding between rows to make it look like a table */
    .element-container { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
# FIXED: Passing the class GSheetsConnection directly fixes your API error
conn = st.connection("gsheets", type=GSheetsConnection)

# %% [3] THE "DIFFERENT" MATRIX UI
st.subheader("AI Workplace Sentiment")

# Define our column widths once so they are identical for every row
# [4 units for question, 1 unit for each of the 5 options]
widths = [4, 1, 1, 1, 1, 1]

with st.form("matrix_survey"):
    # --- 1. THE HEADER ROW ---
    cols = st.columns(widths)
    labels = ["", "Strongly<br>Disagree", "Somewhat<br>Disagree", "Neither", "Somewhat<br>Agree", "Strongly<br>Agree"]
    
    for i, label in enumerate(labels):
        if label:
            cols[i].markdown(f"<div style='text-align:center; font-weight:bold; font-size:12px; line-height:1;'>{label}</div>", unsafe_allow_html=True)

    st.divider()

    # --- 2. THE QUESTION ROWS ---
    questions = [
        "I feel confident identifying when an AI-generated output is factually incorrect.",
        "My current core technical skills will remain relevant for the next 3 years.",
        "I use AI for tasks not explicitly part of my official job description."
    ]
    
    responses = []
    for q_idx, q_text in enumerate(questions):
        row_cols = st.columns(widths)
        
        # Column 0: The Question
        row_cols[0].write(q_text)
        
        # Columns 1-5: The Radio Buttons (one per column)
        # We use a single radio widget but hide its label to make it look like dots
        with row_cols[1]: # This spans the area of the 5 choices
            # We use an empty container to group the radio button across the remaining columns
            # But since Streamlit widgets can't span multiple columns easily, 
            # we place the radio in a sub-container or use a Select Slider.
            
            # ALTERNATIVE: Use a Select Slider which is 100% aligned by default
            choice = st.select_slider(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                value=3,
                label_visibility="collapsed",
                key=f"q_{q_idx}"
            )
            responses.append(choice)
        
        st.divider()

    submitted = st.form_submit_button("Submit Response")

# %% [4] LOGIC
if submitted:
    new_entry = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trust_score": responses[0],
        "skill_score": responses[1],
        "adoption_score": responses[2]
    }])
    
    try:
        # Append data logic
        existing_data = conn.read(worksheet="Sheet1")
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("Responses Saved!")
    except Exception as e:
        st.error(f"Error: {e}")

# %% [5] RESULTS
try:
    data = conn.read(worksheet="Sheet1", ttl=5)
    if not data.empty:
        st.divider()
        st.metric("Total Responses", len(data))
except:
    pass
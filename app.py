# %% [1] IMPORTS & CONFIGURATION
import streamlit as st
import pandas as pd
from datetime import datetime
# Note: You'll eventually need: pip install gspread
# import gspread 

st.set_page_config(page_title="Research Portfolio", layout="centered")

# %% [2] DATABASE CONNECTION (Updated for Google Sheets)
from streamlit_gsheets import GSheetsConnection

def save_to_database(data_dict):
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read existing data
    existing_data = conn.read(worksheet="Sheet1")
    
    # Add new row
    new_row = pd.DataFrame([data_dict])
    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
    
    # Write back to Google Sheets
    conn.update(worksheet="Sheet1", data=updated_df)

# %% [3] SURVEY UI (The "Frontend")
st.title("📊 The Evolution of Research Careers")
st.write("Testing the survey flow and logic.")

with st.form("main_survey"):
    role = st.selectbox(
        "Current Industry Role",
        ["Data Entry", "Analyst", "Research Manager", "Executive", "Other"]
    )
    
    tools = st.multiselect(
        "Core Tech Stack",
        ["Excel", "Python", "R", "Qualtrics", "Tableau"]
    )
    
    ai_sentiment = st.select_slider(
        "AI Impact Sentiment (1=Low, 5=High)",
        options=[1, 2, 3, 4, 5]
    )
    
    contact = st.text_input("LinkedIn URL (Optional)")
    
    submitted = st.form_submit_button("Submit Response")

# %% [4] LOGIC & POST-SUBMISSION FLOW
if submitted:
    # Prepare data
    entry = {
        "timestamp": datetime.now(),
        "role": role,
        "tools": ", ".join(tools),
        "sentiment": ai_sentiment,
        "link": contact
    }
    
    # Save it
    save_to_database(entry)
    st.success("Data recorded successfully!")
    
    # Logic: Show follow-up only if sentiment is high
    if ai_sentiment >= 4:
        st.info("Since you are optimistic about AI, keep an eye on your LinkedIn inbox for our AI focus group!")

# %% [5] DATA VISUALIZATION
st.divider()
st.header("Real-time Results")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(worksheet="Sheet1")
    
    if not data.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total Responses", len(data))
        # Use 'sentiment' column we defined in Step 1
        col2.metric("Avg. AI Sentiment", round(data['sentiment'].mean(), 2))
        
        st.subheader("Responses by Role")
        role_counts = data['role'].value_counts()
        st.bar_chart(role_counts)
    else:
        st.info("The sheet is empty. Be the first to submit!")
        
except Exception as e:
    st.warning("Connect your Google Sheet in secrets to see the dashboard!")
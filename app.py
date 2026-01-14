# %% [1] IMPORTS & CONFIGURATION
import streamlit as st
import pandas as pd
from datetime import datetime
# Note: You'll eventually need: pip install gspread
# import gspread 

st.set_page_config(page_title="Research Portfolio", layout="centered")

# %% [2] DATABASE CONNECTION (The "Brain")
# This cell handles the connection to your storage (Google Sheets or CSV)
def save_to_database(data_dict):
    """
    For now, this saves to a local CSV. 
    Later, we will swap this code for the Google Sheets API.
    """
    df = pd.DataFrame([data_dict])
    # Append to a local file
    try:
        existing_data = pd.read_csv("responses.csv")
        updated_data = pd.concat([existing_data, df], ignore_index=True)
        updated_data.to_csv("responses.csv", index=False)
    except FileNotFoundError:
        df.to_csv("responses.csv", index=False)

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

# %% [5] DATA VISUALIZATION (The "Dashboard")
st.divider()
st.header("Real-time Results")

try:
    data = pd.read_csv("responses.csv")
    
    # Metric Row
    col1, col2 = st.columns(2)
    col1.metric("Total Responses", len(data))
    col2.metric("Avg. AI Sentiment", round(data['sentiment'].mean(), 2))
    
    # Simple Chart
    st.subheader("Responses by Role")
    role_counts = data['role'].value_counts()
    st.bar_chart(role_counts)
    
except FileNotFoundError:
    st.warning("No data yet. Submit the form above to see the dashboard update!")
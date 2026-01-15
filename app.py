import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# %% [1] PAGE CONFIG & CSS (Includes 'Hide Header' per your request)
st.set_page_config(
    page_title="AI Research Portfolio",
    layout="centered"
)

# Custom CSS to hide the Streamlit header, footer, and main menu
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# %% [2] DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# %% [3] UPGRADE 1: SURVEY UI
st.title("📊 The Evolution of Research Careers")
st.write("Exploring how AI is shifting trust, skills, and adoption across industries.")

with st.form("main_survey"):
    st.subheader("Demographics")
    level = st.selectbox("Organizational Level", 
                         ["Entry-level", "Individual Contributor", "Manager", "Director/Executive"])
    tenure = st.selectbox("Years in Industry", 
                          ["<1 year", "1-3 years", "4-7 years", "8-12 years", "13+ years"])

    st.divider()
    st.subheader("AI Workplace Sentiment")
    st.caption("Rate your agreement: 1 = Strongly Disagree, 5 = Strongly Agree")

    # The 3 Persona Questions
    trust_q = st.radio("I feel confident identifying when an AI-generated output is factually incorrect.", 
                       options=[1,2,3,4,5], horizontal=True)
    
    skill_q = st.radio("My current core technical skills will remain relevant for the next 3 years.", 
                       options=[1,2,3,4,5], horizontal=True)
    
    adoption_q = st.radio("I use AI for tasks not explicitly part of my official job description.", 
                          options=[1,2,3,4,5], horizontal=True)

    linkedin = st.text_input("LinkedIn URL (Optional)")
    
    submitted = st.form_submit_button("Submit Response")

# %% [4] UPGRADE 1: LOGIC
if submitted:
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "tenure": tenure,
        "trust_score": trust_q,
        "skill_score": skill_q,
        "adoption_score": adoption_q,
        "linkedin_url": linkedin
    }
    
    try:
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
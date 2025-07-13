from dotenv import load_dotenv
import os
import streamlit as st
import requests
import math

# Load environment variables
load_dotenv()


AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_INDEX_NAME_JD = os.getenv("AZURE_AI_SEARCH_INDEX_NAME_JD")
SEMANTIC_CONFIG_JD = "semantic-config-search-jd"

def global_jd_recommendation(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME_JD,SEMANTIC_CONFIG_JD):
    # Headers for REST call
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_AI_SEARCH_API_KEY
    }

    # Resume summary (hardcoded for now)
    resume_summary = "Looking for a data engineer in London"

    # --- Streamlit UI ---
    st.set_page_config(page_title="JD Matcher", page_icon="", layout="wide")
    st.title("Smart JD Recommender")
    st.markdown("Match your resume with the most relevant job descriptions using **Azure AI Search + Semantic Reranker**.")

    st.markdown("###  Resume Summary")
    st.info(resume_summary)

    st.markdown("### Top JD Matches")

    # Payload for Azure AI Search
    payload = {
        "search": resume_summary,
        "queryType": "semantic",
        "semanticConfiguration": SEMANTIC_CONFIG_JD,
        "queryLanguage": "en-us",
        "captions": "extractive",
        "answers": "extractive"
    }

    # Call Azure Search
    with st.spinner("Searching"):
        try:
            response = requests.post(
                f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                results = response.json().get("value", [])
                if not results:
                    st.warning("No matching jobs found.")
                else:
                    # Group results in rows of 3
                    rows = [results[i:i+3] for i in range(0, len(results), 3)]

                    for row in rows:
                        cols = st.columns(3)
                        for idx, res in enumerate(row):
                            with cols[idx]:
                                job_role = res.get("JobRole", "Unknown")
                                jd_summary = res.get("JDSummary", "No summary available")
                                location = res.get("Location", "Unknown")
                                skills = res.get("Skills", "N/A")
                                score = res.get("@search.rerankerScore", 0.0)
                                match_percent = round((score / 4.0) * 100)

                                st.markdown(f"""
                                    <div style='background-color: #ffffff; padding: 16px; border-radius: 12px;
                                                box-shadow: 0 2px 8px rgba(0,0,0,0.06); min-height: 250px'>
                                        <h5 style='color: #333333; margin-bottom: 8px;'>🧩 <b>{job_role}</b></h5>
                                        <p style='margin: 4px 0;'><b>📍 Location:</b> {location}</p>
                                        <p style='margin: 4px 0;'><b>🧠 Skills:</b> {skills}</p>
                                        <p style='margin: 4px 0;'><b>📊 Match:</b> {match_percent}%</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                st.progress(match_percent)

            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Exception occurred: {e}")

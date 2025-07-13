import os
import json
import streamlit as st
import time
import pandas as pd
import requests
 
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
import ai_search_index_creator_task
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
import openai_profile_recommendation_chatbot
import pdf_extractor_openai_prompt_task
import global_jd_recommendation_task
import candidate_recommendation_task
import constants
from datetime import datetime
#import general_recommendation_Chatbot
import resume_insight_applicant_info_tab
 
# load .env file which contain the keys
load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_AI_SEARCH_API_KEY=os.getenv("AZURE_AI_SEARCH_API_KEY")
 
OPENAI_ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT_URL")
AZUREOPEN_AI_DEPLOYMENT_NAME = os.getenv("AZUREOPEN_AI_DEPLOYMENT_NAME")
AZURE_AI_SEARCH_ENDPOINT=os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_INDEX_NAME=os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_AI_SEARCH_INDEX_NAME_JD=os.getenv("AZURE_AI_SEARCH_INDEX_NAME_JD")
GPT_API_VERSION=os.getenv("GPT_API_VERSION")
 
# Initialize Azure OpenAI client with key-based authentication
AZUREOPENAI_CLIENT = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT_URL,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=GPT_API_VERSION
)
 
AZUREAISEARCH_CLIENT = SearchClient(
    endpoint=AZURE_AI_SEARCH_ENDPOINT,
    index_name=AZURE_AI_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
    )
 
AZUREAISEARCHINDEX_CLIENT = SearchIndexClient(
    endpoint=AZURE_AI_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
    )
 
AZUREAISEARCH_CLIENT_JD = SearchClient(
    endpoint=AZURE_AI_SEARCH_ENDPOINT,
    index_name=AZURE_AI_SEARCH_INDEX_NAME_JD,
    credential=AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
    )
 
def matchly_login():
 
#    # Read SVG logo
#     svg_path = os.path.join(os.path.dirname(__file__), "../../resources/ubs_semibold_rgb_26_41x110.svg")
#     with open(svg_path, "r") as f:
#         svg_logo = f.read()
#     st.markdown(
#         f"""
#         <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem;">
#             {svg_logo}
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
 
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
 
    # If not logged in, show login form in the center
    if not st.session_state.logged_in:
        # Remove Streamlit's default padding
        st.markdown(
            """
            <style>
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
            }
            .logo-top-right {
                position: fixed;
                top: 30px;
                right: 40px;
                z-index: 9999;
            }
            .centered-login-outer {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .centered-login-inner {
                min-width: 350px;
                max-width: 400px;
                width: 100%;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.07);
                padding: 2.5rem 2rem 2rem 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
   
        role = st.selectbox("Login as", ["Select", constants.CANDIDATE, constants.RECRUITER], key="login_role")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
 
        if st.button("Login"):
            if role == constants.CANDIDATE and username == "can" and password == "can123":
                st.session_state.logged_in = True
                st.session_state.role = constants.CANDIDATE
                st.rerun()  # Force UI refresh
            elif role == constants.RECRUITER and username == "rec" and password == "rec123":
                st.session_state.logged_in = True
                st.session_state.role = constants.RECRUITER
                st.rerun()  # Force UI refresh
            else:
                st.error("Invalid credentials")
        st.markdown("</div></div>", unsafe_allow_html=True)
   
    else:
        # If logged in, show only status and logout button in sidebar
        with st.sidebar:
            st.success(f"Logged in as {st.session_state.role}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.rerun()
   
 
def recruiter_interface():
    st.title("Matchly")
    tab1, tab2 = st.tabs(["Job Descriptions", "Candidate Finder"])
    with tab1:
        st.header("Upload Job Description")
        uploaded_jd = st.file_uploader("Upload JD in PDF format", type=["pdf", "txt"])
 
        if uploaded_jd is not None:
            # Generate a unique file name
            unique_filename = f"{uploaded_jd.name}"
 
            if st.button("📤 Save JD"):
                success=True
                if success:
                    #st.success("File loaded, analyzing resume...")
                    status_placeholder = st.empty()
                    status_placeholder.success("JD uploaded")
 
                    time.sleep(3)  # Wait 3 seconds
 
                    status_placeholder.empty()
 
                    # Extract text from the uploaded file
                    jd_text = pdf_extractor_openai_prompt_task.extract_text_from_pdf(uploaded_jd)
                    print(jd_text)
                    #Extract the correct fields by calling openai
                    openai_jd_response=pdf_extractor_openai_prompt_task.extract_resume_info(jd_text, AZUREOPENAI_CLIENT, AZUREOPEN_AI_DEPLOYMENT_NAME, constants.JD_PROMPT)
                    print(openai_jd_response)
                    if isinstance(openai_jd_response, str):
                        try:
                            data = json.loads(openai_jd_response)
                        except json.JSONDecodeError as e:
                            st.error(f"Failed to parse JSON: {e}")
                            st.stop()
                    else:
                        data = openai_jd_response  # Already a dict
                   
                    #Create azure AI search index
                    ai_search_index_creator_task.create_search_index_jd(AZUREAISEARCHINDEX_CLIENT, AZURE_AI_SEARCH_INDEX_NAME_JD)
                    #Populate azure AI search with json data
                    ai_search_index_creator_task.upload_to_search_index_jd(data,unique_filename,AZUREAISEARCH_CLIENT_JD)  
           
        candidate_recommendation_task.candidate_recommendations()
 
    with tab2:
        openai_profile_recommendation_chatbot.azureai_search_userprofile_ranker(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME,AZURE_AI_SEARCH_INDEX_NAME_JD,constants.SEMANTIC_CONFIG,constants.SEMANTIC_CONFIG_JD,AZUREOPENAI_CLIENT,AZUREOPEN_AI_DEPLOYMENT_NAME)
        #test2.azureai_search_userprofile_ranker(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME,AZURE_AI_SEARCH_INDEX_NAME_JD,SEMANTIC_CONFIG,SEMANTIC_CONFIG_JD,AZUREOPENAI_CLIENT,AZUREOPEN_AI_DEPLOYMENT_NAME)
    #with tab3:
    #    general_recommendation_Chatbot.run_streamlit_chatbot(constants.SEMANTIC_CONFIG)
 
def candidate_interface():
 
    st.title("Matchly")
 
    main_tab1, main_tab2 = st.tabs(["Job Recommendation", "Global Recommendations Bot"])
 
    with main_tab1:
 
        uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
 
        if uploaded_file is not None:
            # Generate a unique file name
            unique_filename = f"{uploaded_file.name}"
 
            if st.button("📤 Upload and Analyze Resume"):
                success=True
                if success:
                    #st.success("File loaded, analyzing resume...")
                    status_placeholder = st.empty()
                    status_placeholder.success("File loaded, analyzing resume...")
 
                    time.sleep(3)  # Wait 3 seconds
 
                    status_placeholder.empty()
 
                    # Extract text from the uploaded file
                    resume_text = pdf_extractor_openai_prompt_task.extract_text_from_pdf(uploaded_file)
                    #Extract the correct fields by calling openai
                    openai_response=pdf_extractor_openai_prompt_task.extract_resume_info(resume_text, AZUREOPENAI_CLIENT, AZUREOPEN_AI_DEPLOYMENT_NAME,constants.RESUME_PROMPT)
                    print(openai_response)
                   
                    if isinstance(openai_response, str):
                        try:
                            data = json.loads(openai_response)
                        except json.JSONDecodeError as e:
                            st.error(f"Failed to parse JSON: {e}")
                            st.stop()
                    else:
                        data = openai_response  # Already a dict
                   
                    ProfileSummary = data.get("Profile Summary",{})
                    print(ProfileSummary)
 
                    def get_top_jobs_by_profile_summary(summary_text):
                        url = f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview"
                       
                        headers = {
                            "Content-Type": "application/json",
                            "api-key": AZURE_AI_SEARCH_API_KEY
                        }
 
                        payload = {
                            "search": summary_text,
                            "queryType": "semantic",
                            "semanticConfiguration": constants.SEMANTIC_CONFIG_JD,
                            "queryLanguage": "en-us",
                            "top": 3
                        }
 
                        response = requests.post(url, headers=headers, json=payload)
 
                        if response.status_code == 200:
                            return response.json().get("value", [])
                        else:
                            st.error(f"Azure AI Search error {response.status_code}: {response.text}")
                            return []
 
                    # Display in Streamlit
                    st.set_page_config(page_title="JD Recommender", layout="centered")
                    st.title("Job Recommendations Based on Resume")
 
                    st.markdown("### Recommended Jobs:")
 
                    results = get_top_jobs_by_profile_summary(ProfileSummary)
 
                    if results:
                        cols = st.columns(len(results))  # Create one column per result
 
                        for idx, job in enumerate(results):
                            with cols[idx]:
                                role = job.get("JobRole", "N/A")
                                location = job.get("Location", "N/A")
                                summary = job.get("JDSummary", "No summary available")[:200]
                                score = job.get("@search.rerankerScore", 0.0)
                                match_percent = round((score / 4.0) * 100)
 
                                st.markdown(f"""
                                    <div style="
                                        padding: 15px;
                                        background-color: #fff;
                                        border-radius: 10px;
                                        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                                        margin-bottom: 20px;
                                        height: 280px;
                                        overflow: auto;
                                    ">
                                        <h4 style="color: #E60000;">{role}</h4>
                                        <p><strong>Location:</strong> {location}</p>
                                        <p><strong>Summary:</strong> {summary}...</p>
                                        <div style="
                                            position: relative;
                                            background-color: #f0f0f0;
                                            height: 20px;
                                            border-radius: 10px;
                                            overflow: hidden;
                                            margin-top: 10px;
                                        ">
                                            <div style="background-color: #E60000; width: {match_percent}%; height: 100%;"></div>
                                            <div style="
                                                position: absolute;
                                                width: 100%;
                                                text-align: center;
                                                top: 0;
                                                line-height: 20px;
                                                font-weight: bold;
                                                color: black;
                                            ">
                                                {match_percent}% match
                                            </div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No jobs matched.")
 
                    #Interface calls
                    resume_insight_applicant_info_tab.resume_insight(openai_response)
     
                   
                    #Create azure AI search index
                    ai_search_index_creator_task.create_search_index(AZUREAISEARCHINDEX_CLIENT, AZURE_AI_SEARCH_INDEX_NAME)
                    #Populate azure AI search with json data
                    ai_search_index_creator_task.upload_to_search_index(data,unique_filename,AZUREAISEARCH_CLIENT)
 
    with main_tab2:
        openai_profile_recommendation_chatbot.openai_aisearch_chatbot(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME,AZURE_AI_SEARCH_INDEX_NAME_JD,constants.SEMANTIC_CONFIG,constants.SEMANTIC_CONFIG_JD,AZUREOPENAI_CLIENT,AZUREOPEN_AI_DEPLOYMENT_NAME)
   
    #with main_tab3:
     #   global_jd_recommendation_task.global_jd_recommendation(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME_JD,SEMANTIC_CONFIG_JD)
 
def main():
    matchly_login()
    if st.session_state.role == constants.CANDIDATE:
        candidate_interface()
    elif st.session_state.role == constants.RECRUITER:
        recruiter_interface()
 
# Run it on your local file
if __name__ == "__main__":
    main()
 
# import streamlit as st
# import requests
# import get_openai_recommendation

# def openai_aisearch_chatbot(
#     AZURE_AI_SEARCH_API_KEY,
#     AZURE_AI_SEARCH_ENDPOINT,
#     AZURE_AI_SEARCH_INDEX_NAME,
#     AZURE_AI_SEARCH_INDEX_NAME_JD,
#     SEMANTIC_CONFIG,
#     SEMANTIC_CONFIG_JD,
#     client,
#     deployment
# ):
#     if st.session_state.get("current_role") != "candidate":
#         st.session_state.candidate_results = []
#         st.session_state.current_role = "candidate"

#     headers = {
#         "Content-Type": "application/json",
#         "api-key": AZURE_AI_SEARCH_API_KEY
#     }

#     # --- UI Config ---
#     st.set_page_config(page_title="JD Chatbot", layout="wide")

#     # --- Styling (match recruiter version) ---
#     st.markdown("""
#         <style>
#             html, body, [class*="css"] {
#                 font-family: 'Segoe UI', sans-serif;
#                 background-color: #f9f9f9;
#             }
#             .jd-card {
#                 padding: 15px 20px;
#                 background-color: #ffffff;
#                 border: 1px solid #e0e0e0;
#                 border-radius: 10px;
#                 margin-bottom: 20px;
#                 box-shadow: 0 1px 4px rgba(0,0,0,0.05);
#             }
#             .jd-title {
#                 font-size: 18px;
#                 font-weight: 600;
#                 color: #1f4e79;
#                 margin-bottom: 8px;
#             }
#         </style>
#     """, unsafe_allow_html=True)

#     col1, col2 = st.columns([1, 2])

#     # --- Left Column: Chatbot ---
#     with col1:
#         st.markdown("#### Describe Your JD or Requirement")

#         if "chat_history" not in st.session_state:
#             st.session_state.chat_history = []

#         if "candidate_results" not in st.session_state:
#             st.session_state.candidate_results = []

#         user_input_2 = st.chat_input("e.g. Looking for DevOps roles with Docker and Jenkins")

#         if user_input_2:
#             with st.chat_message("assistant"):
#                 with st.spinner("Searching..."):
#                     payload = {
#                         "search": user_input_2,
#                         "queryType": "semantic",
#                         "semanticConfiguration": SEMANTIC_CONFIG_JD,
#                         "queryLanguage": "en-us",
#                         "captions": "extractive",
#                         "answers": "extractive",
#                         "top": 3
#                     }

#                     try:
#                         response = requests.post(
#                             f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview",
#                             headers=headers,
#                             json=payload
#                         )

#                         if response.status_code == 200:
#                             results = response.json().get("value", [])
#                             if not results:
#                                 st.markdown("No matching jobs found.")
#                                 st.session_state.candidate_results = []
#                             else:
#                                 st.markdown("Top matching jobs are displayed on the right.")
#                                 st.session_state.candidate_results = results
#                         else:
#                             st.error(f"Error: {response.status_code} - {response.text}")
#                             st.session_state.candidate_results = []

#                     except Exception as e:
#                         st.error(f"Exception occurred: {e}")
#                         st.session_state.candidate_results = []

#     # --- Right Column: Matching JD Tiles ---
#     with col2:
#         st.markdown("#### Recommended Jobs")

#         results = st.session_state.get("candidate_results", [])

#         if not results:
#             st.info("No results to show yet. Enter a prompt on the left.")
#         else:
#             for res in results:
#                 JDSummary = res.get("JDSummary", "No summary available")
#                 Location = res.get("Location", "Unknown")
#                 Skills = res.get("Skills", "N/A")
#                 reranker_score = res.get("@search.rerankerScore", 0.0)
#                 percent_match = round((reranker_score / 4) * 100)

#                 st.markdown(f"""
#                     <div class="jd-card">
#                         <div class="jd-title">{JDSummary}</div>
#                         <p><strong>Location:</strong> {Location}</p>
#                         <p><strong>Skills:</strong> {Skills}</p>
#                         <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 10px;">
#                             <div style="background-color: #d10d0d; width: {percent_match}%; height: 100%;"></div>
#                             <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
#                                 {percent_match}% match
#                             </div>
#                         </div>
#                     </div>
#                 """, unsafe_allow_html=True)


# # def azureai_search_userprofile_ranker(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME,AZURE_AI_SEARCH_INDEX_NAME_JD,SEMANTIC_CONFIG,SEMANTIC_CONFIG_JD,client,deployment):

# #     if st.session_state.get("current_role") != "recruiter":
# #         st.session_state.recruiter_results = []
# #         st.session_state.expanded_bio_keys = set()
# #         st.session_state.current_role = "recruiter"

# #     headers = {
# #         "Content-Type": "application/json",
# #         "api-key": AZURE_AI_SEARCH_API_KEY
# #     }

# #     st.set_page_config(page_title="Profile Ranker", layout="wide")

# #     # --- Styling ---
# #     st.markdown("""
# #         <style>
# #             html, body, [class*="css"] {
# #                 font-family: 'Segoe UI', sans-serif;
# #                 background-color: #f9f9f9;
# #             }
# #             .candidate-card {
# #                 padding: 15px 20px;
# #                 background-color: #ffffff;
# #                 border: 1px solid #e0e0e0;
# #                 border-radius: 10px;
# #                 margin-bottom: 20px;
# #                 box-shadow: 0 1px 4px rgba(0,0,0,0.05);
# #             }
# #             .candidate-name {
# #                 font-size: 18px;
# #                 font-weight: 600;
# #                 color: #1f4e79;
# #                 margin-bottom: 8px;
# #             }
# #         </style>
# #     """, unsafe_allow_html=True)

# #     col1, col2 = st.columns([1, 2])

# #     # --- Left Panel: Search Input ---
# #     with col1:
# #         st.markdown("#### Describe Your Candidate Requirement")

# #         if "chat_history" not in st.session_state:
# #             st.session_state.chat_history = []

# #         user_input = st.chat_input("e.g. Looking for a DevOps engineer with Docker and Jenkins")

# #         if user_input:
# #             with st.chat_message("assistant"):
# #                 with st.spinner("Searching..."):
# #                     payload = {
# #                         "search": user_input,
# #                         "queryType": "semantic",
# #                         "semanticConfiguration": SEMANTIC_CONFIG,
# #                         "queryLanguage": "en-us",
# #                         "captions": "extractive",
# #                         "answers": "extractive",
# #                         "top": 3
# #                     }

# #                     try:
# #                         response = requests.post(
# #                             f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME}/docs/search?api-version=2023-07-01-Preview",
# #                             headers=headers,
# #                             json=payload
# #                         )
# #                         if response.status_code == 200:
# #                             results = response.json().get("value", [])
# #                             st.session_state.recruiter_results = results
# #                         else:
# #                             st.error(f"Error: {response.status_code} - {response.text}")
# #                             st.session_state.recruiter_results = []
# #                     except Exception as e:
# #                         st.error(f"Exception occurred: {e}")
# #                         st.session_state.recruiter_results = []

# #     # --- Right Panel: Candidate Cards ---
# #     with col2:
# #         st.markdown("#### Recommended Candidates")

# #         results = st.session_state.get("recruiter_results", [])

# #         if not results:
# #             st.info("No results to show yet. Enter a prompt in the input box.")
# #         else:
# #             for idx, res in enumerate(results):
# #                 name = res.get("FullName", "N/A")
# #                 summary = res.get("ProfileSummary", "No summary available")
# #                 skills_raw = res.get("Skills", "")
# #                 location = res.get("Location", "N/A")
# #                 skills = [s.strip() for s in skills_raw.split(",")] if isinstance(skills_raw, str) else skills_raw
# #                 reranker_score = res.get("@search.rerankerScore", 0.0)
# #                 percent_match = round((reranker_score / 4.0) * 100)

# #                 cand_key = f"cand_{idx}"
# #                 bio_key = f"bio_{cand_key}"

# #                 with st.container():
# #                     st.markdown(f"**{name}** — {location}")
# #                         #st.progress(percent, text=f"{percent}% match")
# #                     st.markdown(f"""
# #                         <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
# #                             <div style="background-color: #d10d0d; width: {percent_match}%; height: 100%;"></div>
# #                             <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
# #                                 {percent_match}% match
# #                             </div>
# #                         </div>
# #                     """, unsafe_allow_html=True)

# #                     if st.button("View Bio", key=f"btn_{bio_key}"):
# #                         if bio_key in st.session_state.expanded_bio_keys:
# #                             st.session_state.expanded_bio_keys.remove(bio_key)
# #                         else:
# #                             st.session_state.expanded_bio_keys.add(bio_key)

# #                     if bio_key in st.session_state.expanded_bio_keys:
# #                         with st.spinner(f"Loading bio for {name}..."):
# #                             with st.expander(f"Profile Summary for {name}", expanded=True):
# #                                 st.markdown(f"**Summary:** {summary}")
# #                                 st.markdown(f"**Skills:** {', '.join(skills) if skills else 'No skills listed'}")

# def azureai_search_userprofile_ranker(AZURE_AI_SEARCH_API_KEY,AZURE_AI_SEARCH_ENDPOINT,AZURE_AI_SEARCH_INDEX_NAME,AZURE_AI_SEARCH_INDEX_NAME_JD,SEMANTIC_CONFIG,SEMANTIC_CONFIG_JD,client,deployment):

#     if st.session_state.get("current_role") != "recruiter":
#         st.session_state.recruiter_results = []
#         st.session_state.expanded_bio_keys = set()
#         st.session_state.current_role = "recruiter"

#     headers = {
#         "Content-Type": "application/json",
#         "api-key": AZURE_AI_SEARCH_API_KEY
#     }

#     st.set_page_config(page_title="Profile Ranker", layout="wide")

#     # --- Styling ---
#     st.markdown("""
#         <style>
#             html, body, [class*="css"] {
#                 font-family: 'Segoe UI', sans-serif;
#                 background-color: #f9f9f9;
#             }
#             .candidate-card {
#                 padding: 15px 20px;
#                 background-color: #ffffff;
#                 border: 1px solid #e0e0e0;
#                 border-radius: 10px;
#                 margin-bottom: 20px;
#                 box-shadow: 0 1px 4px rgba(0,0,0,0.05);
#             }
#             .candidate-name {
#                 font-size: 18px;
#                 font-weight: 600;
#                 color: #1f4e79;
#                 margin-bottom: 8px;
#             }
#         </style>
#     """, unsafe_allow_html=True)

#     col1, col2 = st.columns([1, 2])

#     # --- Left Panel: Search Input ---
#     with col1:
#         st.markdown("#### Describe Your Candidate Requirement")

#         if "chat_history" not in st.session_state:
#             st.session_state.chat_history = []

#         user_input = st.chat_input("e.g. Looking for a DevOps engineer with Docker and Jenkins")

#         if user_input:
#             with st.chat_message("assistant"):
#                 with st.spinner("Searching..."):
#                     payload = {
#                         "search": user_input,
#                         "queryType": "semantic",
#                         "semanticConfiguration": SEMANTIC_CONFIG,
#                         "queryLanguage": "en-us",
#                         "captions": "extractive",
#                         "answers": "extractive",
#                         "top": 5
#                     }

#                     try:
#                         response = requests.post(
#                             f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME}/docs/search?api-version=2023-07-01-Preview",
#                             headers=headers,
#                             json=payload
#                         )
#                         if response.status_code == 200:
#                             #results = response.json().get("value", [])
#                             all_candidates = res.json().get("value", []) if res.status_code == 200 else []
#                             print(all_candidates)
#                             # Re-rank using OpenAI
#                             candidates = get_openai_recommendation.get_top_candidates_from_openai(user_input, all_candidates, top_n=3)
#                             st.session_state.recruiter_results = candidates
#                         else:
#                             st.error(f"Error: {response.status_code} - {response.text}")
#                             st.session_state.recruiter_results = []
#                     except Exception as e:
#                         st.error(f"Exception occurred: {e}")
#                         st.session_state.recruiter_results = []

#     # --- Right Panel: Candidate Cards ---
#     with col2:
#         st.markdown("#### Recommended Candidates")

#         results = st.session_state.get("recruiter_results", [])

#         if not results:
#             st.info("No results to show yet. Enter a prompt in the input box.")
#         else:
#             for idx, res in enumerate(results):
#                 name = res.get("FullName", "N/A")
#                 summary = res.get("ProfileSummary", "No summary available")
#                 skills_raw = res.get("Skills", "")
#                 location = res.get("Location", "N/A")
#                 skills = [s.strip() for s in skills_raw.split(",")] if isinstance(skills_raw, str) else skills_raw
#                 reranker_score = res.get("@search.rerankerScore", 0.0)
#                 percent_match = round((reranker_score / 4.0) * 100)

#                 cand_key = f"cand_{idx}"
#                 bio_key = f"bio_{cand_key}"

#                 with st.container():
#                     st.markdown(f"**{name}** — {location}")
#                         #st.progress(percent, text=f"{percent}% match")
#                     st.markdown(f"""
#                         <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
#                             <div style="background-color: #d10d0d; width: {percent_match}%; height: 100%;"></div>
#                             <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
#                                 {percent_match}% match
#                             </div>
#                         </div>
#                     """, unsafe_allow_html=True)

#                     if st.button("View Bio", key=f"btn_{bio_key}"):
#                         if bio_key in st.session_state.expanded_bio_keys:
#                             st.session_state.expanded_bio_keys.remove(bio_key)
#                         else:
#                             st.session_state.expanded_bio_keys.add(bio_key)

#                     if bio_key in st.session_state.expanded_bio_keys:
#                         with st.spinner(f"Loading bio for {name}..."):
#                             with st.expander(f"Profile Summary for {name}", expanded=True):
#                                 st.markdown(f"**Summary:** {summary}")
#                                 st.markdown(f"**Skills:** {', '.join(skills) if skills else 'No skills listed'}")

import streamlit as st
import requests
 
import azureopenai_recommendation_function
import candidate_recommendation_task
 
def openai_aisearch_chatbot(
    AZURE_AI_SEARCH_API_KEY,
    AZURE_AI_SEARCH_ENDPOINT,
    AZURE_AI_SEARCH_INDEX_NAME,
    AZURE_AI_SEARCH_INDEX_NAME_JD,
    SEMANTIC_CONFIG,
    SEMANTIC_CONFIG_JD,
    client,
    deployment
):
    if st.session_state.get("current_role") != "candidate":
        st.session_state.candidate_results = []
        st.session_state.current_role = "candidate"
 
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_AI_SEARCH_API_KEY
    }
 
    # --- UI Config ---
    st.set_page_config(page_title="JD Chatbot", layout="wide")
 
    # --- Styling (match recruiter version) ---
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9f9f9;
            }
            .jd-card {
                padding: 15px 20px;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            }
            .jd-title {
                font-size: 18px;
                font-weight: 600;
                color: #1f4e79;
                margin-bottom: 8px;
            }
        </style>
    """, unsafe_allow_html=True)
 
    col1, col2 = st.columns([1, 2])
 
    # --- Left Column: Chatbot ---
    with col1:
        st.markdown("#### Describe Your JD or Requirement")
 
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
 
        if "candidate_results" not in st.session_state:
            st.session_state.candidate_results = []
 
        user_input_2 = st.chat_input("e.g. Looking for DevOps roles with Docker and Jenkins")
 
        if user_input_2:
            with st.chat_message("assistant"):
                with st.spinner("Searching..."):
                    payload = {
                        "search": user_input_2,
                        "queryType": "semantic",
                        "semanticConfiguration": SEMANTIC_CONFIG_JD,
                        "queryLanguage": "en-us",
                        "captions": "extractive",
                        "answers": "extractive",
                        "top": 3
                    }
 
                    try:
                        response = requests.post(
                            f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview",
                            headers=headers,
                            json=payload
                        )
 
                        if response.status_code == 200:
                            results = response.json().get("value", [])
                            if not results:
                                st.markdown("No matching jobs found.")
                                st.session_state.candidate_results = []
                            else:
                                st.markdown("Top matching jobs are displayed on the right.")
                                st.session_state.candidate_results = results
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                            st.session_state.candidate_results = []
 
                    except Exception as e:
                        st.error(f"Exception occurred: {e}")
                        st.session_state.candidate_results = []
 
    # --- Right Column: Matching JD Tiles ---
    with col2:
        st.markdown("#### Recommended Jobs")
 
        results = st.session_state.get("candidate_results", [])
 
        if not results:
            #st.info("No results to show yet. Enter a prompt on the left.")
            st.markdown(
                """
                <div style="background-color: #E6EBB0; padding: 16px; border-radius: 8px; color: #333;">
                    No results to show yet. Enter a prompt in the input box.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for res in results:
                JDSummary = res.get("JDSummary", "No summary available")
                Location = res.get("Location", "Unknown")
                Skills = res.get("Skills", "N/A")
                reranker_score = res.get("@search.rerankerScore", 0.0)
                percent_match = round((reranker_score / 4) * 100)
 
                st.markdown(f"""
                    <div class="jd-card">
                        <div class="jd-title">{JDSummary}</div>
                        <p><strong>Location:</strong> {Location}</p>
                        <p><strong>Skills:</strong> {Skills}</p>
                        <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 10px;">
                            <div style="background-color: #E60000; width: {percent_match}%; height: 100%;"></div>
                            <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
                                {percent_match}% match
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
 
def azureai_search_userprofile_ranker(
    AZURE_AI_SEARCH_API_KEY,
    AZURE_AI_SEARCH_ENDPOINT,
    AZURE_AI_SEARCH_INDEX_NAME,
    AZURE_AI_SEARCH_INDEX_NAME_JD,
    SEMANTIC_CONFIG,
    SEMANTIC_CONFIG_JD,
    client,
    deployment
):
    if st.session_state.get("current_role") != "recruiter":
        st.session_state.recruiter_results = []
        st.session_state.expanded_bio_keys = set()
        st.session_state.expanded_skillgap_keys = set()
        st.session_state.expanded_timeline_keys = set()
        st.session_state.current_role = "recruiter"
 
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_AI_SEARCH_API_KEY
    }
 
    st.set_page_config(page_title="Profile Ranker", layout="wide")
 
    # --- Styling ---
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9f9f9;
            }
            .candidate-card {
                padding: 15px 20px;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            }
            .candidate-name {
                font-size: 18px;
                font-weight: 600;
                color: #1f4e79;
                margin-bottom: 8px;
            }
        </style>
    """, unsafe_allow_html=True)
 
    col1, col2 = st.columns([1, 2])
 
    # --- Left Panel: Search Input ---
    with col1:
        st.markdown("#### Describe Your Candidate Requirement")
 
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
 
        user_input = st.chat_input("e.g. Looking for a DevOps engineer with Docker and Jenkins")
 
        if user_input:
            with st.chat_message("assistant"):
                with st.spinner("Searching..."):
                    payload = {
                        "search": user_input.strip(),
                        "queryType": "semantic",
                        "semanticConfiguration": SEMANTIC_CONFIG,
                        "queryLanguage": "en-us",
                        "captions": "extractive",
                        "answers": "extractive",
                        "top": 5  # fetch more for better re-ranking
                    }
                    try:
                        res = requests.post(
                            f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME}/docs/search?api-version=2023-07-01-Preview",
                            headers=headers,
                            json=payload
                        )
                        if res.status_code == 200:
                            all_candidates = res.json().get("value", []) if res.status_code == 200 else []
                            candidates = azureopenai_recommendation_function.get_top_candidates_from_openai(
                                user_input, all_candidates, top_n=3
                            )
                            st.session_state.recruiter_results = candidates
                        else:
                            st.error(f"Error: {res.status_code} - {res.text}")
                            st.session_state.recruiter_results = []
                    except Exception as e:
                        st.error(f"Exception occurred: {e}")
                        st.session_state.recruiter_results = []
 
    # --- Right Panel: Candidate Cards ---
    with col2:
        st.markdown("#### Recommended Candidates")
 
        candidates = st.session_state.get("recruiter_results", [])
 
        if not candidates:
            #st.info("No results to show yet. Enter a prompt in the input box.")
            st.markdown(
                """
                <div style="background-color: #E6EBB0; padding: 16px; border-radius: 8px; color: #333;">
                    No results to show yet. Enter a prompt in the input box.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for idx, res in enumerate(candidates):
                name = res.get("FullName", "N/A")
                summary = res.get("ProfileSummary", "No summary available")
                skills_raw = res.get("Skills", "")
                location = res.get("Location", "N/A")
                skills = [s.strip() for s in skills_raw.split(",")] if isinstance(skills_raw, str) else skills_raw
                cand_score = res.get("openai_score", "N/A")
 
                cand_key = f"cand_{idx}"
                bio_key = f"bio_{cand_key}"
                skillgap_key = f"skillgap_{cand_key}"
                timeline_key = f"timeline_{cand_key}"
 
                with st.container():
                    st.markdown(f"**{name}** — {location}")
                    st.markdown(f"""
                        <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
                            <div style="background-color: #E60000; width: {cand_score}%; height: 100%;"></div>
                            <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
                                {cand_score}% match
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
 
                    col_bio, col_skillgap, col_timeline = st.columns(3)
                    with col_bio:
                        if st.button("View Bio", key=f"btn_{bio_key}"):
                            if bio_key in st.session_state.expanded_bio_keys:
                                st.session_state.expanded_bio_keys.remove(bio_key)
                            else:
                                st.session_state.expanded_bio_keys.add(bio_key)
                    with col_skillgap:
                        if st.button("Skill Gaps Analysis", key=f"btn_{skillgap_key}"):
                            if skillgap_key in st.session_state.expanded_skillgap_keys:
                                st.session_state.expanded_skillgap_keys.remove(skillgap_key)
                            else:
                                st.session_state.expanded_skillgap_keys.add(skillgap_key)
                    with col_timeline:
                        if st.button("Career Timeline", key=f"btn_{timeline_key}"):
                            if timeline_key in st.session_state.expanded_timeline_keys:
                                st.session_state.expanded_timeline_keys.remove(timeline_key)
                            else:
                                st.session_state.expanded_timeline_keys.add(timeline_key)
 
                    if bio_key in st.session_state.expanded_bio_keys:
                        with st.spinner(f"Loading bio for {name}..."):
                            with st.expander(f"Profile Summary for {name}", expanded=True):
                                st.markdown(f"**Summary:** {summary}")
                                st.markdown(f"**Skills:** {', '.join(skills) if skills else 'No skills listed'}")
 
                    if skillgap_key in st.session_state.expanded_skillgap_keys:
                        with st.spinner(f"Analyzing skill gaps for {name}..."):
                            # Get JD skills for skill gap analysis
                            jd_skill_payload = {
                                "search": user_input if user_input else "",
                                "queryType": "semantic",
                                "semanticConfiguration": SEMANTIC_CONFIG_JD,
                                "queryLanguage": "en-us",
                                "top": 1,
                                "select": "Skills"
                            }
                            jd_resp = requests.post(
                                f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview",
                                headers=headers,
                                json=jd_skill_payload
                            )
                            jd_skills = []
                            if jd_resp.status_code == 200:
                                jd_docs = jd_resp.json().get("value", [])
                                if jd_docs and "Skills" in jd_docs[0]:
                                    jd_skills_raw = jd_docs[0].get("Skills", "")
                                    jd_skills = [s.strip() for s in jd_skills_raw.split(",")] if isinstance(jd_skills_raw, str) else jd_skills_raw
 
                            cand_skills_raw = res.get("Skills", "")
                            cand_skills = [s.strip() for s in cand_skills_raw.split(",")] if isinstance(cand_skills_raw, str) else cand_skills_raw
 
                            missing_skills = [skill for skill in jd_skills if skill and skill.lower() not in [c.lower() for c in cand_skills if c]]
 
                            with st.expander(f"Skill Gaps Analysis for {name}", expanded=True):
                                st.markdown(f"**JD Skills:** {', '.join(jd_skills) if jd_skills else 'Not available'}")
                                st.markdown(f"**Candidate Skills:** {', '.join(cand_skills) if cand_skills else 'Not available'}")
                                if missing_skills:
                                    st.markdown("### Missing Skills:")
                                    for ms in missing_skills:
                                        st.markdown(f"- {ms}")
                                else:
                                    st.markdown("✅ Candidate has all required skills!")
 
                    if timeline_key in st.session_state.expanded_timeline_keys:
                        with st.spinner(f"Loading career timeline for {name}..."):
                            fig = candidate_recommendation_task.show_timeline_chart(res)
                            if fig:
                                st.markdown(f"### Career Timeline")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Timeline data not available.")
 
                    st.markdown("---")
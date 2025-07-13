import streamlit as st
import requests
import hashlib
import os
import json
import plotly.graph_objects as go
import pandas as pd
 
from dotenv import load_dotenv
from dateutil.parser import parse
from openai import AzureOpenAI
import azureopenai_recommendation_function
# Load environment variables
load_dotenv()
 
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_INDEX_NAME_JD = os.getenv("AZURE_AI_SEARCH_INDEX_NAME_JD")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
SEMANTIC_CONFIG_JD = "semantic-config-search-jd"
SEMANTIC_CONFIG = "semantic-config-search"
OPENAI_ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT_URL")
AZUREOPEN_AI_DEPLOYMENT_NAME = os.getenv("AZUREOPEN_AI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
GPT_API_VERSION=os.getenv("GPT_API_VERSION")
 
AZUREOPENAI_CLIENT = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT_URL,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=GPT_API_VERSION
)
 
def parse_date(date_str):
   if not date_str:
       return None
   if date_str.lower() == "present":
       # We'll ignore present as a date here to avoid adding extra point
       return None
   try:
       return parse(date_str, fuzzy=True)
   except Exception:
       return None
   
 
def show_timeline_chart(candidate_doc):
   work_exp_raw = candidate_doc.get("WorkExperience", "[]")
   try:
       work_exp = json.loads(work_exp_raw)
   except Exception:
       return None
   if not work_exp:
       return None
   # Parse dates, skip entries without valid start dates
   filtered_exp = []
   for exp in work_exp:
       start = parse_date(exp.get("Start Date", ""))
       if start is not None:
           filtered_exp.append({**exp, "StartDateParsed": start})
   if not filtered_exp:
       return None
   # Sort experiences by start date
   filtered_exp.sort(key=lambda x: x["StartDateParsed"])
   dates = [exp["StartDateParsed"] for exp in filtered_exp]
   companies = [exp["Company"] for exp in filtered_exp]
   roles = [exp.get("Role", "") for exp in filtered_exp]
   end_dates = [exp.get("End Date", "") for exp in filtered_exp]
   # Build hover texts
   hover_texts = [
       f"<b>{companies[i]}</b><br>Role: {roles[i]}<br>Start: {filtered_exp[i]['Start Date']}<br>End: {end_dates[i]}"
       for i in range(len(filtered_exp))
   ]
   # Y values all zero (line)
   y_vals = [0] * len(dates)
   fig = go.Figure()
   # Draw timeline line
   fig.add_trace(go.Scatter(
       x=[min(dates), max(dates)],
       y=[0, 0],
       mode='lines',
       line=dict(color='#E60000', width=4),
       hoverinfo='skip'
   ))
   # Draw points and labels
   fig.add_trace(go.Scatter(
       x=dates,
       y=y_vals,
       mode='markers+text',
       text=companies,
       textposition=['top center' if i % 2 == 0 else 'bottom center' for i in range(len(dates))],
       marker=dict(color='#E60000', size=16),
       hoverinfo='text',
       hovertext=hover_texts,
       textfont=dict(color='black', size=12),
   ))
   fig.update_layout(
       showlegend=False,
       height=400,  # bigger height but not full screen
       margin=dict(l=50, r=50, t=50, b=50),
       xaxis=dict(
           showgrid=False,
           zeroline=False,
           showticklabels=True,
           tickformat="%Y",
           tickangle=45,
           title='Year',
           tickvals=dates,
           tickfont=dict(size=12),
       ),
       yaxis=dict(
           visible=False,
           range=[-1, 1]
       ),
       plot_bgcolor='#f9f9f9',
   )
   return fig
 
def get_all_jds(headers):
    payload = {
        "search": "*",
        "queryType": "semantic",
        "semanticConfiguration": SEMANTIC_CONFIG_JD,
        "queryLanguage": "en-us",
        "top": 20
    }
    response = requests.post(
        f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME_JD}/docs/search?api-version=2023-07-01-Preview",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        return []
 
def hash_key(text):
    return hashlib.md5(text.encode()).hexdigest()
 
def candidate_recommendations():
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_AI_SEARCH_API_KEY
    }
 
    st.set_page_config(page_title="Global JD Explorer", layout="wide")
    st.title("Global Job Openings")
 
    if "expanded_bio_keys" not in st.session_state:
        st.session_state.expanded_bio_keys = set()
    if "expanded_skillgap_keys" not in st.session_state:
        st.session_state.expanded_skillgap_keys = set()
    if "expanded_job_keys" not in st.session_state:
        st.session_state.expanded_job_keys = set()
   
    all_jds = get_all_jds(headers)
    all_locations = sorted(set(jd.get("Location", "Unknown").strip('"') for jd in all_jds if jd.get("Location")))
    all_jobroles = sorted(set(jd.get("JobRole", "Unknown") for jd in all_jds if jd.get("JobRole")))
    all_corporatetitle = sorted(set(jd.get("CorporateTitle", "Unknown") for jd in all_jds if jd.get("CorporateTitle")))
    all_businessunit = sorted(set(jd.get("BusinessUnit", "Unknown") for jd in all_jds if jd.get("BusinessUnit")))
    all_businesssector = sorted(set(jd.get("BusinessSector", "Unknown") for jd in all_jds if jd.get("BusinessSector")))
    all_businesssegment = sorted(set(jd.get("BusinessSegment", "Unknown") for jd in all_jds if jd.get("BusinessSegment")))
 
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2,1,1,1,1,1,1])
 
    with col1:
        search_term = st.text_input("Search your role", "")
    with col2:
        selected_location = st.selectbox("Filter by Location", ["All"] + all_locations)
    with col3:
        selected_jobroles = st.selectbox("Filter by Job Role", ["All"] + all_jobroles)
    with col4:
        selected_corporatetitle = st.selectbox("Filter by Corporate Title", ["All"] + all_corporatetitle)
    with col5:
        selected_businessunit = st.selectbox("Filter by Business Unit", ["All"] + all_businessunit)
    with col6:    
        selected_businesssector = st.selectbox("Filter by Business Sector", ["All"] + all_businesssector)
    with col7:
        selected_businesssegment = st.selectbox("Filter by Business Segment", ["All"] + all_businesssegment)
   
   
    if search_term or selected_location != "All" or selected_businesssegment != "All" or selected_jobroles != "All" or selected_corporatetitle != "All" or selected_businessunit != "All" or selected_businesssector != "All":
        # ...existing code...
        jds = [
            jd for jd in all_jds if (
                (search_term.lower() in jd.get("JobRole", "").lower() or
                search_term.lower() in jd.get("Location", "").lower() or
                search_term.lower() in jd.get("JDSummary", "").lower())
                and (selected_location == "All" or jd.get("Location", "").strip('"').strip().lower() == selected_location.strip().lower())
                and (selected_jobroles == "All" or jd.get("JobRole", "").strip().lower() == selected_jobroles.strip().lower())
                and (selected_corporatetitle == "All" or jd.get("CorporateTitle", "").strip().lower() == selected_corporatetitle.strip().lower())
                and (selected_businessunit == "All" or jd.get("BusinessUnit", "").strip().lower() == selected_businessunit.strip().lower())
                and (selected_businesssector == "All" or jd.get("BusinessSector", "").strip().lower() == selected_businesssector.strip().lower())
                and (selected_businesssegment == "All" or jd.get("BusinessSegment", "").strip().lower() == selected_businesssegment.strip().lower())
            )
        ]
# ...existing code...
    else:
        jds = all_jds
   
    if not jds:
        st.warning("No job roles match your search.")
        return
 
   
 
    st.subheader("Job Roles")
    rows = [jds[i:i + 3] for i in range(0, len(jds), 3)]
 
    for row_idx, row in enumerate(rows):
        cols = st.columns(3)
        for col_idx, jd in enumerate(row):
            with cols[col_idx]:
                job_role = jd.get("JobRole", "Unknown")
                jd_summary = jd.get("JDSummary", "No summary provided")
                location = jd.get("Location", "Unknown").strip('"')
                JobReference = jd.get("JobReference", "Unknown")
                CorporateTitle = jd.get("CorporateTitle", "Unknown")
                BusinessUnit = jd.get("BusinessUnit", "Unknown")
                BusinessSector = jd.get("BusinessSector", "Unknown")
                BusinessSegment = jd.get("BusinessSegment", "Unknown")
 
                unique_key = hash_key(f"{job_role}_{row_idx}_{col_idx}")
                candidates_key = f"candidates_{unique_key}"
 
                with st.form(key=f"view_candidates_form_{unique_key}"):
                    st.markdown(f"""
                        <div style="background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                            <h4 style="color:#E60000;">{job_role}</h4>
                            <div><b>JobReference:</b> {JobReference}</div>
                            <div><b>Location:</b> {location}</div>
                            <div><b>Job Summary:</b> {jd_summary}...</div>
                            <div><b>CorporateTitle:</b> {CorporateTitle}</div>
                            <div><b>BusinessUnit:</b> {BusinessUnit}</div>
                            <div><b>BusinessSector:</b> {BusinessSector}</div>
                            <div><b>BusinessSegment:</b> {BusinessSegment}</div>
                        </div>
                    """, unsafe_allow_html=True)
 
                    toggle_label = "Hide Candidates" if unique_key in st.session_state.expanded_job_keys else "View Candidates"
                    submitted = st.form_submit_button(toggle_label, use_container_width=True)
 
                if submitted:
                    if unique_key in st.session_state.expanded_job_keys:
                        st.session_state.expanded_job_keys.remove(unique_key)
                    else:
                        st.session_state.expanded_job_keys.add(unique_key)
                        search_text = f"""
                            Hiring for a {job_role} role based in {location}.
                            Summary: {jd_summary}
                        """
                        with st.spinner("Matching candidates..."):
                            # candidate_payload = {
                            #     "search": search_text.strip(),
                            #     "queryType": "semantic",
                            #     "semanticConfiguration": SEMANTIC_CONFIG,
                            #     "queryLanguage": "en-us",
                            #     "top": 3
                            # }
                            # res = requests.post(
                            #     f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME}/docs/search?api-version=2023-07-01-Preview",
                            #     headers=headers,
                            #     json=candidate_payload
                            # )
                            # candidates = res.json().get("value", []) if res.status_code == 200 else []
                            candidate_payload = {
                               "search": search_text.strip(),
                               "queryType": "semantic",
                               "semanticConfiguration": SEMANTIC_CONFIG,
                               "queryLanguage": "en-us",
                               "top": 5  # fetch more for better re-ranking
                           }
                            res = requests.post(
                               f"{AZURE_AI_SEARCH_ENDPOINT}/indexes/{AZURE_AI_SEARCH_INDEX_NAME}/docs/search?api-version=2023-07-01-Preview",
                               headers=headers,
                               json=candidate_payload
                           )
                            all_candidates = res.json().get("value", []) if res.status_code == 200 else []
                            print(all_candidates)
                           # Re-rank using OpenAI
                            candidates = azureopenai_recommendation_function.get_top_candidates_from_openai(search_text, all_candidates, top_n=3)
 
                        st.session_state[candidates_key] = candidates
 
                if unique_key in st.session_state.expanded_job_keys:
                    candidates = st.session_state.get(candidates_key, [])
                    if candidates:
                        for idx, cand in enumerate(candidates):
                            cand_key = f"{unique_key}_cand_{idx}"
                            name = cand.get("FullName", "N/A")
                            cand_loc = cand.get("Location", "N/A")
                            #score = cand.get("@search.rerankerScore", 0.0)
                            #percent = round((score / 4.0) * 100)
                            cand_score = cand.get("openai_score", "N/A")
                            bio_key = f"bio_{cand_key}"
                            skillgap_key = f"skillgap_{cand_key}"
 
                            st.markdown(f"**{name}** — {cand_loc}")
                            st.markdown(f"""
                                <div style="position: relative; background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
                                    <div style="background-color: #E60000; width: {cand_score}%; height: 100%;"></div>
                                    <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 20px; font-weight: bold; color: black;">
                                        {cand_score}% match
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
 
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("View Bio", key=f"btn_{bio_key}"):
                                    if bio_key in st.session_state.expanded_bio_keys:
                                        st.session_state.expanded_bio_keys.remove(bio_key)
                                    else:
                                        st.session_state.expanded_bio_keys.add(bio_key)
                            with col2:
                                if st.button("Skill Gaps Analysis", key=f"btn_{skillgap_key}"):
                                    if skillgap_key in st.session_state.expanded_skillgap_keys:
                                        st.session_state.expanded_skillgap_keys.remove(skillgap_key)
                                    else:
                                        st.session_state.expanded_skillgap_keys.add(skillgap_key)
                            # Below these buttons, add Career Timeline button and chart
                            if st.button("Career Timeline", key=f"btn_timeline_{cand_key}"):
                                fig = show_timeline_chart(cand)
                                if fig:
                                    st.markdown(f"### Career Timeline")
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Timeline data not available.")
 
                            if bio_key in st.session_state.expanded_bio_keys:
                                with st.expander(f"Profile Summary for {name}", expanded=True):
                                    bio = cand.get("ProfileSummary", "No bio available.")
                                    st.write(bio)
                                    skills = cand.get("Skills", "")
                                    st.markdown(f"**Skills:** {skills if skills else 'Not listed'}")
 
                            if skillgap_key in st.session_state.expanded_skillgap_keys:
                                with st.spinner(f"Analyzing skill gaps for {name}..."):
                                    jd_skill_payload = {
                                        "search": job_role,
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
 
                                    cand_skills_raw = cand.get("Skills", "")
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
 
                            st.markdown("---")
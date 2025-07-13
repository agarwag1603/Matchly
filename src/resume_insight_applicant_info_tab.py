import streamlit as st
import json
import plotly.graph_objects as go

def resume_insight(openai_response):
    print(openai_response)

    inner_tab1, inner_tab2 = st.tabs(["Resume Insights", "Applicant Info"])

    try:
        data = json.loads(openai_response)
        full_name= data.get("Full Name")
        education_list = data.get("Education", [])
        if not isinstance(education_list, list):
            education_list = [education_list]
        Work_Experience = data.get("Work Experience", [])
        if not isinstance(Work_Experience, list):
            Work_Experience = [Work_Experience]
        #Certifications = data.get("Certifications") or []
        certsdone_raw = data.get("Certifications")
        Certifications = [c.strip() for c in certsdone_raw.split(",")]
        GrammarCheckScore = data.get("GrammarCheck Score")
        FleschReadingScore=data.get("Flesch Reading Score",)
        certs_raw = data.get("Certifications Needed Based on Skills", "")
        CertificationsRecommendation = [c.strip() for c in certs_raw.split(",")]
        sections = data.get("Section Covered and Missing Score", {})
        covered = sections.get("Covered", [])
        missing = sections.get("Missing", [])
        values = [len(covered), len(missing)]
        ProfileSummary = data.get("Profile Summary",{})
        skills = data.get("Skills")
                        
    except json.JSONDecodeError:
        st.error("Failed to parse model response. Check if the JSON is valid.")
        st.stop()

    with inner_tab1:
        #Resume Insights
        st.markdown(f"""
            <div style="
                background-color: #f9f9f9;
                border-left: 5px solid #d10d0d;
                padding: 16px;
                border-radius: 8px;
                font-size: 16px;
                color: #333;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                margin: 10px 0;
            ">
                <strong>About {full_name}</strong><br>
                {ProfileSummary}
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        #Grammar score
        with col1:
            st.markdown(f"""
            <div style="
                background-color:#f9f9f9;
                width: 120px;
                height: 120px;
                border-radius: 12px;
                border-left: 4px solid #d10d0d;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: bold;
                color: #0d47a1;
            ">
                {GrammarCheckScore}
                <div style="font-size: 12px; color: #333; font-weight: normal; margin-top: 4px;">
                    Grammar Score
                </div>
            </div>
            """, unsafe_allow_html=True)
            #Flesch Reading Score
            with col2:
                st.markdown(f"""
                <div style="
                    background-color:#f9f9f9;
                    width: 120px;
                    height: 120px;
                    border-radius: 12px;
                    border-left: 4px solid #d10d0d;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: bold;
                    color: #0d47a1;
                            ">
                {FleschReadingScore}
                <div style="font-size: 12px; color: #333; font-weight: normal; margin-top: 4px;">
                    Flesch Reading Score
                </div>
            </div>
            """, unsafe_allow_html=True)
            #Section covered
            with col3:
                st.markdown(f"""
                <div style="
                    background-color:#f9f9f9;
                    width: 120px;
                    height: 120px;
                    border-radius: 12px;
                    border-left: 4px solid #d10d0d;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: bold;
                    color: #0d47a1;
                            ">
                {values[0]}
                <div style="font-size: 12px; color: #333; font-weight: normal; margin-top: 4px;">
                    Section Covered
                </div>
            </div>
            """, unsafe_allow_html=True)
            #Section missing
            with col4:
                st.markdown(f"""
                <div style="
                    background-color:#f9f9f9;
                    width: 120px;
                    height: 120px;
                    border-radius: 12px;
                    border-left: 4px solid #d10d0d;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: bold;
                    color: #0d47a1;
                            ">
                {values[1]}
                <div style="font-size: 12px; color: #333; font-weight: normal; margin-top: 4px;">
                    Section Missing
                </div>
            </div>
            """, unsafe_allow_html=True)
                
        labels = ['Covered', 'Missing']            
        custom_hover = [
            "<br>".join(covered),
            "<br>".join(missing)
        ]

        # Plotly pie chart with better colors
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hoverinfo='label+percent+text',
                textinfo='label+value',
                textfont_size=16,
                marker=dict(colors=['#f9f9f9', '#d10d0d']),  # grey and light blue
                hovertext=custom_hover
            )
        ])

        fig.update_layout(
            title='Resume Section Coverage',
            height=400
        )

        # Show in Streamlit
        st.plotly_chart(fig)

        # Optional: detailed list
        with st.expander("View Section Breakdown"):
            st.markdown("### Covered:")
            st.write(covered)

            st.markdown("### Missing:")
            st.write(missing)

    with inner_tab2:
        #Personal information in expander tab
        with st.expander("Personal Bio"):
            st.text_input("Full Name", value=data.get("Full Name", ""), key="full_name")
            st.text_input("Email", value=data.get("Email", ""), key="email")
            st.text_input("Phone", value=data.get("Phone", ""), key="phone")
            st.text_input("Location", value=data.get("Location", ""), key="location")
        
        for idx, edu in enumerate(education_list):
            with st.expander(f"Education Record {idx + 1}", expanded=(idx == 0)):
                st.text_input("Institution", value=edu.get("Institution", ""), key=f"institution_{idx}")
                st.text_input("Degree", value=edu.get("Degree", ""), key=f"degree_{idx}")
                st.text_input("Start Date", value=edu.get("Start Date", ""), key=f"start_date_edu{idx}")
                st.text_input("End Date", value=edu.get("End Date", ""), key=f"end_date_edu{idx}")
                st.text_input("GPA", value=edu.get("GPA", ""), key=f"gpa_{idx}")
        
        for idx, workexp in enumerate(Work_Experience):
            with st.expander(f"Work Experience Record {idx + 1}", expanded=(idx == 0)):
                st.text_input("Location", value=workexp.get("Location", ""), key=f"location_{idx}")
                st.text_input("Company", value=workexp.get("Company", ""), key=f"company_{idx}")
                st.text_input("Start Date", value=workexp.get("Start Date", ""), key=f"start_date_work{idx}")
                st.text_input("End Date", value=workexp.get("End Date", ""), key=f"end_date_work{idx}")
                st.text_input("Role", value=workexp.get("Role", ""), key=f"role_{idx}")

        if Certifications and Certifications[0].lower() not in ["none listed", "n/a", "none"]:
            st.subheader("Certifications")
            cols = st.columns(2)  # 2-column grid
            for i, cert in enumerate(Certifications):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="
                        background-color:#f9f9f9;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 10px;
                        border-left: 5px solid #d10d0d;
                        box-shadow: 1px 1px 8px rgba(0,0,0,0.05);
                    ">
                        <strong>{cert}</strong>
                    </div>
                    """, unsafe_allow_html=True)

        #recommendation for certification based on the skills
        if CertificationsRecommendation and CertificationsRecommendation[0].lower() not in ["none listed", "n/a", "none"]:
        #if CertificationsRecommendation not in ["None listed", "n/a", "None"]:
            st.markdown("### Recommended Certifications to Boost Your Profile")
    
            st.markdown(f"""
            <div style="
                background-color: #f9f9f9;
                border-left: 6px solid #d10d0d;
                padding: 20px;
                border-radius: 10px;
                margin-top: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.05);
            ">
                <ul style="list-style-type: '*'; padding-left: 20px; font-size: 16px;">
                    {''.join(f'<li>{rec}</li>' for rec in CertificationsRecommendation)}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        skills = [s.strip() for s in data.get("Skills", "").split(",")]
        if skills:
            st.markdown("### Detected Skills")
            badge_html = """
            <style>
            .badge {
            display: inline-block;
            background-color: #f9f9f9;
            color: #d10d0d;
            border-radius: 20px;
            padding: 6px 14px;
            margin: 6px 6px 0 0;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            }
            </style>
            <div>
            """
            for skill in skills:
                badge_html += f'<span class="badge">{skill}</span>'
            badge_html += "</div>"

            st.markdown(badge_html, unsafe_allow_html=True)

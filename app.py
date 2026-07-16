import tempfile
from pathlib import Path

import streamlit as st

from resumeAnalyzer import (
    ReadResume,
    parse_resume,
    final_score
)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")

st.write("Upload your resume and paste the Job Description.")

uploaded_resume = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

job_desc = st.text_area(
    "Paste Job Description",
    height=250,
    placeholder="Paste the complete Job Description here..."
)

if st.button("🚀 Analyze Resume"):

    if uploaded_resume is None:
        st.error("Please upload your resume.")
        st.stop()

    if job_desc.strip() == "":
        st.error("Please enter a Job Description.")
        st.stop()

    with st.spinner("Analyzing Resume..."):

        suffix = Path(uploaded_resume.name).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:

            temp.write(uploaded_resume.getvalue())
            temp_path = Path(temp.name)

        resume_text = ReadResume(temp_path)

        parsed_resume = parse_resume(resume_text)

        analysis = final_score(
            parsed_resume,
            job_desc
        )

    st.success("Analysis Completed Successfully!")

    st.divider()

    score = analysis.matchingScore

    st.subheader("🎯 Overall Match")

    st.metric(
        label="Resume Match",
        value=f"{score}%"
    )

    st.progress(score)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("👤 Personal Details")

        st.write(f"**Name:** {analysis.personalDetails.name}")
        st.write(f"**Email:** {analysis.personalDetails.email}")
        st.write(f"**Phone:** {analysis.personalDetails.phone}")

        if analysis.personalDetails.location:
            st.write(f"**Location:** {analysis.personalDetails.location}")

    with col2:

        st.subheader("📊 Score Breakdown")

        st.write("Skills")
        st.progress(analysis.scoreBreakdown.skills)

        st.write("Experience")
        st.progress(analysis.scoreBreakdown.experience)

        st.write("Education")
        st.progress(analysis.scoreBreakdown.education)

        st.write("Projects")
        st.progress(analysis.scoreBreakdown.projects)

    st.divider()

    st.subheader("❌ Missing Skills")

    if analysis.missingSkills:

        for skill in analysis.missingSkills:
            st.error(skill)

    else:

        st.success("No Missing Skills Found 🎉")

    st.divider()

    st.subheader("📝 Final Verdict")

    st.info(analysis.finalVerdict)

    # with st.expander("📄 Parsed Resume"):
    #     st.write(parsed_resume)

    with st.expander("🧾 Complete Analysis"):
        st.json(analysis.model_dump())
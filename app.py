import tempfile
from pathlib import Path

import streamlit as st

from resumeAnalyzer import (
    ReadResume,
    parse_resume,
    final_score,
    parse_job_description,
)

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("Hire Lens: AI-based Resume Analyzer")

st.write("Upload your resume and paste the Job Description.")

# -----------------------------
# Inputs
# -----------------------------

uploaded_resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

job_desc = st.text_area(
    "Paste Job Description",
    height=250,
    placeholder="Paste the complete Job Description here...",
)

# -----------------------------
# Analyze
# -----------------------------

if st.button("Analyze Resume"):
    if uploaded_resume is None:
        st.error("Please upload a resume.")
        st.stop()

    if job_desc.strip() == "":
        st.error("Please paste the Job Description.")
        st.stop()

    with st.spinner("Analyzing Resume..."):
        # Save uploaded file temporarily
        suffix = Path(uploaded_resume.name).suffix

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(uploaded_resume.getvalue())
            temp_path = Path(temp.name)

        # Read Resume
        resume_text = ReadResume(temp_path)

        # Parse Resume
        parsed_resume = parse_resume(resume_text)

        # parse Job Description
        parsed_JD = parse_job_description(job_desc)

        # Final Analysis
        analysis = final_score(parsed_resume, job_desc)

    st.success("Analysis Complete!")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Matching Score", f"{analysis.matchingScore}%")

    with col2:
        st.metric("Overall Percentage", f"{analysis.overallPercentage}%")

    st.progress(analysis.matchingScore)

    st.divider()

    st.subheader("👤 Personal Details")

    st.write(f"**Name:** {analysis.personalDetails.name}")
    st.write(f"**Email:** {analysis.personalDetails.email}")
    st.write(f"**Phone:** {analysis.personalDetails.phone}")

    if analysis.personalDetails.location:
        st.write(f"**Location:** {analysis.personalDetails.location}")

    st.divider()

    st.subheader("❌ Missing Skills")

    if analysis.missingSkills:
        for skill in analysis.missingSkills:
            st.write(f"• {skill}")
    else:
        st.success("No missing skills detected.")

    st.divider()

    st.subheader("📝 Final Verdict")

    st.success(analysis.finalVerdict)

    # with st.expander("Parsed Resume"):
    #     st.write(parsed_resume)

    with st.expander("Complete Analysis"):
        st.json(analysis.model_dump())

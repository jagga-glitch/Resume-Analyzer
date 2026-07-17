import tempfile
from pathlib import Path

import streamlit as st

from resumeAnalyzer import (
    ReadResume,
    parse_resume,
    final_score,
)

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="HireLens AI",
    page_icon="📄",
    layout="wide",
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
    background:#0f172a;
}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

.title{
font-size:52px;
font-weight:800;
text-align:center;
background:linear-gradient(90deg,#4F46E5,#06B6D4);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

.subtitle{
text-align:center;
font-size:18px;
color:#94a3b8;
margin-bottom:35px;
}

.card{
background:#1e293b;
padding:25px;
border-radius:18px;
box-shadow:0px 6px 25px rgba(0,0,0,.25);
margin-bottom:20px;
}

.metric{
font-size:55px;
font-weight:bold;
text-align:center;
color:#38bdf8;
}

.small{
font-size:16px;
font-weight:600;
color:white;
text-align:center;
margin-bottom:15px;
}

.footer{
text-align:center;
color:gray;
margin-top:40px;
}

.stButton>button{
width:100%;
background:linear-gradient(90deg,#4F46E5,#7C3AED);
color:white;
border:none;
padding:14px;
border-radius:12px;
font-size:18px;
font-weight:bold;
}

.stButton>button:hover{
background:linear-gradient(90deg,#4338CA,#6D28D9);
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown(
    "<div class='title'>HireLens AI</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='subtitle'>AI Resume Analyzer & ATS Score Checker</div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# FILE UPLOADER
# -------------------------------------------------

uploaded_file = st.file_uploader(
    "📄 Upload Resume",
    type=["pdf", "docx"],
)

# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------

if uploaded_file is not None:

    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        temp.write(uploaded_file.getvalue())

        temp_path = Path(temp.name)

    if st.button("🚀 Analyze Resume"):

        with st.spinner("Analyzing your resume..."):

            try:

                resume_text = ReadResume(temp_path)

                parsed_resume = parse_resume(resume_text)

                analysis = final_score(parsed_resume)

                st.success("Analysis Completed Successfully!")

                st.divider()

                left, right = st.columns([1, 2])

                # --------------------------
                # ATS SCORE
                # --------------------------

                with left:

                    st.markdown(
                        "<div class='card'>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "<div class='small'>ATS Score</div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"<div class='metric'>{analysis.overallPercentage}%</div>",
                        unsafe_allow_html=True,
                    )

                    st.progress(
                        analysis.overallPercentage / 100
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

                # --------------------------
                # PERSONAL DETAILS
                # --------------------------

                with right:

                    st.markdown(
                        "<div class='card'>",
                        unsafe_allow_html=True,
                    )

                    st.subheader("👤 Candidate Details")

                    c1, c2 = st.columns(2)

                    with c1:

                        st.write("**Name**")
                        st.write(
                            analysis.personalDetails.name
                        )

                        st.write("**Email**")
                        st.write(
                            analysis.personalDetails.email
                        )

                    with c2:

                        st.write("**Phone**")
                        st.write(
                            analysis.personalDetails.phone
                        )

                        st.write("**Location**")
                        st.write(
                            analysis.personalDetails.location
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

                st.divider()

                # --------------------------
                # BREAKDOWN
                # --------------------------

                st.subheader("📊 Score Breakdown")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Skills",
                        analysis.scoreBreakdown.skills,
                    )

                    st.progress(
                        analysis.scoreBreakdown.skills / 100
                    )

                    st.metric(
                        "Projects",
                        analysis.scoreBreakdown.projects,
                    )

                    st.progress(
                        analysis.scoreBreakdown.projects / 100
                    )

                with col2:

                    st.metric(
                        "Experience",
                        analysis.scoreBreakdown.experience,
                    )

                    st.progress(
                        analysis.scoreBreakdown.experience / 100
                    )

                    st.metric(
                        "Education",
                        analysis.scoreBreakdown.education,
                    )

                    st.progress(
                        analysis.scoreBreakdown.education / 100
                    )

                st.divider()

                # --------------------------
                # MISSING SKILLS
                # --------------------------

                st.subheader("❌ Missing Skills")

                if analysis.missingSkills:

                    cols = st.columns(3)

                    for i, skill in enumerate(
                        analysis.missingSkills
                    ):

                        cols[i % 3].info(skill)

                else:

                    st.success(
                        "No missing skills detected!"
                    )

                st.divider()

                # --------------------------
                # VERDICT
                # --------------------------

                st.subheader("📝 Final Verdict")

                if analysis.overallPercentage >= 80:

                    st.success("🎉 Excellent Match")

                elif analysis.overallPercentage >= 60:

                    st.warning("👍 Good Match")

                else:

                    st.error("⚠ Needs Improvement")

                st.write(analysis.finalVerdict)

                # --------------------------
                # RAW JSON
                # --------------------------

                with st.expander(
                    "🔍 View Raw JSON"
                ):

                    st.json(
                        analysis.model_dump()
                    )

            except Exception as e:

                st.error(f"❌ {e}")

            finally:

                if temp_path.exists():
                    temp_path.unlink()

st.markdown(
    """
<div class='footer'>
Built with ❤️ using Streamlit • Groq • Pydantic • Python
</div>
""",
    unsafe_allow_html=True,
)
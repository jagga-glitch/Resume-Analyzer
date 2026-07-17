import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from PyPDF2 import PdfReader
from docx import Document

from prompt import (
    system_prompt_HR,
    system_prompt_resume,
    system_prompt_finalScore,
    jobDesc,
)

# ----------------------------
# API Configuration
# ----------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)
model = "llama-3.3-70b-versatile"


# ----------------------------
# Pydantic Models
# ----------------------------


class JobDesc(BaseModel):
    role: str
    requiredSkills: str
    preferredSkills: str
    experience: str
    education: str
    responsibilties: str


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    responsibilities: str


class PersonalDetails(BaseModel):
    name: str
    phone: str
    email: str
    location: str | None = None


class Resume(BaseModel):
    personalDetails: PersonalDetails
    skills: str
    experience: list[Experience]
    projects: list[str]
    education: str


class ScoreBreakdown(BaseModel):
    skills: int
    experience: int
    education: int
    projects: int


class ResumeAnalyzer(BaseModel):
    personalDetails: PersonalDetails
    matchingScore: int
    missingSkills: list[str]
    overallPercentage: int
    scoreBreakdown: ScoreBreakdown
    finalVerdict: str


# ----------------------------
# Schemas
# ----------------------------

JDschema = JobDesc.model_json_schema()
ResumeSchema = Resume.model_json_schema()


# ----------------------------
# Resume Reader
# ----------------------------


def ReadResume(file_path: Path):

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")

    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    elif file_path.suffix.lower() == ".docx":
        doc = Document(file_path)

        return "\n".join(para.text for para in doc.paragraphs)

    else:
        raise ValueError("Only PDF and DOCX files are supported.")


# ----------------------------
# Parse Job Description
# ----------------------------


def parse_job_description(jobDesc):

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt_HR(JDschema),
            },
            {
                "role": "user",
                "content": jobDesc,
            },
        ],
    )

    return response.choices[0].message.content


# ----------------------------
# Parse Resume
# ----------------------------


def parse_resume(resume_text):

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt_resume(ResumeSchema),
            },
            {
                "role": "user",
                "content": resume_text,
            },
        ],
    )

    return response.choices[0].message.content


# ----------------------------
# Final Analysis
# ----------------------------


def final_score(parsed_resume, parsed_JD):

    parsed_JD = parse_job_description(jobDesc)
    parsed_resume = parse_resume(parsed_resume)

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt_finalScore(
                    parsed_resume,
                    parsed_JD,
                    ResumeAnalyzer.model_json_schema(),
                ),
            },
            {
                "role": "user",
                "content": "Analyze this resume.",
            },
        ],
    )

    result = response.choices[0].message.content

    data = json.loads(result)

    return ResumeAnalyzer(**data)

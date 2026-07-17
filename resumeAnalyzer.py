import os
from dotenv import load_dotenv
from pathlib import Path
from groq import Groq
from pydantic import BaseModel
from PyPDF2 import PdfReader
from docx import Document
import json
from prompt import (
    system_prompt_HR,
    system_prompt_resume,
    system_prompt_finalScore,
    jobDesc
)

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    my_api_key = st.secrets.get("GROQ_API_KEY")

client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"


class JobDesc(BaseModel):
    role: str
    requiredSkills: str
    preferredSkills: str
    experience: str
    education: str
    responsibilties: str


JDschema = JobDesc.model_json_schema()

response_format = {"type": "json_object"}

system_prompt = system_prompt_HR(JDschema)

message_system = {"role": "system", "content": system_prompt}

jobDesc = jobDesc

message = {"role": "user", "content": jobDesc}

messages = [message_system, message]

response = client.chat.completions.create(
    model=model, messages=messages, response_format=response_format
)

parsed_JD = response.choices[0].message.content


# print(parsed_JD)


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
    projects : list[str] 
    education: str
    
ResumeSchema = Resume.model_json_schema()


def ReadResume(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file_path.suffix.lower() == ".docx":
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

        
resume = ReadResume(Path("resume.pdf"))


def parse_resume(resume):
  response_format = {"type": "json_object"}
  
  system_prompt = system_prompt_resume(ResumeSchema)
  message_system = {
    "role" : "system",
    "content" : system_prompt
  }
  
  message = {
    "role": "user", 
    "content": resume
  }
  
  messages = [message_system, message]
  response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  answer = response.choices[0].message.content  
  return answer


parsed_resume = parse_resume(resume)


class PersonalDetails(BaseModel):
    name: str
    phone: str
    email: str
    location: str

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
    
def final_score(parsed_resume, jobDesc):
  response_format = {"type": "json_object"}
  prompt = system_prompt_finalScore(
    parsed_resume,
    parsed_JD,
    ResumeAnalyzer.model_json_schema()
)
  
  message_system = {
    "role" : "system",
    "content" : prompt
  }
  
  message = {
    "role": "user", 
    "content": "Analyze this resume"
  }

  messages = [message_system, message]
  
  response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  result = response.choices[0].message.content
  result = response.choices[0].message.content
  data = json.loads(result)
  return ResumeAnalyzer(**data)

# result = final_score(parsed_resume, jobDesc)
# raw_json = result
# data_file = json.loads(raw_json)
# resume_analysis = ResumeAnalyzer(**data_file)

# print(resume_analysis)


def main():
    resume_path = Path("resume.pdf")

    resume_text = ReadResume(resume_path)

    parsed_resume = parse_resume(resume_text)

    analysis = final_score(parsed_resume, jobDesc)

    print(analysis)
    
if __name__ == "__main__":
    main()
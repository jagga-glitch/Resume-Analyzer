# from resumeAnalyzer import JDschema, ResumeSchema, parsed_JD, parsed_resume, ResumeAnalyzer, final_score
def system_prompt_HR(schema):
  return f"""
You are a HR assistant. Extract the job description from the text strictly based on this schema and give in json:
{schema}
"""

def system_prompt_resume(schema):
  return f"""
You are a HR assistant. Extract the resume information from the text strictly based on this schema and give in json:
{schema}
"""
  
def system_prompt_finalScore(resume, jd, schema):
  return f"""
you are a hr assistant. Compare the resume information and job description and give a score out of 100 based on how well the resume matches the job description. Return the output based on the provided class in json format.Also break down the score based on skills, experience, education, projects and overall percentage. Also provide a final verdict based on the score.{resume}, {jd}, {schema}
""" 
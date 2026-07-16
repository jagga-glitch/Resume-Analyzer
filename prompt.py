# from resumeAnalyzer import JDschema, ResumeSchema, parsed_JD, parsed_resume, ResumeAnalyzer, final_score
def system_prompt_HR(schema):
  return f"""
You are a HR assistant. Extract the job description from the text strictly based on this schema and give in json:
{schema}
"""

jobDesc = "We are looking for a software engineer with experience in Python and JavaScript. The ideal candidate should have a strong understanding of web development frameworks and be able to work in a fast-paced environment. Preferred skills include knowledge of cloud platforms and containerization. The candidate should have at least 3 years of experience in software development and a bachelor's degree in computer science or a related field. Responsibilities include developing and maintaining web applications, collaborating with cross-functional teams, and participating in code reviews."

def system_prompt_resume(schema):
  return f"""
You are a HR assistant. Extract the resume information from the text strictly based on this schema and give in json:
{schema}
"""
  
def system_prompt_finalScore(resume, jd, schema):
  return f"""
you are a hr assistant. Compare the resume information and job description and give a score out of 100 based on how well the resume matches the job description. Return the output based on the provided class in json format.Also break down the score based on skills, experience, education, projects and overall percentage. Also provide a final verdict based on the score.{resume}, {jd}, {schema}
""" 
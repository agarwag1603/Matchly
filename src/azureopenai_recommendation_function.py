from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import json
 
load_dotenv()
 
OPENAI_ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT_URL")
AZUREOPEN_AI_DEPLOYMENT_NAME = os.getenv("AZUREOPEN_AI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
GPT_API_VERSION=os.getenv("GPT_API_VERSION")
 
AZUREOPENAI_CLIENT = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT_URL,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=GPT_API_VERSION
)
 
def get_top_candidates_from_openai(jd_text, candidate_docs, top_n=3):
   scored_candidates = []
 
   for idx, doc in enumerate(candidate_docs):
       full_name = doc.get("FullName", f"Candidate {idx+1}")
       profile = f"""
Name: {full_name}
Skills: {doc.get("Skills", '')}
Experience: {doc.get("ProfileSummary", '')}
Education: {doc.get("Education", '')}
Certifications: {doc.get("Certifications", '')}
Location: {doc.get("Location", '')}
       """
 
       system_prompt = """
You are a recruiter AI. Given a job description and a candidate profile, score how well the candidate matches the job on a scale of 0 to 100.
Be honest and critical. Provide a one-line reason. You should consider location also as a factor for closeness.
Return format:
openai_score: <number>
openai_score: <short reason>
"""
 
       user_prompt = f"""
Job Description:
{jd_text}
 
Candidate Profile:
{profile}
       """
 
       try:
           response = AZUREOPENAI_CLIENT.chat.completions.create(
               model=AZUREOPEN_AI_DEPLOYMENT_NAME,
               messages=[
                   {"role": "system", "content": system_prompt.strip()},
                   {"role": "user", "content": user_prompt.strip()}
               ],
               temperature=0.3,
               max_tokens=4000
           )
           content = response.choices[0].message.content
           score_line = [line for line in content.split("\n") if "score" in line.lower()]
           score = int(score_line[0].split(":")[-1].strip()) if score_line else 0
           doc["openai_score"] = score
           doc["openai_reason"] = content
           scored_candidates.append(doc)
       except Exception as e:
           print(f"OpenAI error for {full_name}: {e}")
 
   scored_candidates.sort(key=lambda x: x.get("openai_score", 0), reverse=True)
   #print(scored_candidates)
   return scored_candidates[:top_n]
 
def get_candidates_Skillmatch_openai(jd_Skills, candidate_skill):
   scored_candidates = []
   system_prompt = """
   Given the following job skills and candidate skills, match job skills and indicate their availability in candidate skills and return a JSON.
   If the candidate mentions a part of the language or skill, populate that skill as '✅' else populate '❌'.
   Additionally, if the job has a specific skill and the candidate has a broader category that includes that skill (e.g., Streamlit is part of Python), recognize the broader category.  
   Do not include any explanation or text outside the JSON.
   example output JSON: {"Skills":[abc,def],"Status":["✅ (Skill)","❌"]}
   My response should have exact number of skills and status values.
   Note: Strictly, keep as json, do NOT include any markdown formatting such as triple backticks (```), or any extra text. Output should be valid JSON only.
   """
   user_prompt = f"""
   Job Skills:
   {jd_Skills}
   Candidate Skills:
   {candidate_skill}"""
   try:
           response = AZUREOPENAI_CLIENT.chat.completions.create(
               model=AZUREOPEN_AI_DEPLOYMENT_NAME,
               messages=[
                   {"role": "system", "content": system_prompt.strip()},
                   {"role": "user", "content": user_prompt.strip()}
               ],
               temperature=0.3,
               max_tokens=4000
           )
           content = response.choices[0].message.content
           #print(content)
           #score_line = [line for line in content.split("\n") if "score" in line.lower()]
           #score = int(score_line[0].split(":")[-1].strip()) if score_line else 0
           #doc["openai_score"] = score
           #doc["openai_reason"] = content
           #scored_candidates.append(doc)
   except Exception as e:
           print(f"OpenAI error for : {e}")
 
   #scored_candidates.sort(key=lambda x: x.get("openai_score", 0), reverse=True)
   #print(scored_candidates)
   return content
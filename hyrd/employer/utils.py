from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional, List
import pathlib
from sentence_transformers import SentenceTransformer, util
import spacy
import dateparser
import re
from typing import List, Dict
import os

class RequirementSchema(BaseModel):
    educational: Optional[str] = None
    technical: Optional[str] = None
    experience: Optional[str] = None

class JobSchema(BaseModel):
    job_title: Optional[str] = None
    job_type: Optional[str] = None
    about_the_company: Optional[str] = None
    job_summary: Optional[str] = None
    location: Optional[str] = None
    compensation: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    requirements: Optional[RequirementSchema] = None
    preferred_qualifications: Optional[List[str]] = None

class Location(BaseModel):
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None

class Profile(BaseModel):
    network: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None

class Basics(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = None

class Work(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

class Volunteer(BaseModel):
    organization: Optional[str] = None
    position: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

class Education(BaseModel):
    institution: Optional[str] = None
    url: Optional[str] = None
    area_of_study: Optional[str] = None
    study_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    score: Optional[str] = None
    courses: Optional[List[str]] = None

class Award(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    awarder: Optional[str] = None
    summary: Optional[str] = None

class Certificate(BaseModel):
    name: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None
    url: Optional[str] = None

class Publication(BaseModel):
    name: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None

class Skill(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    keywords: Optional[List[str]] = None

class Language(BaseModel):
    language: Optional[str] = None
    fluency: Optional[str] = None

class Interest(BaseModel):
    name: Optional[str] = None
    keywords: Optional[List[str]] = None

class Reference(BaseModel):
    name: Optional[str] = None
    reference: Optional[str] = None

class Project(BaseModel):
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[List[str]] = None
    url: Optional[str] = None

class Resume(BaseModel):
    basics: Optional[Basics] = None
    work: List[Work] = None
    volunteer: Optional[List[Volunteer]] = None
    education: Optional[List[Education]] = None
    awards: Optional[List[Award]] = None
    certificates: Optional[List[Certificate]] = None
    publications: Optional[List[Publication]] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    interests: Optional[List[Interest]] = None
    references: Optional[List[Reference]] = None
    projects: Optional[List[Project]] = None


jd_prompt = """You are provided with a PDF of a Job Description and a schema. Your objective is to extract the relevant structured data from the text and format it as a JSON object. Ensure that the extracted data aligns strictly with the given schema. If any information is missing or not explicitly stated, leave the corresponding field empty or null. Aim to capture as much detail as possible from the text."""
def extract_job_description(pdf_path, prompt=jd_prompt):
    client = genai.Client(api_key="AIzaSyADWAdw5IonFBGhA0uORz_LDkVR4CXdVws")
    filepath = pathlib.Path(pdf_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=JobSchema
        ),
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ]
    )
    data: JobSchema = response.parsed
    return data.model_dump()


resume_prompt = """You are provided with a PDF of a Resume and a schema. Your objective is to extract the relevant structured data from the text and format it as a JSON object. Ensure that the extracted data aligns strictly with the given schema. If any information is missing or not explicitly stated, leave the corresponding field empty or null. Aim to capture as much detail as possible from the text."""
def extract_resume(pdf_path, prompt=resume_prompt):
    client = genai.Client(api_key="AIzaSyADWAdw5IonFBGhA0uORz_LDkVR4CXdVws")
    filepath = pathlib.Path(pdf_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=Resume
        ),
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ]
    )
    data: Resume = response.parsed
    return data.model_dump()

# job_description=extract_job_description('/content/Software Engineer Intern.pdf')

# resumes = [extract_resume(os.path.join('/content/', res)) for res in os.listdir('/content/') if res.endswith('.pdf')]

# # Initialize models
# SEMANTIC_MODEL = SentenceTransformer("all-mpnet-base-v2")
# nlp = spacy.load("en_core_web_sm")

# class ResumeMatcher:
#     def __init__(self):
#         self.weights = {
#             'title': 0.15,
#             'summary': 0.15,
#             'responsibilities': 0.20,
#             'requirements': 0.20,
#             'skills': 0.15,
#             'experience': 0.10,
#             'education': 0.05,
#         }

#     def preprocess_text(self, text: str) -> str:
#         """Clean and normalize text input."""
#         if not text:
#             return ""
#         text = re.sub(r'[^\w\s-]', '', text.lower())
#         text = re.sub(r'\s+', ' ', text).strip()
#         return text

#     def extract_entities(self, text: str) -> Dict:
#         """Extract skills, education, and locations using spaCy NER."""
#         doc = nlp(text)
#         return {
#             'skills': list(set([ent.text for ent in doc.ents if ent.label_ == 'SKILL'])),
#             'degrees': list(set([ent.text for ent in doc.ents if ent.label_ == 'DEGREE'])),
#             'locations': list(set([ent.text for ent in doc.ents if ent.label_ == 'GPE']))
#         }

#     def calculate_experience(self, work_history: List[Dict]) -> float:
#         """Calculate total years of experience with date parsing."""
#         total_days = 0
#         for position in work_history:
#             start = dateparser.parse(position.get('Start Date', ''))
#             end = dateparser.parse(position.get('End Date', '') or 'now')
#             if start and end:
#                 total_days += (end - start).days
#         return round(total_days / 365.25, 1)

#     def calculate_similarity(self, text1: str, text2: str) -> float:
#         """Calculate semantic similarity score using SBERT."""
#         emb1 = SEMANTIC_MODEL.encode(self.preprocess_text(text1))
#         emb2 = SEMANTIC_MODEL.encode(self.preprocess_text(text2))
#         return util.pytorch_cos_sim(emb1, emb2).item()

#     def match_job_resume(self, job: Dict, resume: Dict) -> Dict:
#         """Main matching function with hybrid scoring."""

#         # Preprocess job description sections
#         job_text = {
#             "title": self.preprocess_text(job.get("Job Title", "")),
#             "summary": self.preprocess_text(job.get("Job Summary", "")),
#             "responsibilities": self.preprocess_text(job.get("Responsibilities", "")),
#             "requirements": self.preprocess_text(
#                 " ".join([
#                     job.get("Requirements", {}).get("Educational", ""),
#                     job.get("Requirements", {}).get("Technical", ""),
#                     job.get("Requirements", {}).get("Experience (Years of experience)", "")
#                 ])
#             ),
#             "preferred": self.preprocess_text(job.get("Preferred Qualifications", "")),
#             "location": self.preprocess_text(job.get("Location", "")),
#         }

#         # Preprocess resume sections
#         resume_text = {
#             "summary": self.preprocess_text(resume.get("Basics", {}).get("Summary", "")),
#             "work": self.preprocess_text(
#                 " ".join([
#                     work.get("Summary", "") + " ".join(work.get("Highlights", []))
#                     for work in resume.get("Work", [])
#                 ])
#             ),
#             "education": self.preprocess_text(
#                 " ".join([
#                     edu.get("Area of Study", "") + edu.get("Study Type", "")
#                     for edu in resume.get("Education", [])
#                 ])
#             ),
#             "skills": self.preprocess_text(
#                 " ".join([skill.get("Name", "") for skill in resume.get("Skills", [])])
#             ),
#         }

#         # Calculate individual scores using semantic similarity and overlap
#         scores = {
#             'title': self.calculate_similarity(job_text['title'], resume_text['summary']) * 100,

#             'summary': self.calculate_similarity(job_text['summary'], resume_text['summary']) * 100,

#             'responsibilities': self.calculate_similarity(job_text['responsibilities'], resume_text['work']) * 100,

#             'requirements': self.calculate_similarity(job_text['requirements'], resume_text['work']) * 100,

#             'skills': len(set(job_text['requirements'].split()) & set(resume_text['skills'].split())) /
#                       len(job_text['requirements'].split()) * 100 if job_text['requirements'] else 0,

#             'experience': min(
#                 self.calculate_experience(resume.get('Work', [])) /
#                 float(job.get('Requirements', {}).get('Experience (Years of experience)', 1)) * 100,
#                 100
#             ),

#             'education': 100 if any(
#                 edu in job.get('Requirements', {}).get('Educational', '')
#                 for edu in resume_text['education'].split()
#             ) else 0,
#         }

#         # Calculate weighted score
#         weighted_score = sum(
#             scores[category] * weight
#             for category, weight in self.weights.items()
#         )

#         # Generate missing items report
#         missing = {
#             'skills': list(set(job_text['requirements'].split()) - set(resume_text['skills'].split())),
#             'education': job.get('Requirements', {}).get('Educational', '') if not scores['education'] else [],
#             'experience_gap': max(
#                 float(job.get('Requirements', {}).get('Experience (Years of experience)', 0)) -
#                 self.calculate_experience(resume.get('Work', [])),
#                 0
#             )
#         }

#         return {
#             'score': round(weighted_score, 2),
#             'details': scores,
#             'missing': missing
#         }

#     def rank_resumes(self, job: Dict, resumes: List[Dict]) -> List[Dict]:
#         """Rank resumes by match quality."""

#         ranked = []

#         for resume in resumes:

#             result = self.match_job_resume(job, resume)
#             ranked.append({
#                 'name': resume.get('Basics', {}).get('Name', 'Unnamed'),
#                 'score': result['score'],
#                 'details': result['details'],
#                 'missing': result['missing']
#             })

#         # Sort resumes by score in descending order
#         ranked = sorted(ranked, key=lambda x: x['score'], reverse=True)

#         return ranked


#     # Instantiate the matcher
# matcher = ResumeMatcher()

# # Rank resumes for the given job description
# ranked_resumes = matcher.rank_resumes(job_description, resumes)

# # Display results
# print("Resume Ranking Results:\n")
# for idx, candidate in enumerate(ranked_resumes, 1):
#     print(f"{idx}. {candidate['name']} - Score: {candidate['score']}%")
#     print(f"Details: {candidate['details']}")
#     print(f"Missing: {candidate['missing']}\n")


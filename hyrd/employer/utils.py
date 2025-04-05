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
    work: Optional[List[Work]] = None
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

jd_prompt = """You are a specialized information extraction system designed to parse job descriptions from PDF documents and convert them into structured JSON data.

## TASK
Extract all relevant information from the attached job description PDF and organize it according to the provided schema. Return ONLY a valid JSON object without any additional text, explanation, or markdown formatting.

## EXTRACTION GUIDELINES
- Extract information as accurately as possible from the provided PDF
- For list fields like "responsibilities" and "preferred_qualifications", separate distinct items into array elements
- If information for a field is not explicitly found in the PDF, set that field to null
- Use your best judgment to categorize requirements into "educational", "technical", and "experience"
- Avoid fabricating information; only extract what's present in the document
- Maintain formatting of the original text when appropriate (e.g., don't change "Bachelor's degree" to "bachelor degree")
- For the "about_the_company" field, include information about the company's mission, values, and background
- For "job_summary", capture the overall description of the role

## SPECIAL CONSIDERATIONS
- Pay attention to sections that may have different headings but contain relevant information (e.g., "What You'll Do" might contain responsibilities)
- When extracting compensation, include salary ranges, benefits, and any additional compensation information
- Location information may include remote options, specific cities, or regions
- Job type may be full-time, part-time, contract, etc.

## OUTPUT FORMAT
Return a single, valid JSON object that conforms to the provided schema:
- All fields should be populated if information is available
- Maintain the exact field names as specified in the schema
- Ensure all lists are properly formatted as JSON arrays
- The "requirements" field should be an object with the three specified subfields
"""
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


# resume_prompt = """You are provided with a PDF of a Resume and a schema. Your objective is to extract the relevant structured data from the text and format it as a JSON object. Ensure that the extracted data aligns with the given schema. If any information is missing or not explicitly stated, leave the corresponding field empty or null. Aim to capture as much detail as possible from the text."""
resume_prompt = """"You are a specialized information extraction system designed to parse resumes from PDF documents and convert them into structured JSON data.

## TASK
Extract all relevant information from the attached resume PDF and organize it according to the provided schema. Return ONLY a valid JSON object without any additional text, explanation, or markdown formatting.

## EXTRACTION GUIDELINES
- Extract information as accurately as possible from the provided PDF
- For list fields like "highlights", "courses", and "keywords", separate distinct items into array elements
- If information for a field is not explicitly found in the PDF, set that field to null
- Preserve the original formatting of names, titles, and technical terms
- Extract dates in the format provided in the resume; don't attempt to standardize date formats
- For contact information, ensure privacy by extracting exactly what's in the document without modification
- For work experiences, education, and other time-based entries, list them in reverse chronological order (most recent first)

## SPECIAL CONSIDERATIONS
- Personal information (basics): Extract name, job title (label), contact information, and professional summary
- Work experiences: Capture company names, positions, dates, and accomplishments/responsibilities as highlights
- Education: Include institutions, degrees, majors, dates, and relevant coursework
- Skills: Group technical skills, soft skills, and tools/technologies appropriately
- Projects: Extract both professional and personal projects with descriptions and key achievements
- Social profiles: Look for LinkedIn, GitHub, portfolio websites, and other professional networks
- Languages: Note both human languages and programming languages appropriately
- When extracting locations, separate the components (city, region, country) when possible
- Look for skill levels or proficiency indicators (e.g., "expert in", "familiar with")

## OUTPUT FORMAT
Return a single, valid JSON object that conforms to the provided schema:
- All fields should be populated if information is available
- Maintain the exact field names as specified in the schema
- Ensure all dates follow a consistent format within the output
- Nested objects (like Location within Basics) should be properly structured
- List items should be formatted as JSON arrays
- Avoid duplicate entries across different sections
"""
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


class ResumeRanker:
    def __init__(self):
        # Initialize the semantic model for similarity calculations
        self.SEMANTIC_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Define weights for different matching criteria
        self.weights = {
            'title': 0.1,
            'summary': 0.1,
            'responsibilities': 0.2,
            'requirements': 0.2,
            'skills': 0.2,
            'experience': 0.1,
            'education': 0.1
        }
        
        # Load NLP model for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def preprocess_text(self, text):
        """Clean and normalize text for better matching."""
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase and remove extra whitespace
        text = re.sub(r'\s+', ' ', text.lower().strip())
        return text

    def extract_entities(self, text: str) -> Dict:
        """Extract skills, education, and locations using spaCy NER."""
        doc = self.nlp(text)
        return {
            'skills': list(set([ent.text for ent in doc.ents if ent.label_ == 'SKILL'])),
            'degrees': list(set([ent.text for ent in doc.ents if ent.label_ == 'DEGREE'])),
            'locations': list(set([ent.text for ent in doc.ents if ent.label_ == 'GPE']))
        }

    def calculate_experience(self, work_history: List[Dict]) -> float:
        """Calculate total years of experience with date parsing."""
        total_days = 0
        for position in work_history:
            start = dateparser.parse(position.get('Start Date', ''))
            end = dateparser.parse(position.get('End Date', '') or 'now')
            if start and end:
                total_days += (end - start).days
        return round(total_days / 365.25, 1)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity score using SBERT."""
        emb1 = self.SEMANTIC_MODEL.encode(self.preprocess_text(text1))
        emb2 = self.SEMANTIC_MODEL.encode(self.preprocess_text(text2))
        return util.cos_sim(emb1, emb2).item()

    def match_job_resume(self, job: Dict, resume: Dict) -> Dict:
        """Main matching function with hybrid scoring."""

        job_text = {
            "title": self.preprocess_text(job.get("Job Title", "")),
            "summary": self.preprocess_text(job.get("Job Summary", "")),
            "responsibilities": self.preprocess_text(job.get("Responsibilities", "")),
            "requirements": self.preprocess_text(
                " ".join([
                    job.get("Requirements", {}).get("Educational", ""),
                    job.get("Requirements", {}).get("Technical", ""),
                    job.get("Requirements", {}).get("Experience (Years of experience)", "")
                ])
            ),
            "preferred": self.preprocess_text(job.get("Preferred Qualifications", "")),
            "location": self.preprocess_text(job.get("Location", "")),
        }

        resume_text = {
            "summary": self.preprocess_text(resume.get("Basics", {}).get("Summary", "")),
            "work": self.preprocess_text(
                " ".join([
                    work.get("Summary", "") + " ".join(work.get("Highlights", []))
                    for work in resume.get("Work", [])
                ])
            ),
            "education": self.preprocess_text(
                " ".join([
                    edu.get("Area of Study", "") + edu.get("Study Type", "")
                    for edu in resume.get("Education", [])
                ])
            ),
            "skills": self.preprocess_text(
                " ".join([skill.get("Name", "") for skill in resume.get("Skills", [])])
            ),
        }

        scores = {
            'title': self.calculate_similarity(job_text['title'], resume_text['summary']) * 100,
            'summary': self.calculate_similarity(job_text['summary'], resume_text['summary']) * 100,
            'responsibilities': self.calculate_similarity(job_text['responsibilities'], resume_text['work']) * 100,
            'requirements': self.calculate_similarity(job_text['requirements'], resume_text['work']) * 100,
            'skills': len(set(job_text['requirements'].split()) & set(resume_text['skills'].split())) /
                      max(len(job_text['requirements'].split()), 1) * 100 if job_text['requirements'] else 0,
        }
        
        # Fix for division by zero error
        required_experience = float(job.get('Requirements', {}).get('Experience (Years of experience)', 1) or 1)
        candidate_experience = self.calculate_experience(resume.get('Work', []))
        
        # Calculate experience score safely
        if required_experience > 0:
            experience_score = min(candidate_experience / required_experience * 100, 100)
        else:
            # If no experience required, give full score if candidate has any experience
            experience_score = 100 if candidate_experience > 0 else 0
        
        scores['experience'] = experience_score
        
        scores['education'] = 100 if any(
            edu in job.get('Requirements', {}).get('Educational', '')
            for edu in resume_text['education'].split()
        ) else 0

        weighted_score = sum(
            scores[category] * weight
            for category, weight in self.weights.items()
        )

        # Fix for experience gap calculation
        required_exp = float(job.get('Requirements', {}).get('Experience (Years of experience)', 0) or 0)
        experience_gap = max(required_exp - candidate_experience, 0)

        missing = {
            'skills': list(set(job_text['requirements'].split()) - set(resume_text['skills'].split())),
            'education': job.get('Requirements', {}).get('Educational', '') if not scores['education'] else [],
            'experience_gap': experience_gap
        }

        return {
            'score': round(weighted_score, 2),
            'details': scores,
            'missing': missing
        }

    def rank_resumes(self, job: Dict, resumes: List[Dict]) -> List[Dict]:
        """Rank resumes by match quality."""

        ranked = []

        for resume in resumes:

            result = self.match_job_resume(job, resume)
            ranked.append({
                'name': resume.get('Basics', {}).get('Name', 'Unnamed'),
                'score': result['score'],
                'details': result['details'],
                'missing': result['missing']
            })

        ranked = sorted(ranked, key=lambda x: x['score'], reverse=True)

        return ranked
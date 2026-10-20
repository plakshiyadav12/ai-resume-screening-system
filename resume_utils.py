import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python", "java", "c++", "javascript", "react", "flask",
    "django", "sql", "sqlite", "mysql", "mongodb", "html",
    "css", "machine learning", "deep learning", "data analysis",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "nlp", "natural language processing", "rest api", "git",
    "github", "docker", "aws", "azure", "power bi", "excel",
    "data visualization", "statistics", "fastapi", "streamlit",
]


def extract_skills(text):
    """Extract recognized skills using case-insensitive whole-word matching."""
    normalized = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))


def calculate_similarity(resume_text, job_text):
    """Return TF-IDF cosine similarity between resume and job description."""
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([resume_text, job_text])

    return float(
        cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    )


def analyze_resume(resume_text, job_text, required_skills=None):
    """Calculate an explainable heuristic match score for one resume."""
    required_skills = required_skills or []

    candidate_skills = extract_skills(resume_text)
    target_skills = [
        skill.strip().lower()
        for skill in required_skills
        if skill.strip()
    ]

    if not target_skills:
        target_skills = extract_skills(job_text)

    target_skills = list(dict.fromkeys(target_skills))

    matched_skills = [
        skill for skill in target_skills
        if skill in candidate_skills
    ]
    missing_skills = [
        skill for skill in target_skills
        if skill not in candidate_skills
    ]

    skill_score = (
        len(matched_skills) / len(target_skills)
        if target_skills else 0.0
    )

    try:
        text_score = calculate_similarity(resume_text, job_text)
    except ValueError:
        text_score = 0.0

    final_score = (0.60 * skill_score + 0.40 * text_score) * 100

    return {
        "score": round(final_score, 2),
        "skill_score": round(skill_score * 100, 2),
        "text_score": round(text_score * 100, 2),
        "skills": candidate_skills,
        "matched": matched_skills,
        "missing": missing_skills,
    }

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# NORMALIZE TEXT
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# -------------------------------
# SKILL SYNONYMS (VERY IMPORTANT)
# -------------------------------
SKILL_MAP = {
    "machine learning": ["ml"],
    "powerbi": ["power bi", "power-bi"],
    "javascript": ["js"],
    "node": ["nodejs"],
    "react": ["reactjs"],
    "python": ["py"],
    "sql": ["mysql", "postgresql"]
}

# -------------------------------
# EXPAND TEXT WITH SYNONYMS
# -------------------------------
def expand_text(text):
    text = clean_text(text)

    for main_skill, variants in SKILL_MAP.items():
        for v in variants:
            if v in text:
                text += f" {main_skill}"

    return text

# -------------------------------
# SKILLS
# -------------------------------
COMMON_SKILLS = {
    # Data
    "python","pandas","numpy","sql","machine learning","statistics",
    "excel","powerbi","tableau",

    # Backend
    "java","spring","api","node","express","database",

    # Frontend
    "html","css","javascript","react","angular",

    # DevOps
    "aws","docker","kubernetes","ci","cd",

    # General
    "git","github"
}

# -------------------------------
# EXTRACT SKILLS (SMART MATCHING)
# -------------------------------
def extract_skills(text):
    text = expand_text(text)
    found = set()

    for skill in COMMON_SKILLS:
        if skill in text:
            found.add(skill)

    return found

# -------------------------------
# MATCHED SKILLS
# -------------------------------
def get_matched_skills(resume, jd):
    return list(extract_skills(resume) & extract_skills(jd))

def get_missing_skills(resume, jd):
    return list(extract_skills(jd) - extract_skills(resume))

# -------------------------------
# FINAL SCORING
# -------------------------------
def calculate_similarities(resume, job_list):
    results = []

    resume_expanded = expand_text(resume)

    for jd in job_list:

        jd_expanded = expand_text(jd)

        matched = extract_skills(resume) & extract_skills(jd)
        required = extract_skills(jd)

        # Skill score
        if len(required) == 0:
            skill_score = 0
        else:
            skill_score = (len(matched) / len(required)) * 100

        # TF-IDF score
        text = [resume_expanded, jd_expanded]
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(text)

        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0] * 100

        # Final score (balanced)
        final_score = (0.75 * skill_score) + (0.25 * tfidf_score)

        results.append(round(final_score, 2))

    return results
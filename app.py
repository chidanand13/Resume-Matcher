import streamlit as st
import pandas as pd
import PyPDF2
from matcher import calculate_similarities, get_missing_skills, get_matched_skills

st.set_page_config(page_title="AI Career Assistant")

st.title("🧠 AI Resume Analyzer + Career Advisor")
st.info("Upload or paste your resume to get job matches + career guidance 🚀")

# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])

resume = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                resume += text
    else:
        resume = uploaded_file.read().decode("utf-8")

resume_text = st.text_area("Or paste your resume here:", height=200)

if resume_text:
    resume = resume_text

# -------------------------------
# JOB DATA
# -------------------------------
jobs_df = pd.read_csv("jobs.csv")

# -------------------------------
# CAREER SUGGESTION
# -------------------------------
def suggest_career(resume):
    text = resume.lower()

    if "machine learning" in text or "tensorflow" in text:
        return "ML Engineer"
    elif "pandas" in text or "numpy" in text:
        return "Data Scientist"
    elif "sql" in text and "excel" in text:
        return "Data Analyst"
    elif "java" in text or "spring" in text:
        return "Backend Developer"
    elif "html" in text or "css" in text:
        return "Frontend Developer"
    elif "docker" in text or "aws" in text:
        return "DevOps Engineer"
    else:
        return "General Role"

# -------------------------------
# MAIN
# -------------------------------
if st.button("Analyze Resume"):

    if resume.strip() == "":
        st.warning("⚠️ Please upload or enter your resume")
    else:
        st.success("Analyzing... 🔄")

        st.subheader("🎯 Suggested Career:")
        st.success(suggest_career(resume))

        scores = calculate_similarities(resume, jobs_df["description"].tolist())
        jobs_df["match_score"] = scores
        jobs_df = jobs_df.sort_values(by="match_score", ascending=False)

        st.subheader("🔍 Top Matches:")

        for _, row in jobs_df.head(5).iterrows():

            score = row["match_score"]

            st.write(f"### {row['job_title']} — {score}%")

            if score > 80:
                st.success("Excellent Match 🚀")
            elif score > 50:
                st.warning("Moderate Match ⚠️")
            else:
                st.error("Low Match ❌")

            st.progress(int(score))

            matched = get_matched_skills(resume, row["description"])
            missing = get_missing_skills(resume, row["description"])

            st.write("✅ Matched:", ", ".join(matched))
            st.write("❌ Missing:", ", ".join(missing))

            st.markdown("---")
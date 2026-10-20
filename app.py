
import re
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

from resume_utils import analyze_resume

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
)



def extract_pdf_text(uploaded_file):
    """Extract selectable text from an uploaded PDF."""
    text_parts = []

    with fitz.open(stream=uploaded_file.getvalue(), filetype="pdf") as pdf:
        for page in pdf:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()





st.title("📄 AI Resume Screening System")
st.caption("Resume analysis, skill-gap identification, and job matching")

with st.sidebar:
    st.header("About the project")
    st.write(
        "This application uses text similarity and a predefined "
        "technical-skill dictionary. Its scores are screening aids, "
        "not predictions of job performance."
    )

st.subheader("1. Enter the job requirements")

job_desc = st.text_area(
    "Job description",
    height=180,
    placeholder="Paste the job description here...",
)

required_skills_input = st.text_input(
    "Required skills (comma-separated)",
    placeholder="Python, SQL, Flask, Machine Learning",
)

st.subheader("2. Add candidate resumes")

input_method = st.radio(
    "Resume input method",
    ["Upload PDF files", "Paste resume text"],
    horizontal=True,
)

resumes = []

if input_method == "Upload PDF files":
    uploaded_files = st.file_uploader(
        "Upload one or more resumes",
        type=["pdf"],
        accept_multiple_files=True,
        help="Text-based PDFs are supported. Scanned PDFs may need OCR.",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                extracted_text = extract_pdf_text(uploaded_file)

                if extracted_text:
                    resumes.append(
                        {
                            "name": uploaded_file.name,
                            "text": extracted_text,
                        }
                    )
                else:
                    st.warning(
                        f"No selectable text found in {uploaded_file.name}. "
                        "It may be scanned or image-only."
                    )
            except Exception:
                st.error(
                    f"Could not read {uploaded_file.name}. "
                    "Please check that it is a valid PDF."
                )
else:
    candidate_name = st.text_input(
        "Candidate name",
        value="Sample Candidate",
    )
    resume_text = st.text_area(
        "Resume text",
        height=220,
        placeholder="Paste resume text here...",
    )

    if resume_text.strip():
        resumes.append(
            {"name": candidate_name.strip() or "Unnamed Candidate",
             "text": resume_text}
        )

if st.button("Analyze resumes", type="primary"):
    if not job_desc.strip():
        st.warning("Please enter a job description.")
    elif not resumes:
        st.warning("Please upload a readable PDF or paste resume text.")
    else:
        required_skills = [
            item.strip().lower()
            for item in required_skills_input.split(",")
            if item.strip()
        ]

        # Remove duplicate requirements while preserving their order.
        required_skills = list(dict.fromkeys(required_skills))

        results = []

        for resume in resumes:
          analysis = analyze_resume(
            resume_text=resume["text"],
            job_text=job_desc,
            required_skills=required_skills,
            )

          results.append({
           "name": resume["name"],
           "score": analysis["score"],
           "skill_score": analysis["skill_score"],
           "text_score": analysis["text_score"],
           "matched": analysis["matched"],
           "missing": analysis["missing"],
           "skills": analysis["skills"],
           "text": resume["text"],
        })

        results.sort(key=lambda item: item["score"], reverse=True)

        

        # Prepare candidate results for download
        export_data = []

        for rank, result in enumerate(results, start=1):
          export_data.append({
          "Rank": rank,
          "Candidate": result["name"],
          "Overall Match (%)": result["score"],
          "Skill Coverage (%)": result["skill_score"],
          "Text Similarity (%)": result["text_score"],
          "Matched Skills": ", ".join(result["matched"]),
          "Missing Skills": ", ".join(result["missing"]),
          "Detected Skills": ", ".join(result["skills"]),
        })

        export_df = pd.DataFrame(export_data)

        st.download_button(
          label="Download Candidate Ranking (CSV)",
          data=export_df.to_csv(index=False).encode("utf-8-sig"),
          file_name="candidate_ranking.csv",
          mime="text/csv",
        )        

        st.subheader("3. Candidate ranking")

        if not target_skills:
            st.info(
                "No recognized target skills were found. "
                "Add required skills to enable skill-coverage scoring."
            )

        for index, result in enumerate(results, start=1):
            with st.expander(
                f"#{index} — {result['name']} "
                f"({result['score']}% match)",
                expanded=(index == 1),
            ):
                col1, col2, col3 = st.columns(3)

                col1.metric("Overall match", f"{result['score']}%")
                col2.metric("Skill coverage", f"{result['skill_score']}%")
                col3.metric("Text similarity", f"{result['text_score']}%")

                st.write("**Detected skills**")
                st.write(
                    ", ".join(result["skills"])
                    if result["skills"] else "No known skills detected."
                )

                st.write("**Matching required skills**")
                st.write(
                    ", ".join(result["matched"])
                    if result["matched"] else "No matching skills detected."
                )

                st.write("**Required skills not detected**")
                st.write(
                    ", ".join(result["missing"])
                    if result["missing"] else "All listed target skills detected."
                )

                with st.expander("Review extracted resume text"):
                    st.text(result["text"])

        st.caption(
            "Scores use a fixed skill dictionary and TF-IDF similarity. "
            "Undetected skills may still be present in a resume. "
            "Review the source text before drawing conclusions."
        )

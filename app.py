




import streamlit as st
import re
import os
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from groq import Groq
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================= TESSERACT =================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= STORAGE =================
TXT_FOLDER = "extracted_texts"
os.makedirs(TXT_FOLDER, exist_ok=True)

# ================= UI CONFIG =================
st.set_page_config(
    page_title="AI Resume Compatibility Checker",
    layout="centered",
    page_icon="📄"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    backdrop-filter: blur(10px);
}
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 14px;
    font-size: 18px;
    height: 3em;
    font-weight: bold;
    border: none;
}
.stProgress > div > div {
    background: linear-gradient(90deg, #00ff87, #60efff);
}
</style>
""", unsafe_allow_html=True)

# ================= TEXT EXTRACTION =================
def extract_text_from_pdf(pdf):
    reader = PdfReader(pdf)
    return " ".join([p.extract_text() or "" for p in reader.pages])

def extract_text_from_image(img):
    return pytesseract.image_to_string(Image.open(img).convert("L"))

def save_to_txt(text):
    filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(os.path.join(TXT_FOLDER, filename), "w", encoding="utf-8") as f:
        f.write(text)

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

# ================= SKILL EXTRACTION (UI ONLY) =================
def extract_skills(text):
    skills = [
        "Python","Java","C++","SQL","Machine Learning","Deep Learning",
        "NLP","Data Science","TensorFlow","Keras","PyTorch",
        "Streamlit","Git","Docker","AWS","Flask","FastAPI"
    ]
    return [s for s in skills if s.lower() in text.lower()]

# ================= AI SCORING (ROLE-AWARE ATS PROMPT) =================
def internal_score_engine(resume_text, job_title):
    prompt = f"""
You are an ATS-style resume evaluation engine.

IMPORTANT ROLE DEFINITIONS:
- Data Analyst: SQL, Excel, reporting, dashboards, BI tools, business insights
- Data Scientist: Machine learning, statistics, models, experimentation
- Machine Learning Engineer: model deployment, MLOps, pipelines
- Business Intelligence Analyst: KPIs, visualization, reporting
- Data Engineer: ETL, pipelines, databases

TASK:
Evaluate this resume STRICTLY for the target role:
TARGET ROLE: {job_title}

SCORING RULES (MANDATORY):
- Skills relevance: 40 points
- Experience relevance: 35 points
- Education relevance: 25 points
- Total score = 100

ROLE MISMATCH RULE:
If the resume is primarily suited for a DIFFERENT role than the target role,
apply a strong penalty to the final score.

You must:
1. Detect the resume's most suitable role
2. Compare it with the target role
3. Score conservatively and realistically (ATS behavior)

Return EXACTLY in this format:

Score: <0-100>
Reasons:
- reason1
- reason2
- reason3
Suggestions:
- suggestion1
- suggestion2
- suggestion3

Resume:
{resume_text}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a strict ATS resume evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=600
    )

    return completion.choices[0].message.content.strip()

# ================= HEADER =================
st.markdown("""
<h1 style='text-align:center;'>📄 AI Resume Compatibility Checker</h1>
<p style='text-align:center;color:#cfcfcf;'>
Upload your resume and get an AI-powered evaluation instantly
</p>
<hr>
""", unsafe_allow_html=True)

# ================= RESUME INPUT =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("## 📥 Resume Input")

resume_type = st.radio(
    "Select resume format",
    ["Text", "PDF", "Image"],
    horizontal=True
)

resume_text = ""

if resume_type == "Text":
    resume_text = st.text_area(
        "Paste resume text",
        height=220,
        placeholder="Paste resume content here..."
    )
elif resume_type == "PDF":
    pdf = st.file_uploader("Upload resume (PDF)", type=["pdf"])
    if pdf:
        resume_text = extract_text_from_pdf(pdf)
        save_to_txt(resume_text)
        st.success("Resume extracted successfully")
elif resume_type == "Image":
    img = st.file_uploader("Upload resume image", type=["png", "jpg", "jpeg"])
    if img:
        resume_text = extract_text_from_image(img)
        save_to_txt(resume_text)
        st.success("Resume extracted successfully")

st.caption(f"🧾 Characters detected: {len(resume_text)}")
st.markdown("</div>", unsafe_allow_html=True)

# ================= JOB TITLE (FREE TEXT – SAME UI) =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("## 💼 Job Context")
job_title = st.text_input(
    "Target Job Title",
    placeholder="e.g. Data Scientist, Data Analyst, ML Engineer"
)
st.markdown("</div>", unsafe_allow_html=True)

# ================= BUTTON =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
check = st.button("🔍 Analyze Resume", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= RESULT =================
if check:
    if not resume_text.strip() or not job_title.strip():
        st.error("Please provide resume and job title")
    else:
        resume_text = clean_text(resume_text)

        with st.spinner("🧠 AI is analyzing your resume..."):
            result = internal_score_engine(resume_text, job_title)

        score_match = re.search(r"Score:\s*(\d+)", result)
        reasons = re.findall(r"Reasons:\s*- (.+)", result)
        suggestions = re.findall(r"Suggestions:\s*- (.+)", result)

        if score_match:
            score = min(100, max(0, int(score_match.group(1))))

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## 📊 Compatibility Score")
            st.progress(score / 100)
            st.markdown(f"<h2 style='text-align:center;'>{score}%</h2>", unsafe_allow_html=True)

            if score >= 80:
                st.success("🚀 Strong match for this role")
            elif score >= 60:
                st.warning("⚡ Partial match – skill gap exists")
            else:
                st.error("🛠 Weak match for this role")
            st.markdown("</div>", unsafe_allow_html=True)

            skills = extract_skills(resume_text)
            if skills:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("## 🧠 Detected Skills")
                for s in skills:
                    st.success(s)
                st.markdown("</div>", unsafe_allow_html=True)

            if score < 85 and reasons:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("## ❗ Why the score is low")
                for r in reasons[:3]:
                    st.write("•", r)
                st.markdown("</div>", unsafe_allow_html=True)

            if suggestions:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("## ✨ Improvement Suggestions")
                for s in suggestions[:3]:
                    st.info(s)
                st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                "📥 Download Full Report",
                data=result,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )
        else:
            st.error("Failed to analyze resume")


# import streamlit as st
# import re
# from PyPDF2 import PdfReader
# from PIL import Image
# import pytesseract

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# st.set_page_config("Resume ATS Checker", page_icon="📄", layout="centered")

# # ================= CSS =================
# st.markdown("""
# <style>
# .stApp {background:#0f2027;color:white;}
# .card {background:rgba(255,255,255,0.08);padding:20px;border-radius:14px;margin-bottom:20px;}
# </style>
# """, unsafe_allow_html=True)

# # ================= JOB SKILLS =================
# JOB_SKILLS = {
#     "data analyst": [
#         "sql","excel","data analysis","reporting",
#         "dashboard","visualization","business intelligence",
#         "power bi","tableau","stakeholder"
#     ],
#     "senior data analyst": [
#         "advanced sql","excel","dashboard","business intelligence",
#         "power bi","tableau","kpi","analytics","stakeholder"
#     ],
#     "data scientist": [
#         "python","machine learning","deep learning",
#         "statistics","scikit-learn","tensorflow",
#         "pytorch","model","feature engineering"
#     ],
#     "machine learning engineer": [
#         "python","machine learning","deep learning",
#         "deployment","mlops","docker","kubernetes","api"
#     ],
#     "business intelligence analyst": [
#         "sql","business intelligence","dashboard",
#         "power bi","tableau","kpi","reporting"
#     ],
#     "data engineer": [
#         "sql","python","etl","pipeline",
#         "airflow","spark","hadoop","warehouse"
#     ],
#     "product data analyst": [
#         "sql","product analytics","a/b testing",
#         "cohort","funnel","metrics","dashboard"
#     ],
#     "ai researcher": [
#         "machine learning","deep learning","nlp",
#         "research","pytorch","tensorflow","neural network"
#     ]
# }

# # ================= HELPERS =================
# def extract_text_pdf(pdf):
#     reader = PdfReader(pdf)
#     return " ".join(p.extract_text() or "" for p in reader.pages)

# def extract_text_image(img):
#     return pytesseract.image_to_string(Image.open(img))

# def clean(text):
#     return re.sub(r"\s+", " ", text.lower())

# # ================= EXPERIENCE =================
# def score_experience(text):
#     years = re.findall(r"(\d+)\+?\s*(?:years|yrs)", text)
#     years = max(map(int, years)) if years else 0

#     if years >= 7: return 35, years
#     if years >= 4: return 28, years
#     if years >= 1: return 18, years
#     if "intern" in text: return 10, 0
#     return 5, 0

# # ================= EDUCATION =================
# def score_education(text):
#     if "phd" in text: return 25, "PhD"
#     if "master" in text or "m.tech" in text or "m.sc" in text:
#         return 22, "Master's"
#     if "b.tech" in text or "bachelor" in text or "b.sc" in text:
#         return 18, "Bachelor's"
#     if "diploma" in text: return 12, "Diploma"
#     return 8, "Not Found"

# # ================= SKILLS =================
# def score_skills(text, job):
#     required = JOB_SKILLS[job]
#     found = [s for s in required if s in text]
#     score = (len(found) / len(required)) * 40
#     return round(score,2), found, required

# # ================= FINAL =================
# def calculate(resume, job):
#     skill_score, found, required = score_skills(resume, job)
#     exp_score, years = score_experience(resume)
#     edu_score, edu = score_education(resume)
#     total = round(skill_score + exp_score + edu_score,2)
#     return total, skill_score, exp_score, edu_score, found, years, edu, required

# # ================= UI =================
# st.markdown("<h1 style='text-align:center;'>📄 Resume ATS Checker</h1>", unsafe_allow_html=True)

# job = st.selectbox("💼 Select Job Role", JOB_SKILLS.keys())

# resume_type = st.radio("Resume Type", ["Text","PDF","Image"], horizontal=True)

# resume_text = ""
# if resume_type=="Text":
#     resume_text = st.text_area("Paste Resume")
# elif resume_type=="PDF":
#     pdf = st.file_uploader("Upload PDF", type=["pdf"])
#     if pdf: resume_text = extract_text_pdf(pdf)
# elif resume_type=="Image":
#     img = st.file_uploader("Upload Image", type=["png","jpg"])
#     if img: resume_text = extract_text_image(img)

# if st.button("🔍 Analyze"):
#     if not resume_text:
#         st.error("Upload resume")
#     else:
#         resume = clean(resume_text)
#         total, s, e, ed, found, years, edu, req = calculate(resume, job)

#         st.markdown("<div class='card'>", unsafe_allow_html=True)
#         st.progress(total/100)
#         st.markdown(f"## ✅ Final Score: {total}/100")
#         st.write(f"🧠 Skills: {s}/40")
#         st.write(f"💼 Experience: {e}/35 ({years} yrs)")
#         st.write(f"🎓 Education: {ed}/25 ({edu})")
#         st.markdown("</div>", unsafe_allow_html=True)

#         st.markdown("<div class='card'>", unsafe_allow_html=True)
#         st.write("**Required Skills:**", ", ".join(req))
#         st.write("**Matched Skills:**", ", ".join(found) if found else "None")
#         st.markdown("</div>", unsafe_allow_html=True)

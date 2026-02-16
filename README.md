# 📄 AI Resume Compatibility Checker

An AI-powered ATS-style Resume Evaluation App built using **Streamlit +
Groq LLM**.

This project analyzes resumes and calculates a compatibility score based
on a selected job role such as Data Scientist, Data Analyst, Machine
Learning Engineer, etc.

It simulates how modern Applicant Tracking Systems (ATS) evaluate
resumes using skills, education, and experience relevance.

------------------------------------------------------------------------

## 🚀 Features

-   Upload Resume in **Text / PDF / Image** format
-   OCR Text Extraction using **Tesseract**
-   Role-Aware AI Scoring Engine
-   ATS Compatibility Score (0--100)
-   Skill Detection System
-   Improvement Suggestions
-   Downloadable AI Report
-   Modern Streamlit UI

------------------------------------------------------------------------

## 🧠 How It Works

1.  User uploads resume or pastes text.
2.  Text is extracted using:
    -   PyPDF2 (PDF files)
    -   Tesseract OCR (Images)
3.  Resume text is sent to Groq LLM.
4.  AI evaluates resume strictly for the selected job role.

### 📊 Scoring System

-   Skills Relevance → 40 points\
-   Experience Relevance → 35 points\
-   Education Relevance → 25 points

Role mismatch penalties are applied like real ATS systems.

------------------------------------------------------------------------

## 🛠 Tech Stack

-   Python
-   Streamlit
-   Groq API (LLaMA 3.1)
-   PyPDF2
-   Pytesseract
-   PIL
-   Regex

------------------------------------------------------------------------

## 📂 Project Structure

AI-Resume-Checker/ │ ├── app.py ├── extracted_texts/ ├──
requirements.txt ├── .env └── README.md

------------------------------------------------------------------------

## ⚙️ Installation

### 1️⃣ Clone Repository

git clone https://github.com/your-username/AI-Resume-Checker.git cd
AI-Resume-Checker

### 2️⃣ Create Virtual Environment

python -m venv venv venv`\Scripts`{=tex}`\activate`{=tex}

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Setup Environment Variable

Create a `.env` file and add:

GROQ_API_KEY=your_api_key_here

### 5️⃣ Install Tesseract OCR

https://github.com/tesseract-ocr/tesseract

------------------------------------------------------------------------

## ▶️ Run the Application

streamlit run app.py

------------------------------------------------------------------------

## 👨‍💻 Author

Harsh Modi\
AI / ML Developer

------------------------------------------------------------------------

## ⭐ Support

If you like this project:

⭐ Star the repo\
🍴 Fork it\
🚀 Build your own AI tools

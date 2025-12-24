import streamlit as st
import os
import tempfile
from resume_parser import extract_text_from_pdf, clean_text
from matcher import ResumeMatcher

PORT = int(os.environ.get("PORT", 8501))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Job-Fit | Resume Screening",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #ffffff;
    color: #2c2c2c;
}

.title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 800;
    color: #ff4b4b;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #6b6b6b;
    margin-bottom: 40px;
}

.card {
    background: #f9f9fb;
    border: 1px solid #e6e6ea;
    border-radius: 14px;
    padding: 25px;
    text-align: center;
    margin-top: 20px;
}

.label {
    font-size: 0.85rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.category {
    font-size: 2.2rem;
    font-weight: 800;
    color: #222;
    margin: 10px 0;
}

.progress {
    background: #eaeaea;
    height: 8px;
    border-radius: 10px;
    overflow: hidden;
    margin: 15px 0;
}

.progress-bar {
    height: 100%;
    background: #ff4b4b;
}

.confidence {
    font-weight: 600;
    color: #444;
}

[data-testid="stFileUploader"] {
    border-radius: 12px;
    padding: 25px;
    background: #f4f6f9;
    border: 1px dashed #d0d3d8;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- MODEL LOADING ----------------
@st.cache_resource
def load_matcher():
    return ResumeMatcher()

try:
    matcher = load_matcher()
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

# ---------------- HEADER ----------------
st.markdown('<div class="title">Job-Fit</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-based Resume Screening System</div>',
    unsafe_allow_html=True
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Resume (PDF only)",
    type=["pdf"]
)

if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File size must be under 10MB.")
    else:
        with st.spinner("Analyzing resume..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                raw_text = extract_text_from_pdf(tmp_path)
                resume_text = clean_text(raw_text)

                if not resume_text:
                    st.error("Unable to extract text. Scanned PDFs are not supported.")
                else:
                    category, confidence = matcher.predict_category(resume_text)

                    st.subheader("Best Matched Category")
                    st.markdown(f"### {category}")
                    st.progress(int(confidence * 100))
                    st.write(f"**Confidence Score:** {confidence:.1%}")

                    with st.expander("View Extracted Resume Text"):
                        st.text_area("", resume_text, height=220)

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
else:
    st.info("Upload a PDF resume to begin screening.")


    
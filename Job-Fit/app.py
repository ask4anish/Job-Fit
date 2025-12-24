import streamlit as st
import os
import tempfile
import requests
from streamlit_lottie import st_lottie
from resume_parser import extract_text_from_pdf, clean_text
from matcher import ResumeMatcher

# ---------------- CONFIG & ASSETS ----------------
st.set_page_config(
    page_title="Job-Fit",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Lottie Animation Loader
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Assets
# Animation of a scanning doc or processing
lottie_scanning = load_lottieurl("https://lottie.host/3c26cd66-26ba-4478-8720-3301a97d5223/81XyL3jZtJ.json") 
# Fallback or generic loading
if not lottie_scanning:
    lottie_scanning = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

/* GLOBAL STYLES */
body, .stApp {
    font-family: 'Outfit', sans-serif;
}

h1, h2, h3, h4, h5, h6, p, div, span, button, input, textarea, label {
    font-family: 'Outfit', sans-serif;
}

/* Fix for Streamlit icons/ligatures rendering as text */
button[kind="header"] span {
    font-family: inherit !important;
}

.stApp {
    background-color: #f8fafc; /* Slate-50 */
    color: #1e293b; /* Slate-800 */
}

/* HEADINGS */
h1, h2, h3 {
    color: #0f172a; /* Slate-900 */
    font-weight: 700;
}

.main-title {
    text-align: center;
    font-size: 3rem;
    background: -webkit-linear-gradient(45deg, #4f46e5, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #64748b; /* Slate-500 */
    margin-bottom: 3rem;
}

/* Change default Streamlit uploader size text */
[data-testid="stFileUploader"] small {
    visibility: hidden;
}

/* CARDS & CONTAINERS */
.result-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    margin-top: 2rem;
    border: 1px solid #e2e8f0;
}

.category-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #e0e7ff; /* Indigo-100 */
    color: #4338ca; /* Indigo-700 */
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.match-score {
    font-size: 2.5rem;
    font-weight: 800;
    color: #4f46e5; /* Indigo-600 */
}

/* UPLOADER CUSTOMIZATION */
[data-testid="stFileUploader"] {
    background-color: #ffffff;
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5;
    background-color: #eef2ff;
}

/* BROWSE BUTTON STYLING */
[data-testid="stFileUploader"] button {
    background: -webkit-linear-gradient(45deg, #4f46e5, #06b6d4) !important;
    color: white !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: transform 0.2s;
}

[data-testid="stFileUploader"] button:hover {
    transform: scale(1.05);
    opacity: 0.9;
}

/* RESPONSIVE DESIGN */
@media (max-width: 768px) {
    .main-title {
        font-size: 2.2rem;
    }
    .subtitle {
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .result-card {
        padding: 1.5rem;
        margin: 1rem;
    }
    .match-score {
        font-size: 2rem;
    }
    [data-testid="stFileUploader"] {
        padding: 1rem;
    }
}



@media (max-width: 480px) {
    .main-title {
        font-size: 1.8rem;
    }
    .result-card {
        padding: 1rem;
        margin: 0.5rem;
    }
    .match-score {
        font-size: 1.75rem;
    }
    /* Adjust container padding on very small screens */
    .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* HIDE STREAMLIT BRANDING */
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

# ---------------- UI LAYOUT ----------------

# Header
st.markdown('<div class="main-title">Job-Fit</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ai resume screening system</div>', unsafe_allow_html=True)

# File Upload Section
uploaded_file = st.file_uploader(
    label="",          
    type=["pdf"]
)




if uploaded_file:
    # Size Validation (200MB) 
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error("⚠️ File size exceeds 200MB limit.")
    else:
        # Processing Block
        with st.container():
            # Create a placeholder for the loading state
            loading_placeholder = st.empty()
            
            # Show Animation
            with loading_placeholder.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if lottie_scanning:
                        st_lottie(lottie_scanning, height=250, key="loader")
                    else:
                        st.spinner("Analyzing resume content...")
            
            # Perform Analysis
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                raw_text = extract_text_from_pdf(tmp_path)
                resume_text = clean_text(raw_text)

                # Clear animation once done
                loading_placeholder.empty()

                if not resume_text:
                    st.error("❌ Could not extract text. Please ensure it's a text-based PDF.")
                else:
                    category, confidence = matcher.predict_category(resume_text)
                    
                    # ---------------- RESULTS DISPLAY ----------------
                    st.markdown("""
                    <div class="result-card">
                        <div style="text-align: center;">
                            <span class="category-badge">TOP MATCH</span>
                            <h2 style="margin: 10px 0; color: #1e293b;">""" + category + """</h2>
                            <div class="match-score">""" + f"{confidence:.1%}" + """</div>
                            <p style="color: #64748b;">Confidence Match</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Simple Progress Bar
                    st.progress(int(confidence * 100))

                    # Expandable details
                    with st.expander("📄 View Extracted Content"):
                        st.text_area("Raw Text", resume_text, height=200)

            except Exception as e:
                loading_placeholder.empty()
                st.error(f"An error occurred during analysis: {str(e)}")
            
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

else:
    # Empty State Helper
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; color: #94a3b8;">
            <p>Supported format: <strong>PDF</strong> • Max size: <strong>200MB</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

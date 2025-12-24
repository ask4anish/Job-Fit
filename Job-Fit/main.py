import argparse
import os
from resume_parser import extract_text_from_pdf, clean_text
from matcher import ResumeMatcher

def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening System")
    parser.add_argument("--resume", type=str, help="Path to the resume PDF file")
    parser.add_argument("--job_desc", type=str, help="Path to the job description text file or raw text string")
    parser.add_argument("--keywords", type=str, nargs="*", help="List of required skills/keywords")
    
    args = parser.parse_args()
    
    # Initialize Matcher
    matcher = ResumeMatcher()
    
    # Handle Resume Input
    if args.resume and os.path.exists(args.resume):
        print(f"Processing resume: {args.resume}")
        raw_text = extract_text_from_pdf(args.resume)
        resume_text = clean_text(raw_text)
        if not resume_text:
            print("Error: Could not extract text from resume.")
            return
    else:
        print("No resume provided or file not found. Running in DEMO mode.")
        resume_text = "Experienced Python Developer with strong background in Data Science and Machine Learning. Proficient in PyTorch, TensorFlow, and building REST APIs."
        print(f"Demo Resume Text: {resume_text}\n")

    # Handle Job Description Input
    if args.job_desc:
        if os.path.exists(args.job_desc):
             with open(args.job_desc, 'r') as f:
                job_desc = f.read()
        else:
            job_desc = args.job_desc
    else:
        job_desc = "Looking for a Python Developer with experience in Machine Learning, Data Analysis, and API development. key skills: Python, PyTorch, SQL."
        print(f"Demo Job Description: {job_desc}\n")
        
    # Match
    required_skills = args.keywords if args.keywords else ["Python", "Machine Learning"]
    
    print("\nCalculated Scores:")
    results = matcher.score_resume(resume_text, job_desc, required_skills)
    
    print(f"Final Score: {results['final_score']}")
    print(f"Semantic Similarity: {results['similarity_score']}")
    print(f"Keyword Match Score: {results['keyword_score']}")
    print(f"Matched Keywords: {results['matched_keywords']}")

if __name__ == "__main__":
    main()

import argparse
import os
from resume_parser import extract_text_from_pdf, clean_text
from matcher import ResumeMatcher

def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening System - Classifier Mode")
    parser.add_argument("--resume", type=str, required=True, help="Path to the resume PDF file")
    
    args = parser.parse_args()
    
    # Initialize Matcher
    try:
        matcher = ResumeMatcher()
    except Exception as e:
        print(f"Error initializing model: {e}")
        return
    
    # Handle Resume Input
    if os.path.exists(args.resume):
        print(f"Processing resume: {args.resume}")
        raw_text = extract_text_from_pdf(args.resume)
        resume_text = clean_text(raw_text)
        
        if not resume_text:
            print("Error: Could not extract text from resume.")
            return
            
        print("\nPredicting Category...")
        category, confidence = matcher.predict_category(resume_text)
        
        print("\n" + "="*30)
        print(f"PREDICTED CATEGORY: {category}")
        print(f"CONFIDENCE: {confidence:.2%}")
        print("="*30 + "\n")
        
    else:
        print(f"Error: File not found at {args.resume}")

if __name__ == "__main__":
    main()

import re
import pickle
import os
import numpy as np
import pandas as pd
from typing import List, Tuple, Union, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

class ResumeMatcher:
    def __init__(self, transformer_model: str = "all-MiniLM-L6-v2"):
        print("Loading models... this might take a moment.")
        self.model = SentenceTransformer(transformer_model)
        
        # Try to load existing model - CRITICAL for Cloud Deployment
        model_path = "model.pkl"
        if os.path.exists(model_path):
            self.saved_categories = self.load_model(model_path)
            if self.saved_categories:
                print(f"Loaded saved model with {len(self.saved_categories)} categories.")
            else:
                raise ValueError("Failed to load model from model.pkl")
        else:
            # On Cloud, we cannot train, so we must raise an error if model is missing
            raise FileNotFoundError("model.pkl not found! Please ensure the pre-trained model is uploaded.")

    def predict_category(self, resume_text):
        """
        Predicts the job category using the trained classifier.
        """
        if hasattr(self, 'classifier') and self.classifier:
            try:
                # Encode text
                embedding = self.model.encode(resume_text).reshape(1, -1)
                # Predict
                prediction = self.classifier.predict(embedding)[0]
                probs = self.classifier.predict_proba(embedding)[0]
                confidence = max(probs)
                return prediction, round(confidence, 4)
            except Exception as e:
                print(f"Prediction failed: {e}")
                raise e # Propagate error for visibility
        else:
            raise RuntimeError("Model is not loaded properly.")

    def train_model(self, csv_path):
        """
        Trains a Logistic Regression classifier on the provided CSV dataset.
        Expected CSV columns: 'Resume', 'Category'
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset not found at {csv_path}")
            
        print("Loading dataset...")
        df = pd.read_csv(csv_path)
        
        if 'Resume' not in df.columns or 'Category' not in df.columns:
            raise ValueError("CSV must contain 'Resume' and 'Category' columns.")
            
        # create embeddings
        print("Encoding resumes... this may take a minute.")
        embeddings = self.model.encode(df['Resume'].tolist(), show_progress_bar=True)
        
        # Train classifier
        print("Training classifier...")
        self.classifier = LogisticRegression(max_iter=1000)
        self.classifier.fit(embeddings, df['Category'])
        
        print("Training complete.")
        
        # Save model
        self.save_model(self.classifier, sorted(df['Category'].unique().tolist()))
        
        return sorted(df['Category'].unique().tolist())

    def save_model(self, classifier: Any, categories: List[str], filename: str = "model.pkl") -> None:
        """
        Saves the trained classifier and categories to disk.
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump({'classifier': classifier, 'categories': categories}, f)
            print(f"Model saved to {filename}")
        except IOError as e:
            print(f"Error saving model: {e}")

    def load_model(self, filename: str = "model.pkl") -> Optional[List[str]]:
        """
        Loads the trained classifier and categories from disk.
        """
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                    self.classifier = data['classifier']
                    return data['categories']
            except Exception as e:
                print(f"Error loading model: {e}")
        return None

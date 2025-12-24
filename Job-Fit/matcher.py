import re
from sentence_transformers import SentenceTransformer, util
import numpy as np

class ResumeMatcher:
    def __init__(self, transformer_model="all-MiniLM-L6-v2"):
        print("Loading models... this might take a moment.")
        self.model = SentenceTransformer(transformer_model)
        print("Models loaded successfully.")
        
        # Try to load existing model
        self.saved_categories = self.load_model()
        if self.saved_categories:
            print(f"Loaded saved model with {len(self.saved_categories)} categories.")

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
                return "Unknown", 0.0
        else:
            return "Model not trained - Please train using UpdatedResumeDataSet.csv", 0.0

    def train_model(self, csv_path):
        """
        Trains a Logistic Regression classifier on the provided CSV dataset.
        Expected CSV columns: 'Resume', 'Category'
        """
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import LabelEncoder
        import pickle
        
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

    def save_model(self, classifier, categories, filename="model.pkl"):
        """
        Saves the trained classifier and categories to disk.
        """
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump({'classifier': classifier, 'categories': categories}, f)
        print(f"Model saved to {filename}")

    def load_model(self, filename="model.pkl"):
        """
        Loads the trained classifier and categories from disk.
        """
        import pickle
        import os
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                    self.classifier = data['classifier']
                    return data['categories']
            except Exception as e:
                print(f"Error loading model: {e}")
        return None

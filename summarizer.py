from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Set up logging to avoid transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

# Initialize the models once when the module is loaded
# Using "t5-small" for a good balance of speed and performance
try:
    print("Loading summarization model (t5-small)...")
    summarizer = pipeline("summarization", model="t5-small")
    print("Summarization model loaded.")
except Exception as e:
    print(f"Error loading summarization model: {e}")
    summarizer = None

def get_summary(text: str) -> str:
    """
    Generates a summary for the given text.
    """
    if summarizer is None:
        return "Error: Summarization model is not loaded."

    # T5 models have a token limit. For simplicity, we'll truncate.
    # A more advanced approach would be to chunk the text.
    max_chunk_length = 512 
    
    # Simple truncation
    if len(text.split()) > max_chunk_length:
        text = " ".join(text.split()[:max_chunk_length])

    try:
        summary_result = summarizer(text, max_length=150, min_length=30, do_sample=False)
        return summary_result[0]['summary_text']
    except Exception as e:
        return f"Error during summarization: {e}"

def get_keywords(text: str) -> list:
    """
    Extracts keywords using TF-IDF.
    """
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5)
        vectorizer.fit_transform([text])
        keywords = vectorizer.get_feature_names_out()
        return list(keywords)
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []
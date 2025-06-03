import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_sm")

def pdf2text(file_path):
    return extract_text(file_path)

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens_1 = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space and token.is_alpha
    ]
    return tokens_1


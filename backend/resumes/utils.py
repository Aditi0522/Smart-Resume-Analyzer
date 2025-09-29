import spacy
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def pdf2text(file_path):
    return extract_text(file_path)

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens_1 = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space and token.is_alpha
    ]
    return tokens_1

def compute_cosine_similarity(token_1,token_2):
    text1 = " ".join(token_1)
    text2 = " ".join(token_2)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1,text2])
    sim = cosine_similarity(vectors[0],vectors[1])
    return round(sim[0][0],4)
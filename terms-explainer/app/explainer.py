import fitz  # PyMuPDF for PDF text extraction
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

# Load model and tokenizer globally
model_id = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to("cpu")  # or "cuda" if available

KEY_CLAUSES = [
    "auto-renewal",
    "cancellation",
    "payment",
    "refund",
    "liability",
    "termination",
    "governing law",
    "dispute resolution"
]

def extract_text_from_pdf(file_bytes):
    """Extract all text from PDF bytes"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=900):  # ~900 words ~ fits into 1024 token limit
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

def summarize_chunk(chunk):
    """Summarize a single chunk using BART"""
    inputs = tokenizer.encode(chunk, return_tensors="pt", truncation=True, max_length=1024)
    inputs = inputs.to(model.device)

    summary_ids = model.generate(
        inputs,
        max_length=200,
        min_length=50,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def format_summary_to_points(summary_text):
    """
    Convert summary text into a list of bullet points.
    This splits on sentence boundaries and cleans whitespace.
    """
    # Simple sentence splitter (can be improved with nltk or spacy)
    sentences = re.split(r'(?<=[.!?]) +', summary_text.strip())

    # Filter out very short sentences (optional)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Format as bullet points
    points = [f"• {sentence}" for sentence in sentences]

    return "\n".join(points)

def summarize_terms(text):
    """Generate overall summary from chunked terms text, formatted as bullet points"""
    summaries = [summarize_chunk(chunk) for chunk in chunk_text(text)]
    combined_summary = "\n\n".join(summaries)

    # Format combined summary into points
    formatted_summary = format_summary_to_points(combined_summary)

    # Optional dummy confidence estimation (not native in BART)
    confidence = 85  # static/fixed for now, can be enhanced

    return formatted_summary, confidence

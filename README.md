Usage
Place your PDF at ./temppdf.pdf (or adjust pdf_path in the script).

Run the script:

bash
Copy
Edit
python generate_headings.py
After completion you’ll see headings_output.json containing:

json
Copy
Edit
[
  {
    "page_number": 1,
    "generated_heading": "Introduction to Widgets"
  },
  {
    "page_number": 1,
    "generated_heading": "Widget Installation Steps"
  },
  …  
]
Script Overview
Step 1: Load and parse the PDF, extracting text blocks >30 characters (PyMuPDF).

Step 2: Split each block into overlapping 250‑char chunks (LangChain).

Step 3: Load google/flan‑t5‑small and generate a heading for each chunk (Transformers).

Step 4: Serialize a list of { page_number, generated_heading } to JSON.

Dependencies
PyMuPDF (fitz)

LangChain (CharacterTextSplitter)

Hugging Face Transformers (T5Tokenizer, T5ForConditionalGeneration)

Python’s built‑in json module

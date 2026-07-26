# ContractIQ — Setup & Run Guide
## Read this fully before starting. Takes 15 minutes to set up.

---

## WHAT IS IN THIS FOLDER

```
contractiq/
│
├── 01_Setup.ipynb                ← Run first. Installs everything.
├── 02_PDF_Parser.ipynb           ← Reads your contract PDFs
├── 03_Obligation_Extractor.ipynb ← AI extracts obligations  
├── 04_Conflict_Detector.ipynb    ← Finds conflicts between docs
├── 05_RAG_Engine.ipynb           ← Builds Q&A on your contracts
│
├── demo_app.py                   ← THE DEMO (run this for presentation)
├── generate_contracts.py         ← Generates fake test contracts
│
├── requirements.txt              ← All Python packages needed
├── SETUP.bat                     ← Double-click to install (Windows)
├── .env                          ← YOUR API KEY GOES HERE
│
├── test_contracts/               ← Put your PDF contracts here
├── database/                     ← SQLite database (auto-created)
├── vectorstore/                  ← ChromaDB vectors (auto-created)
└── exports/                      ← Downloaded reports go here
```

---

## STEP 0 — ONE TIME SETUP (Do this tonight)

### Option A — Double click (Windows)
```
Double-click SETUP.bat
Wait for it to finish (5-10 minutes)
```

### Option B — Terminal
```bash
pip install groq pymupdf pdfplumber chromadb sentence-transformers \
            langchain langchain-community langchain-groq sqlalchemy \
            python-dotenv streamlit plotly pandas openpyxl reportlab \
            apscheduler spacy python-multipart fastapi uvicorn nbformat

python -m spacy download en_core_web_sm
```

---

## STEP 1 — SET YOUR API KEY

Open the `.env` file (use Notepad or any text editor)

Change this line:
```
GROQ_API_KEY=paste_your_groq_key_here
```

To this (your actual key):
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

Save the file.

**NEVER share this file. Never put the key in your code.**

---

## STEP 2 — GET TEST CONTRACTS

You already have the contract generator. Run it:
```bash
python generate_contracts.py
```

Then copy the generated PDFs to the test_contracts folder:
```bash
# Windows
copy contracts\run_*\*.pdf test_contracts\

# Mac/Linux  
cp contracts/run_*/  .pdf test_contracts/
```

Make sure you do NOT copy the `00_CONFLICT_REFERENCE.pdf` — 
that is your answer key, keep it private.

---

## STEP 3 — RUN THE NOTEBOOKS (In Order)

Open terminal in the contractiq folder and run:
```bash
jupyter notebook
```

This opens your browser. Run each notebook top to bottom:

### 01_Setup.ipynb
- Installs packages (skip if SETUP.bat already ran)  
- Creates the database and all tables
- Tests your Groq API key
- **Run all cells. Should show all green ticks.**

### 02_PDF_Parser.ipynb
- Reads all PDFs from test_contracts/ folder
- Extracts text from every page
- Splits into chunks
- Saves to database
- **Run all cells. Should show chunk counts for each document.**

### 03_Obligation_Extractor.ipynb
- Sends each chunk to Groq AI
- Gets back obligations in JSON
- Saves all obligations to database
- ⏳ Takes 5-10 minutes (one API call per chunk)
- **Run all cells. Watch obligations being extracted live.**

### 04_Conflict_Detector.ipynb
- Groups obligations by type
- Compares same-type clauses across documents  
- Finds contradictions using AI
- ⏳ Takes 3-5 minutes
- **Should detect all 7 intentional conflicts.**

### 05_RAG_Engine.ipynb
- Converts all chunks to vector embeddings
- Stores in ChromaDB
- Tests Q&A on your contracts
- **Run all cells. Test the sample questions.**

---

## STEP 4 — LAUNCH THE DEMO

Open a NEW terminal window:
```bash
cd contractiq
streamlit run demo_app.py
```

Browser opens automatically at: **http://localhost:8501**

---

## DEMO SCRIPT FOR PRESENTATION (5-7 minutes)

### Slide 1 — Dashboard (30 seconds)
```
"This is ContractIQ. You can see on the dashboard:
 - How many contracts are loaded
 - How many obligations were extracted
 - How many conflicts were found
 - Risk distribution chart"
```

### Slide 2 — Obligations Page (1 minute)
```
"Here are all obligations extracted automatically.
 No one read these contracts manually. The AI did it.
 I can filter by type — let me show just SLA obligations.
 I can filter by risk — here are all HIGH risk obligations."
```

### Slide 3 — Conflicts Page (2 minutes)
```
"This is the most important feature.
 The system found X conflicts across the documents.
 
 Look at this one — Liability Cap conflict.
 The MSA says USD 500,000.
 The SOW says USD 1,200,000.
 These two documents directly contradict each other.
 
 In a real company this would be a legal and financial risk.
 My system finds it automatically."
```

### Slide 4 — Deadlines Page (30 seconds)
```
"Here are all time-bound obligations.
 Colour coded: red is urgent, yellow is coming soon.
 The system watches these automatically."
```

### Slide 5 — Chat (1.5 minutes)
```
"Now I can ask questions about my contracts in plain English."

Ask these questions live:
1. "What is the payment deadline?"
2. "What happens if there is a data breach?"
3. "What is the governing law?"

"Notice the answer comes from the actual contract text,
 not from the AI's general knowledge. It cites the source."
```

### Slide 6 — Export (30 seconds)
```
"Finally I can export everything as Excel or CSV
 for the legal team or finance team to use."
```

---

## COMMON ERRORS AND FIXES

### "No module named 'fitz'"
```bash
pip install pymupdf
```

### "No module named 'groq'"
```bash
pip install groq
```

### "API key not valid"
- Check .env file has the correct key
- Make sure no spaces around the = sign
- Make sure the key starts with gsk_

### "No PDFs found in test_contracts/"
- Run generate_contracts.py first
- Copy PDFs to test_contracts/ folder

### "ChromaDB error on Python 3.14"
```bash
pip install chromadb --upgrade
```
If still failing:
```bash
pip install chromadb==0.4.24
```

### "Rate limit error from Groq"
- Wait 60 seconds and re-run the cell
- Groq free tier limit: 30 requests/minute
- The notebook automatically retries with delay

### Streamlit not opening
```bash
pip install streamlit --upgrade
streamlit run demo_app.py --server.port 8502
```
Then open: http://localhost:8502

---

## QUICK REFERENCE — DAILY COMMANDS

```bash
# Generate fresh test contracts
python generate_contracts.py

# Start Jupyter notebooks
jupyter notebook

# Launch demo app
streamlit run demo_app.py

# Check database contents
python -c "
import sqlite3
conn = sqlite3.connect('database/contractiq.db')
print('Documents:',   conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0])
print('Obligations:', conn.execute('SELECT COUNT(*) FROM obligations').fetchone()[0])
print('Conflicts:',   conn.execute('SELECT COUNT(*) FROM conflicts').fetchone()[0])
conn.close()
"
```

---

## FOR YOUR VIVA

**Q: How does obligation extraction work?**
A: Each contract is split into 1000-character overlapping chunks using 
   LangChain's RecursiveCharacterTextSplitter. Each chunk is sent to 
   Llama-3-70B via Groq API with a structured JSON prompt. The LLM 
   classifies obligations into 9 types and returns deadline, clause 
   reference, and risk level.

**Q: How does conflict detection work?**
A: Obligations are grouped by type across all documents. For any type 
   that appears in more than one document, the system sends pairs to 
   the LLM for natural language inference — specifically contradiction 
   detection. If conflict_found is true, it's stored with severity and 
   explanation.

**Q: What is RAG?**
A: Retrieval Augmented Generation. Contract chunks are embedded using 
   sentence-transformers (all-MiniLM-L6-v2) and stored in ChromaDB. 
   At query time, the question is embedded and cosine similarity finds 
   the top-5 most relevant chunks. These are passed as context to the 
   LLM which generates a cited answer.

**Q: Did you train any model?**
A: No. The system uses pre-trained models via API. Training is not 
   required — the novelty is in the pipeline: chunking strategy, 
   obligation-type prompting, cross-document conflict detection logic, 
   and RAG architecture tuned for legal document structure.

---

*ContractIQ — M.Tech Project | Ambient-AI for Contract Intelligence*

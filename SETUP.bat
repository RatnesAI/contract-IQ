@echo off
echo.
echo ================================================
echo   ContractIQ - First Time Setup
echo   Run this ONCE before anything else
echo ================================================
echo.

echo [1/4] Installing Python packages...
pip install groq pymupdf pdfplumber chromadb sentence-transformers langchain langchain-community langchain-groq sqlalchemy python-dotenv streamlit plotly pandas openpyxl reportlab apscheduler spacy python-multipart fastapi uvicorn nbformat ipywidgets
echo.

echo [2/4] Downloading spaCy language model...
python -m spacy download en_core_web_sm
echo.

echo [3/4] Creating project folders...
mkdir contracts 2>nul
mkdir database 2>nul
mkdir vectorstore 2>nul
mkdir exports 2>nul
mkdir test_contracts 2>nul
echo Done.
echo.

echo [4/4] Checking .env file...
if not exist .env (
    echo GROQ_API_KEY=paste_your_groq_key_here > .env
    echo Created .env file - OPEN IT AND PASTE YOUR GROQ API KEY
) else (
    echo .env file already exists.
)
echo.

echo ================================================
echo   SETUP COMPLETE
echo.
echo   NEXT STEPS:
echo   1. Open .env file and paste your Groq API key
echo   2. Copy your contract PDFs to test_contracts/
echo   3. Run: jupyter notebook
echo   4. Open notebooks in order: 01 to 05
echo   5. Run: streamlit run demo_app.py
echo ================================================
pause

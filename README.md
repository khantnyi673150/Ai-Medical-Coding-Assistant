# AI Medical Coding Assistant

🏥 **Intelligent ICD Code Extraction & AI Suggestion System**

## 🎯 Features

- **Match Existing ICD Codes**: Extracts ICD-10 codes from CSV/Excel files
- **AI Suggest ICD Codes**: Uses Google Gemini AI to analyze clinical text and suggest appropriate ICD codes
- Matches codes against Thai ICD-10 guideline database
- Organizes results by admission number (AN)
- Returns structured JSON with principal and secondary diagnoses

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```


cd backend
uvicorn main:app --reload
```

Server runs on: `http://localhost:8000`

### 4. Open Frontend

```bash
cd frontend
python3 -m http.server 8080
```

Then visit: `http://localhost:8080`

## 📝 Usage

### Option 1: Match Existing ICD Codes

Upload a CSV/Excel file that **already contains ICD codes**:

```csv
AN,principal_dx,secondary_dx
1001,I50.9,"I10, E11.9"
1002,I48.91,I10
```

Click: **"Match Existing ICD Codes"**

### Option 2: AI Suggest ICD Codes

Upload a CSV/Excel file with **clinical text descriptions**:

```csv
AN,Clinical_Summary
AN001,65M with chest pain. Labs: Troponin 4.5 ng/mL. ECG: ST elevation. Heart failure
AN002,45F with type 1 diabetes. Glucose 450 mg/dL, pH 7.1. Diabetic ketoacidosis
```

Click: **"🤖 AI Suggest ICD Codes"**

## 🧪 Test Examples

### Example 1: File with ICD Codes

```csv
AN,icd_codes,diagnosis
1001,I21.9,Acute MI
1002,"I50.9, I10",Heart failure with hypertension
```

### Example 2: File with Clinical Text

```csv
AN,Admission_Date,Clinical_Summary
AN001,2024-01-15,65M with chest pain. Labs: Troponin 4.5 ng/mL, CK-MB elevated. ECG: ST elevation. Complications: Heart failure, Cardiogenic shock
AN002,2024-01-16,45F with type 1 diabetes. Labs: Glucose 450 mg/dL, pH 7.1, Ketones positive. Complications: Acute kidney injury
```

## 📦 Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **AI**: Google Gemini 1.5 Flash (FREE API)
- **Data Processing**: pandas, openpyxl, regex
- **Frontend**: Vanilla HTML/JS
- **Database**: icd_guideline_62.csv (Thai ICD-10 guideline)

## 🔐 Security

- ✅ Gemini API key stored in `backend/.env`
- ✅ Never exposed to frontend
- ✅ CORS protection enabled
- ⚠️ For production: use specific CORS origins

## 📂 Required Files

```
backend/
├── icd_guideline_62.csv  ← ICD-10 guideline database
├── .env                   ← Gemini API key
├── main.py
├── icd_matcher.py
├── ai_icd_suggester.py
└── requirements.txt
```

## ⚠️ Important Notes

- **Only Gemini API is used** - No OpenAI required
- ICD codes must follow pattern: **Letter + 2-3 digits** (e.g., I50, E11.9)
- System automatically detects codes from any text
- At least one column should be named `AN` for tracking

## 🔍 How It Works

### Match Existing ICD Codes:
1. Scans all columns for ICD-10 code patterns
2. First code = Principal Diagnosis
3. Remaining codes = Secondary Diagnoses
4. Matches against `icd_guideline_62.csv` for descriptions

### AI Suggest ICD Codes:
1. Reads clinical text from CSV/Excel
2. Sends to Google Gemini AI for analysis
3. AI suggests appropriate ICD-10 codes
4. Returns structured results with diagnoses, complications, and lab findings

## 📄 License

Educational/Hackathon Project

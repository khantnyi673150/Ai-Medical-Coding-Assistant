import os
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def process_file(file_path: str, file_extension: str) -> str:
    """
    Read CSV or XLSX file and convert to text for processing.
    """
    try:
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Convert dataframe to readable text format
        text = df.to_string(index=False)
        return text
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

def extract_medical_information(text: str) -> dict:
    """
    Extract structured medical information from clinical text using Google Gemini.
    """
    
    prompt = f"""You are a medical coding assistant. Extract structured information from the following clinical text.

Return ONLY valid JSON with this exact structure:
{{
    "primary_diagnosis": "",
    "secondary_diagnoses": [],
    "complications": [],
    "lab_findings": []
}}

Rules:
- Extract the main diagnosis as primary_diagnosis
- List all additional diagnoses in secondary_diagnoses array
- List all complications in complications array
- Extract all laboratory test results in lab_findings array
- Return ONLY the JSON object, no additional text

Clinical Text:
{text}
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        
        # Parse the response
        result_text = response.text.strip()
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        # Parse JSON
        result = json.loads(result_text)
        
        return result
    
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")
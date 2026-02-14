import os
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict
import logging

logger = logging.getLogger(__name__)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_icd_guideline(guideline_path: str = "icd_guideline_62.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(guideline_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        logger.error(f"Error loading guideline: {str(e)}")
        return pd.DataFrame()

def suggest_icd_codes_from_text(text: str, guideline_df: pd.DataFrame = None) -> Dict:
    prompt = f"""You are an expert medical coder. Analyze the clinical text and suggest ACTUAL ICD-10 codes.

IMPORTANT: Return ONLY valid JSON with this EXACT structure:
{{
    "principal_diagnosis": {{
        "code": "I21.3",
        "description": "ST elevation myocardial infarction"
    }},
    "secondary_diagnoses": [
        {{
            "code": "I10",
            "description": "Hypertension"
        }}
    ],
    "complications": [
        {{
            "code": "I50.9",
            "description": "Acute heart failure"
        }},
        {{
            "code": "R57.0",
            "description": "Cardiogenic shock"
        }}
    ],
    "laboratory_findings": [
        "Troponin 4.5 ng/mL",
        "CK-MB elevated"
    ]
}}

Rules:
1. Use ACTUAL ICD-10 codes (e.g., I21.3, I50.9, R57.0)
2. Provide accurate medical descriptions
3. Extract laboratory findings as simple strings
4. Return ONLY the JSON object

Clinical Text:
{text}
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1])
            if result_text.strip().startswith('json'):
                result_text = result_text.strip()[4:].strip()
        
        result = json.loads(result_text)
        return result
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "principal_diagnosis": {"code": "", "description": "Error parsing AI response"},
            "secondary_diagnoses": [],
            "complications": [],
            "laboratory_findings": []
        }

def process_medical_file_with_ai(file_content: bytes, filename: str, guideline_path: str = "icd_guideline_62.csv") -> Dict:
    try:
        guideline_df = load_icd_guideline(guideline_path)
        
        if filename.endswith('.csv'):
            input_df = pd.read_csv(pd.io.common.BytesIO(file_content), encoding='utf-8-sig')
        elif filename.endswith(('.xlsx', '.xls')):
            input_df = pd.read_excel(pd.io.common.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        results = []
        all_codes = set()
        
        for idx, row in input_df.iterrows():
            an = str(row.get('AN', row.get('an', row.get('Admission_Number', f'Record-{idx+1}'))))
            
            clinical_text = ""
            for col in input_df.columns:
                value = row[col]
                if pd.notna(value) and col.lower() not in ['an', 'admission_number']:
                    clinical_text += f"{col}: {value}\n"
            
            if clinical_text.strip():
                ai_result = suggest_icd_codes_from_text(clinical_text, guideline_df)
                
                if ai_result.get('principal_diagnosis', {}).get('code'):
                    all_codes.add(ai_result['principal_diagnosis']['code'])
                
                for dx in ai_result.get('secondary_diagnoses', []):
                    if dx.get('code'):
                        all_codes.add(dx['code'])
                
                for comp in ai_result.get('complications', []):
                    if comp.get('code'):
                        all_codes.add(comp['code'])
                
                results.append({
                    "AN": an,
                    "principal_diagnosis": ai_result.get('principal_diagnosis', {}),
                    "secondary_diagnoses": ai_result.get('secondary_diagnoses', []),
                    "complications": ai_result.get('complications', []),
                    "laboratory_findings": ai_result.get('laboratory_findings', [])
                })
        
        total_codes = sum(
            (1 if r.get('principal_diagnosis', {}).get('code') else 0) +
            len(r.get('secondary_diagnoses', [])) + 
            len(r.get('complications', [])) 
            for r in results
        )
        
        return {
            "statistics": {
                "total_records": len(results),
                "total_icd_codes_suggested": total_codes,
                "unique_icd_codes": len(all_codes)
            },
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise
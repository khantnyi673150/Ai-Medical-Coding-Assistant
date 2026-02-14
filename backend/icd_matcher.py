import pandas as pd
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def load_icd_guideline(guideline_path: str = "icd_guideline_62.csv") -> pd.DataFrame:
    """Load ICD guideline CSV file."""
    try:
        df = pd.read_csv(guideline_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        logger.error(f"Error loading guideline: {str(e)}")
        raise

def extract_icd_codes_from_text(text: str) -> List[str]:
    """Extract ICD-10 codes from text using regex."""
    # Pattern: Letter + 2-3 digits + optional decimal part
    pattern = r'\b([A-Z]\d{2,3}(?:\.\d{1,2})?)\b'
    codes = re.findall(pattern, str(text))
    return codes

def get_code_description(code: str, guideline_df: pd.DataFrame) -> str:
    """Get description for an ICD code from guideline."""
    match = guideline_df[guideline_df['code'] == code]
    if not match.empty:
        return match.iloc[0]['description']
    return code  # Return code itself if no description found

def process_uploaded_file(
    file_content: bytes, 
    filename: str,
    guideline_path: str = "icd_guideline_62.csv"
) -> Dict:
    """
    Process uploaded CSV/Excel file and extract ICD codes with structure.
    """
    try:
        # Load guideline
        guideline_df = load_icd_guideline(guideline_path)
        
        # Load uploaded file
        if filename.endswith('.csv'):
            input_df = pd.read_csv(pd.io.common.BytesIO(file_content), encoding='utf-8-sig')
        elif filename.endswith(('.xlsx', '.xls')):
            input_df = pd.read_excel(pd.io.common.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        results = []
        all_detected_codes = set()
        
        # Process each row
        for idx, row in input_df.iterrows():
            # Get AN (Admission Number) - adjust column name as needed
            an = str(row.get('AN', row.get('an', row.get('admission_number', f'Record-{idx+1}'))))
            
            # Extract all ICD codes from all columns in this row
            row_codes = []
            for col in input_df.columns:
                value = row[col]
                if pd.notna(value):
                    codes = extract_icd_codes_from_text(str(value))
                    row_codes.extend(codes)
            
            # Remove duplicates while preserving order
            unique_codes = []
            seen = set()
            for code in row_codes:
                if code not in seen:
                    seen.add(code)
                    unique_codes.append(code)
                    all_detected_codes.add(code)
            
            if unique_codes:
                # First code is principal diagnosis
                principal_code = unique_codes[0]
                principal_desc = get_code_description(principal_code, guideline_df)
                
                # Rest are secondary diagnoses
                secondary_diagnoses = []
                for code in unique_codes[1:]:
                    desc = get_code_description(code, guideline_df)
                    secondary_diagnoses.append({
                        "code": code,
                        "description": desc
                    })
                
                results.append({
                    "AN": an,
                    "principal_diagnosis": {
                        "code": principal_code,
                        "description": principal_desc
                    },
                    "secondary_diagnoses": secondary_diagnoses
                })
        
        # Calculate statistics
        total_codes_detected = sum(
            1 + len(r['secondary_diagnoses']) for r in results
        )
        
        return {
            "statistics": {
                "total_records": len(results),
                "total_icd_codes_detected": total_codes_detected,
                "unique_icd_codes": len(all_detected_codes)
            },
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise

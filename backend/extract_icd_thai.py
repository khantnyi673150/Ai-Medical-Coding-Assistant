import pdfplumber
import re
import pandas as pd
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_icd10_from_thai_pdf(pdf_path: str) -> List[Dict[str, str]]:
    """
    Extract ICD-10 codes and descriptions from Thai guideline PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries with 'code' and 'description'
    """
    
    # ICD-10 pattern: Letter + 2 digits + optional decimal part
    # Examples: I50, I50.9, E11.65, Z99.2
    icd_pattern = re.compile(r'\b([A-Z]\d{2}(?:\.\d{1,2})?)\b')
    
    codes_dict = {}  # Use dict to automatically handle duplicates
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"📄 Processing {total_pages} pages from: {pdf_path}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Log progress
                if page_num % 10 == 0 or page_num == 1:
                    logger.info(f"⏳ Processing page {page_num}/{total_pages}...")
                
                try:
                    # Extract text
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Process line by line
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        
                        if not line:
                            continue
                        
                        # Find all ICD codes in this line
                        matches = icd_pattern.findall(line)
                        
                        for code in matches:
                            # Skip if already exists
                            if code in codes_dict:
                                continue
                            
                            # Extract description from current line
                            description = line
                            
                            # Remove the code from description
                            description = re.sub(r'\b' + re.escape(code) + r'\b', '', description)
                            
                            # Try to get surrounding context (current + next line)
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                # Only add if next line doesn't contain another ICD code
                                if not icd_pattern.search(next_line):
                                    description += ' ' + next_line
                            
                            # Clean description
                            description = ' '.join(description.split())
                            description = description.strip()
                            
                            # Remove common prefixes/suffixes
                            description = re.sub(r'^[-:•\s]+', '', description)
                            description = re.sub(r'[-:•\s]+$', '', description)
                            
                            # Only add if description is meaningful
                            if description and len(description) > 2:
                                codes_dict[code] = description
                
                except Exception as e:
                    logger.warning(f"⚠️  Error on page {page_num}: {str(e)}")
                    continue
            
            logger.info(f"✅ Extraction complete! Found {len(codes_dict)} unique ICD-10 codes.")
    
    except FileNotFoundError:
        logger.error(f"❌ File not found: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"❌ Error opening PDF: {str(e)}")
        raise
    
    # Convert to list of dicts
    result = [
        {'code': code, 'description': desc}
        for code, desc in sorted(codes_dict.items())
    ]
    
    return result

def save_to_csv(data: List[Dict[str, str]], output_file: str):
    """
    Save extracted data to CSV file.
    
    Args:
        data: List of dictionaries with 'code' and 'description'
        output_file: Output CSV filename
    """
    try:
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Sort by code
        df = df.sort_values('code').reset_index(drop=True)
        
        # Save to CSV with UTF-8 encoding (for Thai text)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"💾 Saved {len(df)} codes to: {output_file}")
        
        # Display statistics
        logger.info(f"\n📊 Statistics:")
        logger.info(f"   Total codes: {len(df)}")
        logger.info(f"   File size: {len(df)} rows × 2 columns")
        
        # Show sample data
        logger.info(f"\n📋 Sample data (first 10 rows):")
        print(df.head(10).to_string(index=False))
        
        # Show code distribution by category
        df['category'] = df['code'].str[0]
        category_counts = df['category'].value_counts().sort_index()
        logger.info(f"\n📈 Code distribution by category:")
        for cat, count in category_counts.items():
            logger.info(f"   {cat}**: {count} codes")
        
    except Exception as e:
        logger.error(f"❌ Error saving CSV: {str(e)}")
        raise

def main():
    """Main execution function."""
    
    # File paths
    pdf_path = "คู่มือแนวทางการตรวจสอบ62.pdf"
    output_csv = "icd_guideline_62.csv"
    
    logger.info("=" * 60)
    logger.info("🏥 ICD-10 Code Extraction Tool")
    logger.info("=" * 60)
    logger.info(f"📥 Input PDF: {pdf_path}")
    logger.info(f"📤 Output CSV: {output_csv}")
    logger.info("=" * 60)
    
    try:
        # Extract codes
        logger.info("\n🔍 Step 1: Extracting ICD-10 codes from PDF...")
        codes_data = extract_icd10_from_thai_pdf(pdf_path)
        
        if not codes_data:
            logger.warning("⚠️  No ICD-10 codes found in the PDF!")
            return
        
        # Save to CSV
        logger.info("\n💾 Step 2: Saving to CSV file...")
        save_to_csv(codes_data, output_csv)
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ Process completed successfully!")
        logger.info("=" * 60)
        
    except FileNotFoundError:
        logger.error(f"\n❌ PDF file not found: {pdf_path}")
        logger.error("💡 Please ensure the PDF file is in the same directory as this script.")
    except Exception as e:
        logger.error(f"\n❌ Process failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()

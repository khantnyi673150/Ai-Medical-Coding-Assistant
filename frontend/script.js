const API_URL = 'http://localhost:8000';

// Tab switching
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const btns = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    btns.forEach(btn => btn.classList.remove('active'));
    
    if (tabName === 'file') {
        document.getElementById('fileTab').classList.add('active');
        btns[0].classList.add('active');
    } else {
        document.getElementById('textTab').classList.add('active');
        btns[1].classList.add('active');
    }
}

// Extract from file upload
async function matchICDCodes() {
    const fileInput = document.getElementById('icdFile');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showError('Please select a CSV or Excel file');
        return;
    }
    
    const file = fileInput.files[0];
    
    if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
        showError('Please select a valid CSV or Excel file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    loading.style.display = 'block';
    resultDiv.innerHTML = '';
    
    try {
        const response = await fetch(`${API_URL}/match-icd-codes`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Processing failed');
        }
        
        displayResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// Extract from text input
async function extractFromText() {
    const textInput = document.getElementById('patientText');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    
    const text = textInput.value.trim();
    
    if (!text) {
        showError('Please enter patient medical record text');
        return;
    }
    
    loading.style.display = 'block';
    resultDiv.innerHTML = '';
    
    try {
        const response = await fetch(`${API_URL}/api/extract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Extraction failed');
        }
        
        // Format the response
        const formattedData = formatTextExtractionResults(data.data);
        displayResults(formattedData);
        
    } catch (error) {
        showError(error.message);
    } finally {
        loading.style.display = 'none';
    }
}

function formatTextExtractionResults(data) {
    const matched_codes = [];
    
    if (data.primary_diagnosis) {
        matched_codes.push({
            code: "PRIMARY",
            description: data.primary_diagnosis,
            found_in_column: "Primary Diagnosis"
        });
    }
    
    data.secondary_diagnoses?.forEach((diagnosis, idx) => {
        matched_codes.push({
            code: `SEC-${idx + 1}`,
            description: diagnosis,
            found_in_column: "Secondary Diagnoses"
        });
    });
    
    data.complications?.forEach((complication, idx) => {
        matched_codes.push({
            code: `COMP-${idx + 1}`,
            description: complication,
            found_in_column: "Complications"
        });
    });
    
    data.lab_findings?.forEach((finding, idx) => {
        matched_codes.push({
            code: `LAB-${idx + 1}`,
            description: finding,
            found_in_column: "Laboratory Findings"
        });
    });
    
    return {
        statistics: {
            total_matched_codes: matched_codes.length,
            unique_codes: matched_codes.length
        },
        matched_codes: matched_codes
    };
}

function displayResults(data) {
    const resultDiv = document.getElementById('result');
    const stats = data.statistics;
    const results = data.results;
    
    let html = `
        <div class="result-box">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">🤖 AI-Suggested ICD Codes</h2>
            
            <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="margin-bottom: 15px; color: #34495e;">📊 Statistics</h3>
                <div class="result-item">
                    <div class="result-label">Total Records:</div>
                    <div class="result-value">${stats.total_records || 0}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Total ICD Codes Suggested:</div>
                    <div class="result-value">${stats.total_icd_codes_suggested || 0}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Unique ICD Codes:</div>
                    <div class="result-value">${stats.unique_icd_codes || 0}</div>
                </div>
            </div>
        </div>
    `;
    
    if (results && results.length > 0) {
        results.forEach((record) => {
            html += `
                <div class="result-box" style="margin-top: 20px; border-left: 4px solid #27ae60;">
                    <h3 style="color: #27ae60; margin-bottom: 15px;">📋 AN: ${record.AN}</h3>
                    
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #2c3e50; font-size: 1.1em;">Principal Diagnosis:</strong>
                        <div style="margin-left: 20px; margin-top: 8px;">
                            <span style="background: #27ae60; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 600;">${record.principal_diagnosis.code || 'N/A'}</span>
                            <span style="margin-left: 10px; color: #555;">${record.principal_diagnosis.description || 'Not found'}</span>
                        </div>
                    </div>
            `;
            
            if (record.secondary_diagnoses && record.secondary_diagnoses.length > 0) {
                html += `
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #2c3e50;">Secondary Diagnoses:</strong>
                        <ul style="margin-left: 20px; margin-top: 8px; list-style: none; padding: 0;">
                `;
                
                record.secondary_diagnoses.forEach(dx => {
                    html += `
                        <li style="margin-bottom: 6px;">
                            <span style="background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em;">${dx.code}</span>
                            <span style="margin-left: 10px; color: #555;">${dx.description}</span>
                        </li>
                    `;
                });
                
                html += `</ul></div>`;
            }
            
            if (record.complications && record.complications.length > 0) {
                html += `
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #e74c3c;">⚠️ Complications:</strong>
                        <ul style="margin-left: 20px; margin-top: 8px; list-style: none; padding: 0;">
                `;
                
                record.complications.forEach(comp => {
                    html += `
                        <li style="margin-bottom: 6px;">
                            <span style="background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em;">${comp.code}</span>
                            <span style="margin-left: 10px; color: #555;">${comp.description}</span>
                        </li>
                    `;
                });
                
                html += `</ul></div>`;
            }
            
            if (record.laboratory_findings && record.laboratory_findings.length > 0) {
                html += `
                    <div>
                        <strong style="color: #f39c12;">🧪 Laboratory Findings:</strong>
                        <ul style="margin-left: 20px; margin-top: 8px; list-style: disc; padding-left: 20px;">
                `;
                
                record.laboratory_findings.forEach(finding => {
                    html += `<li style="margin-bottom: 4px; color: #555;">${finding}</li>`;
                });
                
                html += `</ul></div>`;
            }
            
            html += `</div>`;
        });
    } else {
        html += `
          <div class="result-box" style="margin-top: 20px; background: #fff3cd; border-color: #ffc107;">
                <h3 style="color: #856404;">⚠️ No Data Found</h3>
                <p style="color: #856404;">No medical information could be extracted from the uploaded file.</p>
            </div>
        `;  // ✅ COMPLETED the closing tags
    }
    
    resultDiv.innerHTML = html;  // ✅ Added this line
}
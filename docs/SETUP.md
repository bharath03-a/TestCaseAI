# How to Run the Healthcare Test Case Generation System

## Quick Start

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Set API Keys
```bash
export GOOGLE_API_KEY="your_gemini_api_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"  # Optional
```

### 3. Run the System
```bash
python run.py
```

## Alternative Methods

### Method 1: Run Examples
```bash
python examples/basic_usage.py
```

### Method 2: Interactive Python
```python
from src.testcaseaiagent.workflows import HealthcareTestCaseGenerator
from src.testcaseaiagent.models import ComplianceStandard

# Initialize
generator = HealthcareTestCaseGenerator()

# Prepare documents
documents = [{
    "filename": "healthcare_requirements.txt",
    "content": "The system shall provide secure patient data management."
}]

# Process
result = generator.process_documents(
    documents=documents,
    compliance_standards=[ComplianceStandard.FDA, ComplianceStandard.HIPAA]
)

print(f"Success: {result['success']}")
print(f"Requirements: {len(result.get('requirements', []))}")
print(f"Test Cases: {len(result.get('test_cases', []))}")
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Run `pip install -e .` first
2. **API Quota Exceeded**: Wait for quota reset or use different API key
3. **NumPy Version Conflict**: Run `pip install "numpy<2.0"`
4. **Import Errors**: Check all dependencies are installed

### Environment Setup

Create a `.env` file (optional):
```bash
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
GEMINI_MODEL_NAME=gemini-1.5-pro
DEBUG_MODE=false
```

## Expected Output

When successful, you should see:
```
Processing Results:
Success: True
Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Requirements Count: X
Test Cases Count: Y
Quality Score: 0.XX
```

## What the System Does

1. **Parses Documents**: Extracts text from PDF, Word, XML, Markdown files
2. **Extracts Requirements**: Uses Gemini AI to identify healthcare requirements
3. **Maps Compliance**: Links requirements to FDA, HIPAA, IEC 62304, ISO standards
4. **Generates Test Cases**: Creates comprehensive test scenarios
5. **Validates Quality**: Assesses completeness and accuracy
6. **Provides Results**: Structured output with metrics and recommendations

## Healthcare Focus

The system understands:
- Medical terminology and concepts
- Regulatory compliance requirements
- Patient safety considerations
- Healthcare workflow processes
- Data privacy and security needs

Ready to generate compliant, traceable test cases for healthcare software!
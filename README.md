# L3 M7.1: Financial Document Types & Regulatory Context

Part of **L3.M7: Financial Compliance & Controls** in the TechVoyageHub L3 FinanceAI track.

## Overview

This module teaches RAG engineers in financial services how to build compliance-aware document classification systems. It covers the identification of 8+ financial document types with regulatory implications, mapping to compliance frameworks, and managing document lifecycle workflows with retention policies and audit trails.

This module demonstrates critical compliance requirements for financial AI systems, including SOX certification, Regulation FD fair disclosure, GLBA privacy requirements, FCRA credit reporting standards, and GDPR data protection.

## Learning Outcomes

After completing this module, you will be able to:

1. **Identify 8+ financial document types** with regulatory implications:
   - 10-K Annual Reports
   - 10-Q Quarterly Reports
   - 8-K Material Event Disclosures
   - Earnings Call Transcripts
   - Credit Reports
   - Loan Applications
   - Internal Financial Analyses
   - Investment Prospectuses

2. **Map documents to compliance frameworks** including:
   - SOX Sections 302/404 (CEO/CFO certification and internal controls)
   - Regulation FD (Fair Disclosure)
   - GLBA (Gramm-Leach-Bliley Act)
   - FCRA (Fair Credit Reporting Act)
   - GDPR Article 25 (Data Protection by Design)
   - Securities Act of 1933
   - ECOA (Equal Credit Opportunity Act)

3. **Classify sensitivity levels** distinguishing:
   - Public Information (filed SEC documents)
   - Material Non-Public Information (MNPI - unfiled reports, internal analyses)
   - Personally Identifiable Information (PII - credit reports, loan applications)

4. **Design document lifecycle workflows** with:
   - Retention policies (7-year SOX minimum, permanent for prospectuses)
   - Audit trails (source, timestamp, user, access logging)
   - Access controls meeting auditor standards
   - PII detection and redaction (99.9% recall threshold)

## Prerequisites

- Python 3.9+
- Basic understanding of financial services and regulatory compliance
- Familiarity with SEC filings (recommended)
- SEC EDGAR account (optional - module works in offline mode)

## Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd financial_ai_ccc_l2

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set EDGAR_ENABLED=true if you have credentials
```

### 2. Run Jupyter Notebook

```bash
# Set Python path
$env:PYTHONPATH = $PWD

# Start Jupyter
jupyter notebook notebooks/L3_M7_Financial_Compliance_Controls.ipynb
```

### 3. Start API Server

```bash
# Using PowerShell script
.\scripts\run_api.ps1

# Or manually
$env:PYTHONPATH = $PWD
$env:EDGAR_ENABLED = "false"
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at: http://localhost:8000/docs

### 4. Run Tests

```bash
# Using PowerShell script
.\scripts\run_tests.ps1

# Or manually
$env:PYTHONPATH = $PWD
pytest -v tests/
```

## Project Structure

```
financial_ai_ccc_l2/
├── app.py                              ← FastAPI entrypoint
├── config.py                           ← Environment & EDGAR client
├── requirements.txt                    ← Pinned dependencies
├── .env.example                        ← Configuration template
├── .gitignore                          ← Python defaults
├── LICENSE                             ← MIT License
├── README.md                           ← This file
├── example_data.json                   ← Sample documents
├── example_data.txt                    ← Sample text data
│
├── src/                                ← Source code
│   └── l3_m7_financial_compliance_controls/
│       └── __init__.py                 ← Core business logic
│
├── notebooks/                          ← Jupyter notebooks
│   └── L3_M7_Financial_Compliance_Controls.ipynb
│
├── tests/                              ← Test suite
│   └── test_m7_financial_compliance_controls.py
│
├── configs/                            ← Configuration files
│   └── example.json
│
└── scripts/                            ← Automation scripts
    ├── run_api.ps1                     ← Start API server
    └── run_tests.ps1                   ← Run tests
```

## How It Works

### Architecture Overview

The system implements a **compliance-aware document classification pipeline** with the following components:

1. **Document Classifier**: Identifies document type using pattern matching and content heuristics
2. **Regulatory Mapper**: Maps document types to applicable compliance frameworks
3. **Sensitivity Classifier**: Determines sensitivity level (Public/MNPI/PII)
4. **Retention Policy Manager**: Calculates retention periods and deletion dates
5. **PII Detector**: Detects and redacts personally identifiable information
6. **Audit Logger**: Tracks all document access and operations
7. **Access Controller**: Enforces role-based access controls
8. **Material Event Detector**: Identifies events requiring Form 8-K filing

### Key Components

#### 1. Document Classification
Classifies documents into 8 core types using SEC filing identifiers, content patterns, and terminology:
- **10-K Annual Report**: SOX 302/404 certification, 7-year retention
- **10-Q Quarterly Report**: Similar to 10-K but unaudited, 7-year retention
- **8-K Material Event Disclosure**: 4-day filing deadline, Regulation FD compliance
- **Earnings Call Transcript**: Regulation FD compliance, MNPI during call
- **Credit Report**: FCRA/GLBA/GDPR compliance, 40+ PII fields, 7-year retention
- **Loan Application**: ECOA/GLBA compliance, 25-month minimum retention
- **Internal Financial Analysis**: SOX 404 controls, MNPI classification
- **Investment Prospectus**: Securities Act 1933, permanent retention

#### 2. Regulatory Framework Mapping
Maps each document type to applicable regulations:
- **SOX 302**: CEO/CFO certification with criminal liability (up to 20 years)
- **SOX 404**: Internal controls with 7-year retention requirement
- **Regulation FD**: Fair disclosure preventing selective material information sharing
- **GLBA**: Privacy notices, safeguards rule, access logging
- **FCRA**: Credit report accuracy and consumer dispute rights
- **GDPR Article 25**: Data protection by design (4% revenue or €20M fine)
- **ECOA**: Equal credit opportunity with 25-month retention minimum

#### 3. Sensitivity Classification
Three-level classification based on document type and filing status:
- **Public**: Filed SEC documents, published earnings transcripts
- **MNPI**: Unfiled 10-K/10-Q/8-K, internal analyses, ongoing earnings calls
- **PII**: Credit reports, loan applications, customer data

#### 4. Retention Policies
Automated retention period calculation:
- **7 years**: SOX-regulated documents (10-K, 10-Q, 8-K, credit reports)
- **3 years**: Loan applications (ECOA 25-month minimum)
- **Permanent**: Investment prospectuses (fraud claim protection)

#### 5. PII Detection & Redaction
High-recall detection (99.9% threshold) for:
- Social Security Numbers (SSN)
- Phone numbers
- Email addresses
- Account numbers
- Dates of birth
- Physical addresses

#### 6. Material Event Detection
Identifies events requiring Form 8-K filing within 4 business days:
- Bankruptcy filings (Chapter 11)
- Acquisitions and mergers
- Management changes (CEO/CFO resignations)
- Accounting restatements
- Material asset sales
- Regulatory investigations

### Workflow

1. **Document Ingestion**: Upload document via API or notebook
2. **Type Classification**: Identify document type using pattern matching
3. **Regulatory Mapping**: Determine applicable compliance frameworks
4. **Sensitivity Assessment**: Classify as Public/MNPI/PII
5. **PII Scanning**: Detect and optionally redact sensitive information
6. **Material Event Check**: Flag events requiring legal review
7. **Access Control**: Enforce role-based permissions
8. **Audit Logging**: Record all access and operations
9. **Retention Calculation**: Determine storage and deletion requirements

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/

Response:
{
  "status": "healthy",
  "module": "L3_M7_Financial_Compliance_Controls",
  "edgar_enabled": "false",
  "version": "1.0.0"
}
```

### Document Classification
```bash
POST http://localhost:8000/classify
Content-Type: application/json

{
  "document_text": "FORM 10-K ANNUAL REPORT...",
  "metadata": {"is_filed": true},
  "offline": false
}

Response:
{
  "document_type": "10-K Annual Report",
  "sensitivity_level": "Public Information",
  "regulatory_frameworks": ["SOX Section 302", "SOX Section 404"],
  "retention_period_years": 7,
  "pii_detected": false,
  "material_events_detected": false
}
```

### Regulatory Mapping
```bash
POST http://localhost:8000/regulatory-mapping

{
  "document_type": "10-K Annual Report"
}
```

### Sensitivity Classification
```bash
POST http://localhost:8000/sensitivity

{
  "document_type": "10-K Annual Report",
  "is_filed": true
}
```

### PII Detection & Redaction
```bash
POST http://localhost:8000/pii-detection

{
  "text": "Customer SSN: 123-45-6789",
  "redact": true
}
```

### Access Control Check
```bash
POST http://localhost:8000/access-control

{
  "user_role": "analyst",
  "document_type": "10-K Annual Report",
  "is_filed": false
}
```

### Retention Policy Query
```bash
POST http://localhost:8000/retention-policy

{
  "document_type": "Investment Prospectus"
}
```

### Material Event Detection
```bash
POST http://localhost:8000/material-events

{
  "text": "The company announces the acquisition of TargetCo for $500 million."
}
```

## Usage Examples

### Example 1: Classify a 10-K Annual Report
```python
from src.l3_m7_financial_compliance_controls import classify_document

doc_text = """
FORM 10-K
ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d)
For the fiscal year ended December 31, 2023
"""

result = classify_document(doc_text, metadata={"is_filed": True}, offline=True)

print(f"Document Type: {result['document_type']}")
print(f"Sensitivity: {result['sensitivity_level']}")
print(f"Retention: {result['retention_period_years']} years")
print(f"Regulations: {', '.join(result['regulatory_frameworks'])}")
```

### Example 2: Detect and Redact PII from Credit Report
```python
from src.l3_m7_financial_compliance_controls import detect_pii

credit_report = """
CREDIT REPORT
SSN: 123-45-6789
Email: customer@example.com
Phone: 555-123-4567
Credit Score: 720
"""

redacted_text, detections = detect_pii(credit_report)

print(f"PII Detected: {len(detections)} instances")
print(f"Redacted Text:\n{redacted_text}")
```

### Example 3: Check Access Control
```python
from src.l3_m7_financial_compliance_controls import check_access_control, DocumentType

# Can an analyst access unfiled 10-K?
has_access = check_access_control(
    user_role="analyst",
    doc_type=DocumentType.FORM_10K,
    is_filed=False
)

print(f"Analyst access to unfiled 10-K: {has_access}")  # True (MNPI access)

# Can an employee access credit reports?
has_access = check_access_control(
    user_role="employee",
    doc_type=DocumentType.CREDIT_REPORT,
    is_filed=False
)

print(f"Employee access to credit reports: {has_access}")  # False (PII restricted)
```

### Example 4: Detect Material Events
```python
from src.l3_m7_financial_compliance_controls import MaterialEventDetector

detector = MaterialEventDetector()

internal_memo = """
The CEO has resigned effective immediately.
The Board has appointed an interim CEO while conducting a search.
"""

events = detector.detect_material_events(internal_memo)

if events:
    print("⚠️ Material events detected - 8-K filing required within 4 business days")
    for event in events:
        print(f"  - {event['event_type']}: {event['keyword']}")
```

### Example 5: Calculate Retention Period
```python
from src.l3_m7_financial_compliance_controls import RetentionPolicyManager, DocumentType
from datetime import datetime

manager = RetentionPolicyManager()

# 10-K retention
period = manager.get_retention_period(DocumentType.FORM_10K)
print(f"10-K retention period: {period} years")

# Calculate deletion date
creation_date = datetime(2020, 1, 1)
deletion_date = manager.calculate_deletion_date(DocumentType.FORM_10K, creation_date)
print(f"Can be deleted after: {deletion_date.strftime('%Y-%m-%d')}")

# Prospectus (permanent retention)
period = manager.get_retention_period(DocumentType.PROSPECTUS)
print(f"Prospectus retention: {'Permanent' if period is None else f'{period} years'}")
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EDGAR_ENABLED` | No | `false` | Enable EDGAR API integration |
| `EDGAR_USER_AGENT` | Yes* | - | User agent for EDGAR requests (format: "CompanyName email@example.com") |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `OFFLINE` | No | `false` | Force offline mode (skip all external API calls) |

*Required only if EDGAR_ENABLED=true

### Role-Based Access Control

| Role | Public | MNPI | PII |
|------|--------|------|-----|
| Executive | ✓ | ✓ | ✓ |
| Compliance Officer | ✓ | ✓ | ✓ |
| Analyst | ✓ | ✓ | ✗ |
| Auditor | ✓ | ✓ | ✗ |
| Credit Officer | ✓ | ✗ | ✓ |
| Employee | ✓ | ✗ | ✗ |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Tesla CEO "take private" tweet (2018)** | Material information tweeted without Form 8-K filing | $20M SEC fine; always file 8-K within 4 business days for material events |
| **Netflix CEO Facebook post (2013)** | Q3 subscriber numbers posted on personal Facebook (selective disclosure) | $5M SEC fine; ensure Regulation FD compliance with simultaneous public disclosure |
| **Equifax breach (2017)** | 147 million credit reports exposed due to unpatched vulnerability | $700M settlement; implement PII encryption, access logging, security controls per GLBA |
| **2015 hedge fund insider trading** | Intern accessed M&A analysis without authorization | SEC investigation and imprisonment; enforce strict access controls and audit trails |
| **Missed SSN redaction** | PII leakage in document processing | Failed FCRA compliance; use 99.9% recall threshold for PII detection |
| **SOX certification failure** | CEO/CFO signed 10-K with material misstatements | Criminal liability (up to 20 years); implement rigorous internal controls and review processes |
| **Regulation FD violation** | Material guidance shared with select analysts before public disclosure | SEC enforcement action; monitor all communications for material information |
| **GDPR Right to be Forgotten failure** | Unable to delete EU customer data on request | €20M or 4% revenue fine; implement data deletion workflows |
| **ECOA retention violation** | Loan application deleted before 25-month minimum | Discrimination audit failure; enforce automated retention policies |
| **Prospectus version control failure** | Unable to prove which version investors received | Securities fraud litigation exposure; implement strict version control |

## Decision Card

### When to Use

✅ Building RAG systems for **public companies or SEC-regulated entities**
✅ Processing **SEC filings** (10-K, 10-Q, 8-K)
✅ Handling **customer credit reports or loan applications**
✅ Managing **earnings call transcripts or investor relations materials**
✅ Building **financial Q&A chatbots** using material information
✅ Operating in **regulated jurisdictions** (US SEC, EU GDPR)
✅ Systems requiring **SOX 404 internal controls** compliance
✅ Applications with **7-year audit trail** requirements

### When NOT to Use

❌ System handles **exclusively non-regulated financial content**
❌ **No customer PII** involved
❌ **No SEC filing requirements** apply
❌ **Document retention requirements cannot be enforced** technically
❌ **No compliance officer or legal counsel** oversight available
❌ Processing **non-US financial documents** without applicable US regulations
❌ **Real-time trading systems** (requires specialized low-latency architecture)

### Trade-offs

**Cost:**
- **High initial implementation cost** due to compliance complexity
- Requires legal counsel review ($5,000-$50,000)
- External audit requirements for SOX 404 ($10,000-$100,000 annually)
- Ongoing compliance monitoring and maintenance

**Latency:**
- PII detection adds 50-200ms per document
- Audit logging adds 10-50ms per operation
- Access control checks add 5-20ms per request
- Material event detection adds 100-300ms per document

**Complexity:**
- 8 document types with distinct regulatory requirements
- 9 compliance frameworks with overlapping rules
- Role-based access control matrix (6 roles × 3 sensitivity levels)
- Retention policies ranging from 25 months to permanent
- 99.9% recall threshold for PII detection
- 4-business-day material event filing deadlines

**Benefits:**
- **Criminal liability protection** for executives (SOX 302)
- **Regulatory compliance** reducing SEC enforcement risk
- **Audit-ready** documentation and trails
- **PII protection** preventing data breach litigation
- **Material event detection** preventing Regulation FD violations
- **Automated retention** ensuring compliance without manual tracking

## Production Compliance Checklist

Before deploying to production, ensure:

- [ ] **CFO approval** for financial accuracy and SOX certification
- [ ] **Chief Compliance Officer review** for regulatory compliance
- [ ] **Securities counsel approval** for SEC/FINRA requirements
- [ ] **External auditor assessment** for SOX 404 internal controls
- [ ] **Data retention policy enforcement** (7-year SOX minimum, variable by document type)
- [ ] **Audit trail implementation** (source, timestamp, user, access, output logging)
- [ ] **Access control matrix** (role-based restrictions for MNPI/PII)
- [ ] **PII detection and redaction** with 99.9% recall threshold
- [ ] **Adverse action tracking** for loan/credit decisions
- [ ] **Dispute workflow** for credit report inaccuracies
- [ ] **Version control** for prospectuses and legally-reviewed documents
- [ ] **Material event detection** and legal review escalation procedures
- [ ] **Regulation FD compliance monitoring** for earnings calls
- [ ] **GDPR Right to be Forgotten** implementation for EU customers
- [ ] **Third-party vendor assessment** (LLM providers, database services)

## Troubleshooting

### EDGAR Service Disabled Mode

The module runs without external EDGAR integration if `EDGAR_ENABLED` is not set to `true` in `.env`. The `config.py` file will skip client initialization, and API endpoints will return skipped responses. This is the default behavior and is useful for local development or testing.

To enable EDGAR integration:
```bash
# In .env file
EDGAR_ENABLED=true
EDGAR_USER_AGENT=CompanyName email@example.com
```

### Import Errors

If you see `ModuleNotFoundError: No module named 'src.l3_m7_financial_compliance_controls'`, ensure:

```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD

# Linux/Mac bash
export PYTHONPATH=$PWD
```

### Tests Failing

Run tests with verbose output to diagnose:
```bash
pytest -v tests/
```

Common issues:
- Python path not set → Set `PYTHONPATH` before running tests
- Missing dependencies → Run `pip install -r requirements.txt`
- Package not found → Ensure `src/l3_m7_financial_compliance_controls/__init__.py` exists

### API Not Starting

Check for port conflicts:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Use alternate port if needed:
```bash
uvicorn app:app --port 8080
```

## Important Disclaimers

⚠️ **This module provides technical implementation guidance ONLY**

This training is NOT:
- Financial advice or investment recommendations
- Legal counsel or regulatory approval
- Substitute for compliance officer review
- Guarantee of regulatory compliance

Organizations remain **fully responsible** for compliance. Improper implementation risks:
- **SEC enforcement actions** and investigations
- **Criminal liability for executives** (SOX 302: up to 20 years imprisonment)
- **Multi-million dollar fines** (GDPR: 4% global revenue or €20M)
- **Failed audits** and delayed financial reporting
- **Shareholder lawsuits** and reputational damage
- **Data breach litigation** (Equifax: $700M settlement)

**Always engage:**
- Chief Financial Officer (CFO)
- Chief Compliance Officer (CCO)
- Securities Counsel
- External Auditors

**Before production deployment.**

## Next Module

Continue to **L3 M7.2: Document Retention and Audit Trail Implementation** to learn about:
- Advanced audit trail architecture
- Immutable logging systems
- Compliance-ready data warehousing
- SOX 404 control testing automation

## License

MIT License - See [LICENSE](LICENSE) file for details.

## References

- SEC EDGAR Database: https://www.sec.gov/edgar
- Sarbanes-Oxley Act (2002): SOX Sections 302, 404
- Regulation FD: https://www.sec.gov/rules/final/33-7881.htm
- GLBA Privacy Rule: https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act
- FCRA: https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act
- GDPR Article 25: https://gdpr-info.eu/art-25-gdpr/
- ECOA: https://www.consumerfinance.gov/rules-policy/regulations/1002/

---

**Built with TechVoyageHub PractaThon™ standards**

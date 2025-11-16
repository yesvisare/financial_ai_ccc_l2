# L3 M9.3: Regulatory Constraints in LLM Outputs (MNPI, Disclaimers, Safe Harbor)

## Overview

**Duration:** 45-50 minutes | **Level:** L2+ SkillElevate | **Track:** Finance AI (Domain-Specific)

This module implements a **three-layer compliance framework** for financial LLM systems that prevents securities law violations, ensures regulatory compliance, and creates audit trails for SEC investigations.

**The Hook Problem:** An LLM inadvertently surfaces internal financial forecasts before public announcement, creating potential Regulation Fair Disclosure (Reg FD) violations and securities law exposure. Without proper filtering, a single leaked earnings projection could trigger SEC enforcement actions, shareholder lawsuits, and criminal liability for insider trading.

This module solves that problem by implementing:
- **MNPI Detection:** Prevents Material Non-Public Information disclosure (98%+ recall required)
- **Disclaimer Requirements:** Ensures FINRA Rule 2210 and Safe Harbor compliance
- **Information Barriers:** Implements Chinese Walls to prevent selective disclosure

## What You'll Learn

By completing this module, you will master:

1. **Detect Material Non-Public Information (MNPI)** in LLM outputs using pattern matching, source validation, and materiality thresholds (98%+ recall required to avoid catastrophic regulatory violations)

2. **Implement systematic disclaimers** ("Not Investment Advice", Safe Harbor statements) that meet FINRA Rule 2210 and Private Securities Litigation Reform Act standards

3. **Build information barriers (Chinese Walls)** preventing selective disclosure and Regulation FD violations through role-based access control and data namespace separation

4. **Create compliance audit trails** that survive SEC investigations and shareholder litigation with timestamped violation logs, user tracking, and action documentation

## How It Works

The system uses a **three-layer compliance framework** that processes LLM outputs through sequential checks:

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Output (Raw)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
          ┌───────────────────────────┐
          │   Layer 1: MNPI Detection │
          │   ─────────────────────── │
          │   • Source Validation     │
          │   • Materiality Indicators│
          │   • Temporal Check        │
          └───────────┬───────────────┘
                      │
                   ≥2 layers flagged OR
                   confidence ≥ 0.9?
                      │
            ┌─────────┴─────────┐
            │                   │
           YES                 NO
            │                   │
            ▼                   ▼
    ┌──────────────┐   ┌──────────────────┐
    │ BLOCK        │   │ Layer 2:         │
    │ Response     │   │ Disclaimer       │
    │ Log Violation│   │ Requirements     │
    └──────────────┘   └────────┬─────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Layer 3:              │
                    │ Information Barriers  │
                    │ (Chinese Walls)       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Filtered Output       │
                    │ + Disclaimers         │
                    │ + Audit Log Entry     │
                    └───────────────────────┘
```

**Three-Layer Decision Logic:**
- **Layer 1 - MNPI Detection:** Source validation (internal vs. public documents), materiality indicator matching (earnings, M&A, executive changes), temporal check (disclosed or still internal?)
- **Layer 2 - Disclaimer Requirements:** Automatic injection of FINRA Rule 2210 disclaimers for investment advice patterns and Safe Harbor statements for forward-looking predictions
- **Layer 3 - Information Barriers:** Chinese Walls preventing selective disclosure by restricting MNPI access to authorized personnel only

**Blocking Criteria:** If ≥2 layers flag MNPI OR single high-confidence violation (0.9+) → BLOCK response and log violation.

## Key Concepts

### Concept 1: Material Non-Public Information (MNPI)

**Definition:** Information that could reasonably affect a company's stock price AND hasn't been disclosed simultaneously to all investors.

**Examples:**
- ✅ **Public:** "Q3 earnings were $2.5 billion" (filed 10-Q, publicly available)
- ❌ **MNPI:** "Q4 earnings will be $3 billion" (internal forecast, not yet disclosed)
- ✅ **Public:** "CEO announced retirement" (press release issued)
- ❌ **MNPI:** "Board considering CFO replacement" (board minutes, confidential)

**Why it Matters:** Disclosing MNPI violates:
- Securities Exchange Act Section 10(b) and Rule 10b-5 (fraud, insider trading)
- Regulation Fair Disclosure (Reg FD) - selective disclosure prohibition
- Potential criminal liability under 15 U.S.C. § 78ff (up to 20 years imprisonment)

**Detection Approach:** Three-check pattern:
1. **Source Validation:** Is citation from internal document? (draft, confidential, board minutes, email, memo)
2. **Materiality Indicators:** Does text contain material event keywords? (earnings, merger, executive change, product launch)
3. **Temporal Check:** Was this information publicly disclosed before citation date?

If ≥2 checks fail → MNPI violation → BLOCK response.

### Concept 2: Regulation FD (Fair Disclosure)

**Definition:** SEC rule requiring public companies to disclose material information to all investors simultaneously, not selectively.

**Violation Example:**
- Company executive tells analyst in private call: "Q4 guidance will be revised upward"
- Analyst trades on this information before public announcement
- Result: Reg FD violation, SEC enforcement, potential criminal charges

**Information Barriers (Chinese Walls):** Prevents selective disclosure by:
- Maintaining separate data namespaces: `public`, `internal`, `restricted`
- Implementing role-based access control (RBAC)
- Filtering citations based on user permissions
- Logging all access attempts for audit trail

**Implementation:**
```python
# User with "public" access cannot see internal forecasts
user_permissions = {
    "analyst_external": ["public"],
    "analyst_internal": ["public", "internal"],
    "executive": ["public", "internal", "restricted"]
}
```

### Concept 3: Safe Harbor Provisions (Private Securities Litigation Reform Act)

**Definition:** Legal protection for forward-looking statements accompanied by meaningful cautionary language.

**Forward-Looking Statements:**
- Revenue/earnings projections
- Business plans and strategies
- Expected product launches
- Anticipated market conditions

**Safe Harbor Requirements:**
1. Identify statement as forward-looking
2. Include meaningful cautionary language about risks
3. Provide substantive disclosure of risk factors
4. Statement not made with actual knowledge of falsity

**Example Disclaimer:**
```
⚠️ SAFE HARBOR STATEMENT: This response contains forward-looking statements that
involve risks and uncertainties. Actual results may differ materially. See our SEC
filings for risk factors. (Private Securities Litigation Reform Act of 1995)
```

**When Required:**
- Text contains: "will", "expect", "anticipate", "project", "forecast", "estimate", "believe"
- Future-oriented predictions: "Q4 2024 revenue", "planned product launch"
- Business outlook: "growth expectations", "market opportunities"

### Concept 4: FINRA Rule 2210 (Communications with the Public)

**Definition:** FINRA regulation governing financial communications, requiring balanced presentation and risk disclosure.

**Investment Advice Patterns:**
- "Recommend buying XYZ stock"
- "This stock is undervalued/overvalued"
- "Target price is $50"
- "Buy/Sell/Hold rating"

**Required Disclaimer:**
```
⚠️ DISCLAIMER: This information is for educational purposes only and does not
constitute investment advice. Consult a registered financial advisor before making
investment decisions. (FINRA Rule 2210)
```

**Why Critical:** Providing investment advice without registration violates:
- Securities Exchange Act Section 15(a) - unlicensed broker-dealer
- Investment Advisers Act Section 203(a) - unlicensed investment adviser
- Potential SEC enforcement, civil penalties, criminal prosecution

## Prerequisites

- **Generic CCC M1-M4:** RAG architecture, optimization, deployment, evaluation
- **Finance AI M9.1:** Explainability & Citation Tracking (provides citation metadata)
- **Finance AI M9.2:** Risk Assessment in Retrieval (provides risk scores)
- **Regulatory Knowledge:** Understanding of financial compliance frameworks (FINRA, SEC, Reg FD)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd fai_m9_v3
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install spaCy Model (REQUIRED)
```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration:
# REQUIRED:
#   - Set POSTGRES_PASSWORD (for compliance database)
# OPTIONAL:
#   - Set ANTHROPIC_ENABLED=true and ANTHROPIC_API_KEY (for M9.1 integration)
```

### 6. Set Up PostgreSQL Database (REQUIRED)
```bash
# Create database
createdb financial_compliance

# (Optional) Run migrations if available
python scripts/init_db.py
```

### 7. Verify Configuration
```bash
python config.py
```

You should see:
```
✅ All required services ready
  PostgreSQL (Compliance DB):   ✅
  spaCy (NLP):                  ✅
  Anthropic (M9.1 Integration): ⚠️  Optional
  Redis (Caching):              ⚠️  Optional
```

## Usage

### API Mode (Recommended for Production)

**Start the FastAPI server:**
```powershell
# Windows PowerShell
.\scripts\run_api.ps1

# Or manually:
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/

# Filter LLM output
curl -X POST http://localhost:8000/filter \
  -H "Content-Type: application/json" \
  -d '{
    "llm_output": "Q4 earnings will exceed $3B based on internal forecasts",
    "citations": [
      {
        "source_id": "internal_forecast_2024",
        "source_type": "internal memo",
        "data_namespace": "internal"
      }
    ],
    "user_id": "analyst_123"
  }'

# Expected: MNPI violation detected, response blocked

# MNPI detection only
curl -X POST http://localhost:8000/mnpi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Q3 earnings were $2.5B according to 10-Q filing",
    "citations": [{"source_type": "10-Q", "source_id": "sec_filing"}]
  }'

# Expected: No violation (public information)

# Disclaimer injection
curl -X POST http://localhost:8000/disclaimers/inject \
  -H "Content-Type: application/json" \
  -d '{"text": "We recommend buying XYZ stock at current prices"}'

# Expected: Investment advice disclaimer added

# Retrieve audit logs
curl -X POST http://localhost:8000/audit/logs \
  -H "Content-Type: application/json" \
  -d '{"user_id": "analyst_123", "limit": 50}'
```

### Python Package Mode

```python
from src.l3_m9_financial_compliance_risk import filter_llm_output

# Simple filtering
result = filter_llm_output(
    llm_output="Q3 earnings were $2.5B (from 10-Q filing)",
    citations=[
        {"source_type": "10-Q", "source_id": "sec_20231115"}
    ],
    user_id="analyst_external"
)

print(f"Allowed: {result['allowed']}")
print(f"Filtered text: {result['filtered_text']}")
print(f"Disclaimers: {result['disclaimers_added']}")

# Advanced filtering with risk score
from src.l3_m9_financial_compliance_risk import ComplianceFilter

compliance = ComplianceFilter()

result = compliance.filter_output(
    llm_output="Based on internal projections, Q4 revenue will grow 15%",
    citations=[
        {
            "source_type": "internal planning document",
            "source_id": "budget_2024",
            "data_namespace": "restricted",
            "filing_date": None
        }
    ],
    user_id="analyst_external",
    risk_score=0.95  # High risk from M9.2
)

if not result['allowed']:
    print(f"BLOCKED: {result['blocked_reason']}")
    print(f"Violation details: {result['violation_details']}")
```

### Jupyter Notebook Mode (Interactive Learning)

```bash
jupyter notebook notebooks/L3_M9_Financial_Compliance_Risk.ipynb
```

The notebook provides:
- **Learning Arc:** 5-stage framework (Hook → Concept → Code → Challenge → Confidence)
- **Interactive Examples:** Test MNPI detection, disclaimers, information barriers
- **Hands-on Exercises:** Build compliance filters for real financial scenarios
- **Failure Analysis:** Learn from common mistakes and edge cases

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_ENABLED` | No | `false` | Enable Anthropic service for M9.1 integration |
| `ANTHROPIC_API_KEY` | Yes* | - | Anthropic API key (*required if enabled) |
| `POSTGRES_HOST` | Yes | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | Yes | `5432` | PostgreSQL port |
| `POSTGRES_DB` | Yes | `financial_compliance` | Database name |
| `POSTGRES_USER` | Yes | `postgres` | Database user |
| `POSTGRES_PASSWORD` | Yes | - | Database password (**REQUIRED**) |
| `REDIS_HOST` | No | `localhost` | Redis host (optional caching) |
| `REDIS_PORT` | No | `6379` | Redis port |
| `REDIS_DB` | No | `0` | Redis database number |
| `MNPI_DETECTION_THRESHOLD` | No | `0.85` | MNPI confidence threshold (0.0-1.0) |
| `ENABLE_AUTO_DISCLAIMERS` | No | `true` | Auto-inject disclaimers when patterns detected |
| `ESCALATE_INVESTMENT_ADVICE` | No | `true` | Flag investment advice for human review |
| `DEBUG` | No | `false` | Enable debug logging |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |

## Common Failures & Solutions

### Reality Check: What Actually Goes Wrong

| Failure Mode | Cause | Detection | Solution | Severity |
|--------------|-------|-----------|----------|----------|
| **False Negatives (MNPI Leak)** | Low detection threshold, incomplete materiality indicators | Missed MNPI in output, no violation logged | Increase threshold to 0.90+, expand keyword patterns, add manual review queue | ⚠️ CATASTROPHIC - SEC enforcement, criminal liability |
| **False Positives (Over-blocking)** | High detection threshold, overly aggressive patterns | Legitimate public info blocked, user complaints | Lower threshold to 0.80, refine patterns, whitelist common phrases | ⚠️ ACCEPTABLE - Business inconvenience vs. legal risk |
| **Stale Disclosure Database** | `public_disclosures` not updated with recent SEC filings | Public info flagged as MNPI | Implement automated EDGAR filing ingestion, daily sync, staleness alerts | ⚠️ HIGH - False positives reduce system usability |
| **Missing Citation Metadata** | M9.1 integration incomplete, source_type empty | MNPI check passes with null citations | Validate M9.1 output schema, require source_type field, fail-safe to block | ⚠️ CRITICAL - Bypass MNPI detection |
| **Threshold Miscalibration** | Wrong balance between precision and recall | Too many false positives OR false negatives | Run precision/recall analysis, A/B test thresholds, monitor violation logs | ⚠️ HIGH - Impacts both compliance and usability |
| **Selective Disclosure Bypass** | User permissions not enforced, namespace mismatch | Internal data accessible to external users | Audit RBAC mappings, enforce namespace checks, log access denials | ⚠️ CRITICAL - Reg FD violation |
| **Disclaimer Not Injected** | Pattern matching incomplete, disable flag set | Investment advice without disclaimer | Expand pattern coverage, validate auto-inject enabled, manual review | ⚠️ HIGH - FINRA Rule 2210 violation |
| **Audit Log Not Persisted** | Database connection failure, logging disabled | No compliance record for violations | Monitor DB health, enable retry logic, fail-safe to block if logging fails | ⚠️ CRITICAL - Cannot survive SEC investigation |

### Threshold Tuning Guide

**MNPI Detection Threshold:**
- **0.70-0.80:** High recall (catches more violations), many false positives, acceptable for conservative compliance
- **0.85 (Recommended):** Balanced precision/recall, suitable for production
- **0.90-0.95:** High precision (fewer false positives), risk of false negatives, requires manual review layer

**Testing Approach:**
1. Create labeled dataset of MNPI vs. public information
2. Run detection across threshold range (0.70-0.95)
3. Plot precision-recall curve
4. Select threshold where recall ≥ 0.98 (miss <2% of violations)
5. Monitor production logs and adjust based on false positive rate

## Decision Card

### When to Use This Approach

✅ **Financial applications with regulatory requirements:**
- Banks, broker-dealers, investment advisers (FINRA/SEC regulated)
- Public companies handling earnings, M&A, executive changes
- Applications processing SEC filings, internal forecasts, board minutes

✅ **Systems handling material information:**
- RAG systems with access to both public and internal documents
- LLMs answering investor questions, analyst queries
- Automated financial report generation

✅ **Applications requiring audit trails:**
- Systems subject to SEC examinations, shareholder litigation
- Compliance monitoring for Reg FD, insider trading rules
- Applications needing legal defensibility

### When NOT to Use

❌ **Non-financial applications:**
- Healthcare, e-commerce, general knowledge systems (different compliance frameworks)
- Applications with no securities law obligations

❌ **Internal-only systems with no disclosure risk:**
- Employee-facing tools with no external access
- Systems processing only public data (no MNPI access)
- Read-only archive/research applications

❌ **Pure educational AI:**
- No trading decisions, no material information
- Historical market data analysis (no forward-looking statements)

### Performance Considerations

**Latency Impact:**
- MNPI detection: ~50-100ms per response (pattern matching, database lookups)
- Disclaimer injection: ~10ms (regex matching)
- Information barrier check: ~5ms (RBAC validation)
- Total overhead: ~65-115ms per filtered response

**Scale Optimization:**
- Cache `public_disclosures` in Redis (TTL: 24 hours)
- Pre-compile regex patterns at initialization
- Batch database queries for materiality indicators
- Use async processing for audit logging

**Database Requirements:**
- PostgreSQL with indexes on `public_disclosures.date`, `mnpi_indicators.pattern`
- Expected volume: 100K-1M compliance checks/day → ~10GB/year audit logs
- Retention: 7 years (SEC record-keeping requirement)

### Trade-offs

**Precision vs. Recall:**
- **High Precision (fewer false positives):** Risk missing actual MNPI violations → catastrophic liability
- **High Recall (fewer false negatives):** More false positives → user frustration, over-blocking
- **Recommendation:** Prioritize recall (98%+) over precision for MNPI detection

**Automation vs. Human Review:**
- **Full Automation:** Fast, scalable, but risk of bypassed violations
- **Manual Review Queue:** Catches edge cases, but slow and expensive
- **Recommendation:** Auto-block high-confidence violations (≥0.9), escalate medium confidence (0.7-0.89) to human review

**Source Validation Strictness:**
- **Strict (block unknown sources):** Maximum safety, but blocks legitimate queries with incomplete metadata
- **Permissive (allow unknown sources):** Better UX, but risk of MNPI leaks
- **Recommendation:** Fail-safe to block if citation metadata incomplete or source_type empty

## Testing

### Run Test Suite
```powershell
# Windows PowerShell
.\scripts\run_tests.ps1

# Or manually:
pytest -v tests/

# With coverage report:
pytest --cov=src --cov-report=html tests/
```

### Test Coverage

The test suite includes:
- **MNPI Detection:** Source validation, materiality indicators, temporal checks, multi-layer flagging
- **Disclaimer Injection:** Investment advice patterns, forward-looking statements, Safe Harbor compliance
- **Information Barriers:** RBAC enforcement, namespace filtering, access denial logging
- **Compliance Filter:** End-to-end pipeline, blocking logic, audit trail creation
- **Edge Cases:** Empty citations, null metadata, threshold boundary conditions

**Expected Output:**
```
tests/test_m9_financial_compliance_risk.py::test_mnpi_source_validation PASSED
tests/test_m9_financial_compliance_risk.py::test_mnpi_materiality_indicators PASSED
tests/test_m9_financial_compliance_risk.py::test_mnpi_temporal_check PASSED
tests/test_m9_financial_compliance_risk.py::test_disclaimer_investment_advice PASSED
tests/test_m9_financial_compliance_risk.py::test_disclaimer_forward_looking PASSED
tests/test_m9_financial_compliance_risk.py::test_information_barrier_access_control PASSED
tests/test_m9_financial_compliance_risk.py::test_compliance_filter_blocking PASSED
tests/test_m9_financial_compliance_risk.py::test_compliance_audit_logging PASSED

======================== 15 passed in 2.34s ========================
```

## Project Structure

```
fai_m9_v3/
├── app.py                              # FastAPI entrypoint (8 endpoints)
├── config.py                           # Environment & database management
├── requirements.txt                    # Pinned dependencies (ANTHROPIC detected)
├── .env.example                        # Environment template (ANTHROPIC_API_KEY)
├── .gitignore                          # Python defaults + notebooks
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample queries and test cases
├── example_data.txt                    # Text-format examples
│
├── src/                                # Source code package
│   └── l3_m9_financial_compliance_risk/
│       └── __init__.py                 # Core business logic (4 classes, 500+ LOC)
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M9_Financial_Compliance_Risk.ipynb  # Interactive walkthrough
│
├── tests/                              # Test suite
│   └── test_m9_financial_compliance_risk.py   # 15+ test cases
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Start API server (Windows)
    └── run_tests.ps1                   # Run test suite (Windows)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service status |
| `/filter` | POST | Complete compliance filtering pipeline |
| `/mnpi/detect` | POST | MNPI detection only (no disclaimers) |
| `/disclaimers/inject` | POST | Disclaimer injection only (no MNPI check) |
| `/barriers/check` | POST | Information barrier access control check |
| `/audit/logs` | POST | Retrieve compliance audit logs |
| `/filter/batch` | POST | Batch processing for multiple requests |

See `app.py` for detailed request/response schemas.

## Learning Resources

- **Augmented Script:** [GitHub Link](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_FinanceAI_M9_3_Regulatory_Constraints_LLM_Outputs.md)
- **Track:** Finance AI (Domain-Specific)
- **Level:** L2+ SkillElevate
- **Duration:** 45-50 minutes
- **Prerequisites:** Generic CCC M1-M4, Finance AI M9.1-M9.2

## Related Modules

- **M9.1: Explainability & Citation Tracking** - Provides citation metadata for source validation
- **M9.2: Risk Assessment in Retrieval** - Provides risk scores for escalation decisions
- **M9.4: Human-in-the-Loop for High-Stakes Decisions** - Manual review queue integration

## Regulatory References

- **Securities Exchange Act Section 10(b) & Rule 10b-5:** Fraud and insider trading prohibitions
- **Regulation FD (Fair Disclosure):** Selective disclosure prohibition
- **FINRA Rule 2210:** Communications with the public
- **Private Securities Litigation Reform Act of 1995:** Safe Harbor for forward-looking statements
- **Investment Advisers Act Section 203(a):** Investment adviser registration requirements

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-compliance-check`)
3. Make your changes with tests
4. Run test suite (`pytest tests/`)
5. Submit a pull request

**Contribution Guidelines:**
- All new MNPI patterns must include test cases
- Disclaimer templates must cite regulatory authority
- Maintain ≥98% recall on MNPI detection
- Add audit logging for all new violation types

## Support

For questions or issues:

1. **Check the augmented script** for detailed explanations of concepts
2. **Review the Decision Card** in this README for usage guidance
3. **Run configuration verification:** `python config.py`
4. **Check audit logs** for violation patterns: `/audit/logs` endpoint
5. **Open an issue** in the repository with:
   - Configuration details (`python config.py` output)
   - Sample input/output causing the issue
   - Expected vs. actual behavior

## Frequently Asked Questions

**Q: Can this module run without Anthropic API?**
A: Yes! This module is primarily a compliance filter. Anthropic integration is optional and only needed for M9.1 Citation Tracker integration. Core MNPI detection and disclaimer injection work offline.

**Q: What happens if PostgreSQL is unavailable?**
A: The module will fail-safe to BLOCK mode. Without access to `public_disclosures` database, it cannot validate if information is public, so it blocks all responses to prevent MNPI leaks.

**Q: How do I tune the MNPI detection threshold?**
A: Set `MNPI_DETECTION_THRESHOLD` in `.env` (range: 0.0-1.0). Higher values reduce false positives but increase risk of false negatives. Recommended starting point: 0.85. Monitor audit logs and adjust based on your risk tolerance.

**Q: Can I customize disclaimer templates?**
A: Yes! Edit `DisclaimerManager.DISCLAIMERS` in `src/l3_m9_financial_compliance_risk/__init__.py`. Ensure any changes comply with FINRA Rule 2210 and Safe Harbor requirements (consult legal counsel).

**Q: How long should I retain audit logs?**
A: SEC record-keeping requirements: 7 years for broker-dealers, 5 years for investment advisers. Implement automated archiving and ensure database capacity for retention period.

**Q: What if a user bypasses the filter?**
A: Implement application-level controls:
- All LLM outputs MUST pass through `/filter` endpoint
- No direct database access for end users
- Rate limiting and authentication on API endpoints
- Continuous monitoring of audit logs for anomalies

---

**Version:** 1.0.0
**Last Updated:** 2024
**Detected Service:** ANTHROPIC (from M9.1 integration)

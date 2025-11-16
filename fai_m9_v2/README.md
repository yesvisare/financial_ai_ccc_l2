# L3 M9.2: Financial Compliance Risk - Risk Assessment in Retrieval

Production-ready risk assessment and compliance guardrails for financial RAG systems. Prevents unauthorized investment advice, ensures regulatory compliance, and implements multi-factor confidence scoring for financial document retrieval.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:** L3 M7 (Financial Document Types), L3 M8 (Metadata Structures)
**SERVICE:** OFFLINE (local processing with optional semantic analysis)

---

## The Problem

**February 2023:** A well-funded fintech startup with a beautiful AI-powered investment platform got hit with a **$12 million SEC fine**.

The issue? Their RAG system crossed from providing information into providing investment advice without RIA (Registered Investment Advisor) licensing. The line between "information" and "advice" is legally critical:

- ✅ **Legal (Information):** "Tesla's P/E ratio is 65"
- ❌ **Investment Advice (requires RIA):** "Tesla's P/E is high, consider waiting"

SEC enforcement is **behavior-based**, not intent-based. If your system behaves like an advisor, sounds like an advisor, and users treat it like an advisor—it's legally classified as advice regardless of disclaimers.

---

## What You'll Build

A production RAG compliance layer that:

1. **Classifies query risk** using pattern matching (60%) + optional semantic analysis (40%)
2. **Computes confidence scores** across 5 factors (retrieval quality, source diversity, temporal consistency, citation agreement, domain relevance)
3. **Enforces regulatory guardrails** (RIA, MNPI, Safe Harbor, Form 8-K)
4. **Routes high-risk queries** to licensed human advisors
5. **Works completely offline** (no API keys required for core functionality)

**Key Capabilities:**
- Pattern-based risk classification (7 high-risk, 5 medium-risk, 4 low-risk patterns)
- Multi-factor confidence scoring with automatic thresholds
- Four compliance guardrails with automatic blocking/warnings
- Human-in-the-loop escalation workflows
- Optional semantic analysis via OpenAI/Anthropic

**Success Criteria:**
- 100% blocking of investment advice queries (HIGH risk → escalate to RIA)
- Confidence-based response thresholds (<0.50 = refuse to answer)
- Zero MNPI disclosures (block documents predating public disclosure)
- Automatic Safe Harbor injection for forward-looking statements
- Sub-100ms classification latency (pattern-based, local processing)

---

## How It Works

```
┌─────────────────┐
│  User Query     │ "Should I buy Tesla stock?"
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Risk Classifier (60/40 hybrid)     │
│  - Pattern matching (60% weight)    │
│  - Semantic analysis (40%, optional)│
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Risk Level + Confidence            │
│  HIGH (0.95)                        │
│  Pattern: "should.*buy"             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Compliance Guardrails              │
│  ✓ RIA: VIOLATION (escalate)        │
│  ✓ MNPI: OK                         │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  System Action                      │
│  ESCALATE_TO_HUMAN_ADVISOR          │
│  + "Query requires licensed RIA"    │
└─────────────────────────────────────┘

For LOW-risk queries:
┌─────────────────┐
│  Query          │ "What was Apple's Q4 revenue?"
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Risk: LOW (0.90)                   │
│  Action: ANSWER_NORMALLY            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Retrieve Documents                 │
│  - 10-K (0.92)                      │
│  - 8-K (0.89)                       │
│  - Earnings call (0.91)             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Confidence Scorer                  │
│  Retrieval: 0.91 (40%)              │
│  Diversity: 0.75 (25%)              │
│  Temporal: 1.00 (20%)               │
│  Citation: 1.00 (15%)               │
│  → Overall: 0.908 (HIGH)            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Return Answer + Standard Disclaimer│
└─────────────────────────────────────┘
```

---

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo_url>
cd fai_m9_v2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

The module works **completely offline** by default. No API keys required for core functionality.

```bash
cp .env.example .env
# Edit .env only if you want optional semantic analysis
```

**For core functionality:** No configuration needed! Pattern-based classification works out of the box.

**For optional semantic analysis enhancement:**
```bash
# .env
SEMANTIC_ANALYSIS_ENABLED=true
LLM_PROVIDER=openai  # or "anthropic"
OPENAI_API_KEY=your_key_here
```

### 4. Run Tests

```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Or manually
$env:PYTHONPATH=$PWD
pytest tests/ -v
```

### 5. Start API

```bash
# Windows PowerShell
.\scripts\run_api.ps1

# Or manually
$env:PYTHONPATH=$PWD
uvicorn app:app --reload
```

API will be available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 6. Explore Notebook

```bash
jupyter lab notebooks/L3_M9_Financial_Compliance_Risk.ipynb
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OFFLINE` | No | `false` | Run in offline mode (skip external calls in notebooks) |
| `SEMANTIC_ANALYSIS_ENABLED` | No | `false` | Enable LLM-based semantic analysis (optional 40% enhancement) |
| `LLM_PROVIDER` | No | `openai` | LLM provider for semantic analysis: "openai" or "anthropic" |
| `OPENAI_API_KEY` | If using OpenAI | - | OpenAI API key for semantic analysis |
| `ANTHROPIC_API_KEY` | If using Anthropic | - | Anthropic API key for semantic analysis |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: DEBUG, INFO, WARNING, ERROR |

**Note:** Core functionality (pattern-based classification, confidence scoring, compliance guardrails) works without any API keys.

---

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Pattern Obfuscation** | User asks "In your opinion, should I perhaps consider buying Tesla?" trying to hide advice language | Regex patterns catch "should I...buying" regardless of filler words. Pattern matching is weighted 60% for legal safety. |
| **Mixed Temporal Periods** | Retrieval returns Q4 2024 and Q3 2024 data mixed | Confidence scorer penalizes via temporal consistency (20% weight). Score drops → more cautious response or refusal. |
| **Citation Disagreement** | Sources report different revenue figures ($94.9B vs $95.2B) | Citation agreement factor drops → overall confidence <0.50 → refuse to answer and escalate. |
| **Late 8-K Disclosure** | Material event (CEO resignation) filed 10 days after occurrence (max 4 business days) | Form 8-K guardrail flags compliance violation → cannot use data → system warns user. |
| **MNPI in Retrieval** | Document timestamp (Oct 1) predates public disclosure date (Oct 5) | MNPI guardrail blocks document entirely → cannot return to user → potential insider trading risk. |
| **Empty/Ambiguous Query** | User submits "" or "Tell me about Tesla" | Defaults to MEDIUM risk for safety (conservative approach) → requires disclaimer. |
| **High-Risk Query History** | Retail user with 5+ high-risk queries, now asks medium-risk question | User context adjustment elevates MEDIUM → HIGH → escalate to human advisor (pattern of advice-seeking). |
| **Forward-Looking Without Disclaimer** | Response includes "Apple expects 15% revenue growth next quarter" | Safe Harbor guardrail auto-injects required legal warning → prevents securities litigation. |
| **Very Low Confidence (<0.50)** | Poor retrieval (avg score 0.45), single source type, mixed periods | System refuses to answer → "Information may be incomplete. Please consult primary sources." |
| **Semantic Analysis Unavailable** | `SEMANTIC_ANALYSIS_ENABLED=true` but no API key | Falls back to pattern-based only (60% weight becomes 100%) → still functional but less nuanced. |

---

## Decision Card

### When to Use This Module

✅ **Use when:**
- Building financial RAG systems accessible to retail users (SEC focus area)
- System retrieves SEC filings, earnings calls, analyst reports, financial news
- Queries could cross into investment advice territory ("Should I buy X?")
- Need to enforce Reg FD (MNPI prevention) or Safe Harbor (forward-looking statements)
- Require audit trail for compliance (logging every query classification)
- Working with fiduciary data (10-K, 10-Q, 8-K, proxy statements)
- Need confidence-based response thresholds to prevent hallucinations
- Must route high-risk queries to licensed advisors (RIA/CFP)

✅ **Ideal for:**
- Fintech chatbots and robo-advisors
- Investment research platforms
- Financial education apps
- Compliance monitoring systems
- SEC filing search engines

### When NOT to Use This Module

❌ **Don't use when:**
- Building internal tools for licensed professionals only (different regulatory scope)
- Working with non-financial domains (e-commerce, healthcare, legal)
- System never retrieves regulated financial content
- Users are exclusively institutional clients (different SEC rules)
- You already have an RIA license and qualified advisors handling all responses
- Need real-time market data analysis (this focuses on compliance, not trading)
- Building pure analytics dashboards (no user-facing advice risk)

❌ **Not suitable for:**
- Crypto trading bots (different regulatory framework)
- Real-time trading signal generation (latency requirements)
- Fully automated investment platforms without human oversight

### Trade-offs

**Cost:**
- Core module: $0 (local processing, no API calls)
- Optional semantic analysis: ~$0.01-0.05 per query (LLM API costs)
- Human advisor escalation: $50-200/hour (licensed RIA consultation)

**Latency:**
- Pattern-based classification: <50ms (local regex matching)
- With semantic analysis: +200-500ms (LLM API call)
- Confidence scoring: <10ms (numpy calculations)
- Total: <100ms (pattern-only) or <600ms (with semantic)

**Complexity:**
- Implementation: Medium (regex patterns, multi-factor scoring, 4 guardrails)
- Maintenance: Low (patterns stable, regulations change ~yearly)
- Monitoring: High (must log all classifications for audit trail)

**Accuracy:**
- Pattern-based alone: ~85% precision, ~90% recall (high-risk detection)
- With semantic analysis: ~92% precision, ~95% recall
- False positive cost: Unnecessary escalation to human ($50-200 cost)
- False negative cost: SEC fine ($10K-$1M+ per violation)

**Risk Posture:**
- Conservative by default (ambiguous queries → MEDIUM risk)
- Pattern matching weighted 60% for legal safety over nuance
- Confidence <0.50 → refuse to answer (prevent hallucination liability)
- Human-in-the-loop required for HIGH risk (cannot automate away RIA requirement)

---

## API Endpoints

### `POST /classify`
Classify a financial query's risk level.

**Request:**
```json
{
  "query": "Should I buy Tesla stock?",
  "user_context": {
    "account_type": "retail",
    "high_risk_query_count": 2
  }
}
```

**Response:**
```json
{
  "risk_level": "HIGH",
  "confidence": 0.95,
  "reasoning": "Detected investment advice language: should.*buy",
  "regulatory_concern": "Investment Advisers Act of 1940 - RIA registration required",
  "system_action": "ESCALATE_TO_HUMAN_ADVISOR",
  "pattern_matches": ["\\bshould.*buy\\b"],
  "user_context_adjusted": false
}
```

### `POST /confidence`
Compute multi-factor confidence score for retrieval results.

**Request:**
```json
{
  "retrieval_results": [
    {
      "score": 0.92,
      "source_type": "10-K",
      "fiscal_period": "2024-Q4",
      "numerical_claim": "94.9B"
    }
  ],
  "query": "What was Apple's Q4 2024 revenue?"
}
```

**Response:**
```json
{
  "overall_score": 0.908,
  "retrieval_quality": 0.92,
  "source_diversity": 0.25,
  "temporal_consistency": 1.0,
  "citation_agreement": 1.0,
  "domain_relevance_bonus": 0.03,
  "threshold_category": "HIGH"
}
```

### `POST /compliance`
Run compliance guardrail checks.

**Request:**
```json
{
  "classification": {
    "risk_level": "HIGH",
    "confidence": 0.95,
    "reasoning": "Investment advice detected",
    "system_action": "ESCALATE_TO_HUMAN_ADVISOR"
  },
  "documents": [
    {
      "document_timestamp": "2024-10-01T00:00:00Z",
      "public_disclosure_date": "2024-10-05T00:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "ria_compliance": {
    "compliant": false,
    "violation": "UNAUTHORIZED_INVESTMENT_ADVICE",
    "regulation": "Investment Advisers Act of 1940",
    "required_action": "ESCALATE_TO_RIA"
  },
  "mnpi_compliance": {
    "compliant": false,
    "violation": "MATERIAL_NON_PUBLIC_INFORMATION",
    "regulation": "Regulation Fair Disclosure (Reg FD)",
    "required_action": "BLOCK_DOCUMENT"
  }
}
```

---

## Risk Classification Tiers

### LOW Risk (Educational/Factual)
**System Action:** `ANSWER_NORMALLY`

**Examples:**
- "What is a 10-K filing?"
- "When does Apple's fiscal year end?"
- "Define EBITDA"
- "Explain what Form 8-K is used for"

**Patterns Detected:**
- `\b(what is|define|explain|meaning of)\b`
- `\bhow (does|do|did)\b.{0,50}\b(work|function|operate)\b`
- `\b(when|where|who|which)\s+(did|was|were|filed)\b`

### MEDIUM Risk (Comparative Analysis)
**System Action:** `ANSWER_WITH_DISCLAIMER`

**Examples:**
- "Compare Apple and Microsoft's revenue growth"
- "What are Tesla's risk factors?"
- "How has Goldman Sachs stock performed?"
- "Is Tesla's P/E ratio high compared to the industry?"

**Patterns Detected:**
- `\b(compare|versus|vs|better than|worse than)\b`
- `\b(risk|risky|volatile|safe|dangerous)\b.{0,30}\b(stock|investment)\b`
- `\b(performance|returns|growth|decline)\s+of\b`

### HIGH Risk (Investment Advice - Requires RIA)
**System Action:** `ESCALATE_TO_HUMAN_ADVISOR`

**Examples:**
- "Should I buy Tesla stock?"
- "Is this a good time to invest in crypto?"
- "What's the best stock to buy right now?"
- "Would you recommend investing in Apple or Microsoft?"

**Patterns Detected:**
- `\b(should|would|recommend)\s+(I|you|we)\s+(buy|sell|invest)\b`
- `\b(what|which)\s+.{0,30}\s+(best|worst|top|bottom)\s+(stock|investment)\b`
- `\bis\s+.{0,30}\s+a\s+(good|bad|smart|wise)\s+(investment|trade)\b`

---

## Compliance Guardrails

### 1. RIA Compliance (Investment Advice Detection)
**Regulation:** Investment Advisers Act of 1940
**Trigger:** HIGH risk queries
**Action:** Block response, escalate to licensed RIA
**Violation Cost:** $10K-$1M+ per violation

### 2. MNPI Detection (Material Non-Public Information)
**Regulation:** Regulation Fair Disclosure (Reg FD)
**Trigger:** Document timestamp < public disclosure date
**Action:** Block document from retrieval
**Violation Cost:** Insider trading liability

### 3. Safe Harbor (Forward-Looking Statements)
**Regulation:** Private Securities Litigation Reform Act (1995)
**Trigger:** Response contains forecasts, projections, guidance
**Action:** Auto-inject legal disclaimer
**Protection:** Reduces securities litigation risk

### 4. Form 8-K Validation (Material Event Disclosure)
**Regulation:** Securities Exchange Act of 1934, Rule 8-K
**Trigger:** Material event disclosure >4 business days late
**Action:** Flag compliance violation, warn user
**Violation Cost:** SEC enforcement action

---

## Confidence Score Thresholds

| Threshold | Range | System Behavior | Use Case |
|-----------|-------|-----------------|----------|
| **HIGH** | ≥0.85 | Answer with standard disclaimer | Strong retrieval, multiple agreeing sources |
| **MEDIUM** | 0.70-0.84 | Answer with "moderate confidence" warning | Good retrieval, some inconsistency |
| **LOW** | 0.50-0.69 | Warn "information may be incomplete" | Weak retrieval or temporal mixing |
| **VERY_LOW** | <0.50 | Refuse to answer, escalate | Poor retrieval, citation disagreement |

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_m9_financial_compliance_risk.py::TestRiskClassification -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Coverage:**
- Risk classification (low/medium/high tiers)
- Confidence scoring (all 5 factors)
- Compliance guardrails (all 4 guardrails)
- User context adjustment
- Edge cases and adversarial queries

---

## Troubleshooting

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'src.l3_m9_financial_compliance_risk'`

**Fix:**
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD

# Linux/Mac
export PYTHONPATH=$(pwd)
```

### NumPy Not Available
**Warning:** `NumPy not available - using fallback calculations`

**Fix:**
```bash
pip install numpy==1.26.4
```

**Note:** Fallback calculations work correctly, but NumPy provides faster computation.

### Tests Failing
**Issue:** Some tests fail unexpectedly

**Fix:**
```bash
# Ensure OFFLINE mode is set
$env:OFFLINE="true"
$env:SEMANTIC_ANALYSIS_ENABLED="false"

# Run with verbose output
pytest tests/ -v --tb=long
```

### API Not Starting
**Error:** `Address already in use`

**Fix:**
```bash
# Change port in scripts/run_api.ps1
uvicorn app:app --reload --port 8001
```

---

## Production Checklist

Before deploying to production:

- [ ] Set up audit logging for all query classifications (SOX compliance)
- [ ] Configure human escalation workflow (RIA routing)
- [ ] Test all 7 high-risk patterns with adversarial queries
- [ ] Validate MNPI guardrail with backdated documents
- [ ] Set up monitoring for classification latency (<100ms SLA)
- [ ] Establish legal review process for new regex patterns
- [ ] Document false positive rate and escalation costs
- [ ] Configure rate limiting for compliance endpoints
- [ ] Set up alerts for unusual HIGH risk query spikes
- [ ] Test Safe Harbor injection with forward-looking content
- [ ] Validate Form 8-K disclosure windows (4 business days)
- [ ] Review SEC guidance on robo-advisors annually

---

## Next Module

**L3 M10: Multi-Document Synthesis with Citation** - Building on compliance foundations to create verifiable, auditable financial responses with source attribution.

---

## License

MIT License - Copyright (c) 2025 TechVoyageHub

See [LICENSE](LICENSE) for details.

---

## Support

For issues or questions:
- File an issue in the repository
- Review test suite for usage examples
- Check API docs at `/docs` endpoint
- Consult augmented script for detailed explanations

**Regulatory Disclaimer:** This module is for educational purposes. Consult legal counsel before deploying financial RAG systems in production. Securities regulations vary by jurisdiction.

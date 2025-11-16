# L3 M9.4: Human-in-the-Loop for High-Stakes Decisions

**Track:** Finance AI (Domain-Specific)
**Module:** M9 - Financial Compliance & Risk
**Video:** M9.4 - Human-in-the-Loop for High-Stakes Decisions
**Duration:** 40-45 minutes
**Level:** L2 SkillElevate

Production-ready implementation of a risk-based human review workflow for financial AI systems, ensuring high-stakes decisions receive appropriate expert oversight before execution while maintaining regulatory compliance.

## 📋 Overview

This module implements a **collaborative decision-making model** where AI processes massive datasets and identifies patterns while humans provide contextual judgment and accountability. The system prevents catastrophic financial errors while maintaining analytical speed through risk-proportional review mechanisms.

**Key capabilities:**

- **Risk-based query classification** with automatic routing to domain experts
- **Tamper-proof audit trails** with cryptographic hash chains for SOX compliance
- **Time-aware workflows** with SLA tracking and automatic escalation
- **Role-based access control** with approval hierarchies
- **Fail-safe defaults** that prevent regulatory violations
- **Real-time notifications** via email and Slack for urgent decisions

## 🎯 Learning Outcomes

**After completing this module, you will:**

1. **Implement risk-based query classification** for routing financial decisions to appropriate reviewers
2. **Build approval workflows** with role-based access control and escalation hierarchies
3. **Create audit-ready decision logs** meeting SOX Section 404 regulatory requirements
4. **Handle time-sensitive approvals** with SLA tracking and automatic escalation mechanisms
5. **Design escalation hierarchies** for urgent decisions requiring higher authority

## 🏗️ Architecture

### System Components

The human-in-the-loop workflow orchestrates multiple components:

**Workflow Orchestration:**
- **FastAPI** - HTTP endpoints and async operations for query submission and review
- **Celery** - Background task queues for escalation timers and scheduled checks

**Queue Management:**
- **Redis sorted sets** - Priority-ordered review queues based on SLA urgency

**Data Persistence:**
- **PostgreSQL** - JSONB fields for flexible audit data with SHA-256 hash chains for tamper detection

**Notifications:**
- **SendGrid** - Email alerts for review assignments and SLA warnings
- **Slack webhooks** - Real-time team updates for critical decisions
- **React dashboard** - Analyst UI for pending reviews and approval workflows

**Monitoring:**
- **Prometheus** - Metrics collection for SLA compliance and throughput
- **Grafana** - Dashboards visualizing SLA adherence and review bottlenecks

### How It Works

```
┌─────────────────┐
│  Query Arrives  │
│ (User/PM input) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 1: Risk Classification    │
│  - Transaction amount check     │
│  - Action type detection        │
│  - MNPI flag validation         │
│  - Model confidence assessment  │
│  → Result: CRITICAL/HIGH/MED/LOW│
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 2: Expertise Routing      │
│  - CFO (CRITICAL, $10M+)        │
│  - Senior Analyst (HIGH)        │
│  - Analyst (MEDIUM)             │
│  - Junior Analyst (LOW)         │
│  → Assign SLA: 2h-24h           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 3: Audit Trail Creation   │
│  - Unique audit_id generation   │
│  - Timestamp + user metadata    │
│  - Query + RAG response storage │
│  - SHA-256 hash chain linkage   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 4: Human Review           │
│  - Analyst examines RAG output  │
│  - Checks against regulations   │
│  - Validates financial logic    │
│  - Decision: APPROVE/REJECT/MOD │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 5: Decision Execution     │
│  - Update audit trail with      │
│    reviewer_id + decision       │
│  - Recalculate hash for chain   │
│  - Send notification to user    │
│  - Archive for 7-year retention │
└─────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- (Optional) PostgreSQL for persistent audit trail storage
- (Optional) Redis for queue management
- (Optional) OpenAI API access for RAG response generation
- Windows PowerShell (for scripts) or bash equivalent

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fai_m9_v4
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
# Core workflow operates without external services
```

4. Run the API:
```bash
# Windows PowerShell
.\scripts\run_api.ps1

# Or directly
uvicorn app:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📊 Usage

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "online",
  "service": "L3 M9.4: Human-in-the-Loop for High-Stakes Decisions",
  "configuration": {
    "core_workflow": "✅ Ready",
    "openai_integration": "⚠️ Disabled",
    "database": "⚠️ Not configured"
  }
}
```

#### Submit Query for Review
```bash
curl -X POST http://localhost:8000/submit-query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "pm_001",
    "query_text": "Approve $8M increase in Tesla position based on Q3 earnings",
    "transaction_amount": 8000000,
    "action_type": "investment_decision"
  }'
```

**Response:**
```json
{
  "audit_id": "a1b2c3d4e5f6",
  "risk_level": "HIGH",
  "risk_reason": "Transaction amount $8,000,000 exceeds $1M threshold",
  "routing": {
    "reviewer_role": "Senior Analyst",
    "sla_hours": 4,
    "requires_second_opinion": false
  },
  "status": "pending",
  "message": "Query routed to Senior Analyst with 4h SLA"
}
```

#### Submit Human Review
```bash
curl -X POST http://localhost:8000/submit-review \
  -H "Content-Type: application/json" \
  -d '{
    "audit_id": "a1b2c3d4e5f6",
    "reviewer_id": "analyst_senior_42",
    "reviewer_role": "Senior Analyst",
    "decision_outcome": "rejected",
    "supporting_evidence": "Q3 earnings beat driven by $200M one-time tax benefit..."
  }'
```

#### Get Pending Reviews
```bash
curl http://localhost:8000/pending-reviews?reviewer_role=Senior%20Analyst
```

#### Retrieve Audit Trail
```bash
curl http://localhost:8000/audit-trail
```

### Python Package

```python
from src.l3_m9_financial_compliance_risk import (
    classify_risk,
    route_to_reviewer,
    HumanInTheLoopWorkflow
)

# Initialize workflow
workflow = HumanInTheLoopWorkflow()

# Process a query
result = workflow.process_query(
    user_id="pm_001",
    query_text="Approve $8M Tesla position increase",
    transaction_amount=8_000_000,
    action_type="investment_decision"
)

print(f"Audit ID: {result['audit_id']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Routed to: {result['routing']['reviewer_role']}")
```

### Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M9_Financial_Compliance_Risk.ipynb
```

## 🧪 Testing

Run all tests:
```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Or directly
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_ENABLED` | No | `false` | Enable OpenAI for RAG response generation |
| `OPENAI_API_KEY` | If enabled | - | Your OpenAI API key |
| `DATABASE_URL` | No | `postgresql://localhost/financial_ai` | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |
| `SENDGRID_ENABLED` | No | `false` | Enable email notifications |
| `SLACK_ENABLED` | No | `false` | Enable Slack notifications |
| `DEFAULT_SLA_HOURS` | No | `24` | Default SLA for reviews (hours) |
| `SLA_WARNING_THRESHOLD` | No | `0.8` | Warn when SLA reaches this % |
| `ENABLE_AUTO_ESCALATION` | No | `true` | Auto-escalate on SLA breach |
| `AUDIT_RETENTION_DAYS` | No | `2555` | 7 years for SOX compliance |

### Offline Mode

The core workflow operates fully offline without external services:

✅ **Available offline:**
- Risk classification (rule-based)
- Routing logic
- Audit trail creation with hash chains
- SLA compliance tracking
- Approval workflow validation

⚠️ **Requires external services:**
- RAG response generation (needs OpenAI or alternative)
- Email/Slack notifications
- Persistent database storage (defaults to in-memory)
- Queue-based task scheduling

## 📚 Concepts Covered

### 1. **Risk-Proportional Review**
Matches scrutiny depth to financial risk using transaction size, action type, MNPI presence, and model confidence thresholds.

**Implementation:** `classify_risk()` function evaluates multiple factors:
- Transaction amount thresholds ($1M, $10M)
- Action types (investment_decision, portfolio_rebalancing, credit_approval)
- MNPI flags (material non-public information)
- Model confidence scores (<70% triggers review)

### 2. **Expertise-Matched Routing**
Routes queries to domain specialists based on risk level and financial domain expertise.

**Routing hierarchy:**
- **CFO:** CRITICAL risk (MNPI, $10M+) - 2h SLA, committee approval
- **Senior Analyst:** HIGH risk ($1M+) - 4h SLA, second opinion if $10M+
- **Analyst:** MEDIUM risk ($100K-1M) - 8h SLA
- **Junior Analyst:** LOW risk (informational) - 24h SLA

### 3. **Time-Aware Workflows**
Balances thoroughness with market timing through SLA tracking and automatic escalation.

**SLA tiers:**
- **Urgent (2h):** Market-moving events, MNPI disclosures
- **Standard (4h):** Portfolio rebalancing, investment decisions
- **Extended (24h):** Strategic analysis, informational queries

### 4. **Audit-Ready by Default**
Tamper-proof logging with cryptographic hash chains for SOX Section 404 compliance.

**Hash chain mechanism:**
```
Entry 1: hash(data_1) → hash_1
Entry 2: hash(data_2 + hash_1) → hash_2
Entry 3: hash(data_3 + hash_2) → hash_3
```
Any modification breaks the chain, ensuring tamper detection.

### 5. **Fail-Safe Defaults**
System defaults to safety when uncertain, preventing regulatory violations.

**Fail-safe behaviors:**
- Unknown risk → Escalate to CRITICAL
- Missing reviewer → Route to highest authority
- SLA breach → Auto-escalate to next level
- System error → Block execution pending manual review

### 6. **Role-Based Access Control (RBAC)**
Hierarchical approval chains ensure only authorized personnel approve decisions.

**Role hierarchy:**
```
CFO (Level 5)
  ↓
Head of Trading (Level 4)
  ↓
Senior Analyst (Level 3)
  ↓
Analyst (Level 2)
  ↓
Junior Analyst (Level 1)
```

### 7. **Escalation Hierarchies**
Structured escalation paths for urgent or complex decisions requiring higher authority.

**Escalation triggers:**
- SLA breach (time-based)
- Uncertainty flagged by reviewer (complexity-based)
- Conflicting second opinions (dispute-based)
- Regulatory concerns (compliance-based)

### 8. **Tamper-Proof Audit Trails**
SHA-256 cryptographic hashing with chain linkage ensures audit integrity for 7-year retention.

**Audit entry structure:**
- `audit_id`: Unique identifier
- `timestamp`: ISO 8601 format (UTC)
- `user_id`, `query_text`, `rag_response`: Input data
- `reviewer_id`, `decision_outcome`, `supporting_evidence`: Review data
- `previous_hash`, `current_hash`: Hash chain

### 9. **SLA Compliance Tracking**
Real-time monitoring of review timelines with warnings and automatic escalation.

**Tracking metrics:**
- Elapsed time since submission
- Remaining time until SLA breach
- Warning threshold (default: 80% of SLA)
- Breach severity (hours overdue)

### 10. **Regulatory Compliance Integration**
Built-in support for SOX, FINRA, SEC, and ECOA regulatory requirements.

**Compliance features:**
- 7-year audit retention (SOX Section 404)
- Tamper-proof logging for SEC audits
- Fair lending checks (ECOA)
- MNPI handling procedures (insider trading prevention)

### 11. **Second Opinion Mechanisms**
Mandatory second reviews for high-value or high-risk decisions.

**Second opinion triggers:**
- Transaction amount ≥ $10M
- Conflicting regulatory interpretations
- First reviewer flags uncertainty
- MNPI disclosure scenarios

## ⚠️ Common Failures & Fixes

| Failure | Symptoms | Fix |
|---------|----------|-----|
| **Missing accounting footnotes** | RAG recommends trade based on headline earnings, ignoring one-time gains/losses in footnotes | Enhance RAG retrieval to include full 10-K/10-Q footnotes; train reviewers to check "Non-GAAP Reconciliation" sections |
| **Domain expertise mismatch** | Credit analyst reviewing equity options trade lacks derivatives knowledge | Implement skill-based routing in addition to role-based; maintain reviewer skill matrix in database |
| **Slow approval bottlenecks** | Senior analyst queue has 47 pending reviews, missing market windows | Add queue depth monitoring; auto-escalate to Head of Trading when queue >20; implement overflow routing to backup reviewers |
| **Auto-approve on system failure** | Database connection timeout defaults to approving $12M trade (regulatory violation) | Implement fail-safe defaults: on error, block execution and send Slack alert; require manual CFO override for recovery |
| **Risk classifier downtime** | Classification service crashes, all queries routed as LOW risk, $50M trade goes unreviewed | Add health check endpoint; fallback to conservative CRITICAL classification on service failure; implement circuit breaker pattern |

## 🎓 Decision Card

### Use Human-in-the-Loop When:

✅ **Financial decisions exceed $1M impact threshold**
High-stakes decisions warrant expert oversight to prevent catastrophic errors.

✅ **Regulatory liability exists (SEC, FINRA constraints)**
Human accountability required for compliance and audit trails.

✅ **Model confidence falls below 70%**
Low confidence signals need for expert judgment and validation.

✅ **MNPI or fair lending risks present**
Legal and ethical requirements mandate human review for sensitive decisions.

### Don't Use Human-in-the-Loop When:

❌ **Informational queries require sub-second response times**
Example: "What is Tesla's current stock price?"
Human review adds latency incompatible with real-time needs.

❌ **Portfolio contains only low-risk positions (<$100K)**
Review overhead exceeds potential risk; automated checks sufficient.

❌ **Human reviewers unavailable (after-hours trading)**
Market operates 24/7 but analysts work business hours; requires fallback automation or regional handoffs.

### Trade-offs

✅ **Pros:**
- **Error prevention:** Catches AI hallucinations, stale data, and regulatory violations before execution
- **Accountability:** Clear audit trail assigns responsibility for decisions
- **Regulatory compliance:** Meets SOX, FINRA, and SEC requirements for human oversight
- **Contextual judgment:** Humans detect nuances (sarcasm, market regime shifts) AI misses

❌ **Cons:**
- **Latency:** Review adds 103 minutes average (Tesla case study), potentially missing market windows
- **Staffing costs:** Senior analysts cost $150-300/hour; scales poorly with query volume
- **Bottlenecks:** Queue backlogs delay time-sensitive decisions during market volatility
- **False confidence:** Over-reliance on AI can atrophy human analytical skills

### Cost Analysis

**Per-query cost:**
- Analyst time: 103 minutes average @ $150/hour = ~$257
- Infrastructure: $0.05 (API, database, queue)
- Total: ~$260 per reviewed query

**Break-even:**
- Prevents one $500K error per 1,923 reviews
- Prevents one $2M error per 7,692 reviews

**ROI (Tesla case study):**
- Cost: $257 analyst time
- Prevented loss: $500K-2M (concentration limit breach)
- ROI: 194,500% - 778,000%

## 🔗 Related Modules

### Prerequisites:

**Required foundation:**
- **Generic CCC M1-M4:** RAG MVP foundations (vector search, retrieval, context assembly)
- **Finance AI M9.1:** Explainability & Citation (understanding AI reasoning transparency)
- **Finance AI M9.2:** Risk Assessment Integration (identifying high-risk scenarios)
- **Finance AI M9.3:** Regulatory Output Constraints (SOX, FINRA compliance basics)

**Recommended background:**
- Familiarity with financial regulations (SOX Section 404, FINRA Rule 2111)
- Understanding of investment decision workflows

### Next Steps:

- **Finance AI M9.5:** Real-time Monitoring & Alerts (detecting anomalies in production)
- **Finance AI M10:** Advanced Compliance Automation (multi-jurisdictional regulations)

## 📖 Additional Resources

- **[Augmented Script](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_FinanceAI_M9_4_HumanInTheLoop_HighStakes.md)** - Complete module content with examples
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Web framework reference
- **[SOX Section 404 Overview](https://www.soxlaw.com/s404.htm)** - Compliance requirements
- **[FINRA Rule 2111](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111)** - Suitability obligations

## 🤝 Real-World Scenario

### Tesla Position Increase ($8M)

**Stage 1 - Query Submission:**
```
Portfolio Manager: "Our Tesla position is currently $12M (3% of AUM).
Q3 earnings beat expectations. Increase position by $8M to $20M (5% concentration)."
```

**Stage 2 - Risk Classification:**
```
System detects:
- Transaction amount: $8M (HIGH risk, >$1M threshold)
- Action type: investment_decision (mandatory review)
- Risk level: HIGH
→ Route to Senior Analyst with 4-hour SLA
```

**Stage 3 - Human Review (Senior Analyst):**
```
Analyst examines RAG output and discovers:
✓ Q3 earnings: $0.66 EPS vs $0.55 estimate (beat)
❌ BUT: $200M one-time tax benefit inflated results
❌ Excluding one-time gain: $0.51 EPS (MISSED estimate by $0.04)
❌ Proposed $20M position = 5% concentration (breaches 4.5% limit)

Decision: REJECT original request
Counterproposal: $4M increase to $16M (4% concentration)
```

**Stage 4 - Audit Trail:**
```json
{
  "audit_id": "8a7b6c5d",
  "timestamp": "2024-10-15T14:23:00Z",
  "user_id": "pm_001",
  "query_text": "Increase Tesla position $12M → $20M",
  "rag_response": {"recommendation": "Approve", "confidence": 0.85},
  "risk_classification": "HIGH",
  "reviewer_id": "analyst_senior_42",
  "decision_outcome": "modified",
  "supporting_evidence": "One-time tax benefit inflated Q3 earnings...",
  "current_hash": "3f7a9b2c..."
}
```

**Outcome:**
- **Cost:** 103 minutes analyst time (~$257)
- **Prevented loss:** $500K-2M (concentration breach + earnings quality issue)
- **ROI:** 194,500% - 778,000%

## 📝 License

MIT License - see LICENSE file for details

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/yesvisare/financial_ai_ccc_l2/issues)
- **Documentation:** See notebooks/ for interactive examples
- **Questions:** Refer to augmented script for detailed explanations

---

**Part of TechVoyageHub Finance AI Track - L3 SkillElevate**

*Building production-ready financial AI systems with human oversight, regulatory compliance, and fail-safe defaults.*

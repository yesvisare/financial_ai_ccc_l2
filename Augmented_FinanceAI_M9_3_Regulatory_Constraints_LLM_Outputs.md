# Module 9: Financial Compliance & Risk
## Video 9.3: Regulatory Constraints in LLM Outputs (MNPI, Disclaimers, Safe Harbor) (Enhanced with TVH Framework v2.0)

**Duration:** 45-50 minutes
**Track:** Finance AI (Domain-Specific)
**Level:** L2+ SkillElevate
**Audience:** L2+ learners who completed Generic CCC M1-M4 (RAG MVP) and Finance AI M9.1, M9.2
**Prerequisites:** 
- Generic CCC M1-M4 (RAG architecture, optimization, deployment, evaluation)
- Finance AI M9.1 (Explainability & Citation Tracking)
- Finance AI M9.2 (Risk Assessment in Retrieval)
- Understanding of financial regulatory frameworks (from M9.1/M9.2)

---

## SECTION 1: INTRODUCTION & HOOK (2-3 minutes, 400-500 words)

**[0:00-0:30] Hook - The SEC Investigation Problem**

[SLIDE: Title - "Regulatory Constraints in LLM Outputs: MNPI, Disclaimers, and Safe Harbor"]

**NARRATION:**
"You've built an intelligent financial RAG system with explainability and risk assessment. Your citations are accurate, your risk classifier catches high-stakes queries, and your CFO is impressed with the audit trail.

But then your compliance officer walks into your office with a printout of a RAG response and says: 'This is a Regulation Fair Disclosure violation. If this information leaked to one investor before our public earnings call, we could face SEC investigation, millions in fines, and executive liability.'

You look at the response. It says: 'Q4 earnings are expected to exceed $3 billion based on internal projections.' The information is accurate. The citation is correct. But it came from an internal financial planning document that hasn't been disclosed publicly yet. Your RAG system just helped someone commit potential insider trading.

Here's the brutal reality: **Material Non-Public Information (MNPI) disclosure is a federal crime under securities law**. One leaked earnings number, one merger hint, one product launch detail—and your company faces SEC enforcement action, shareholder lawsuits, and executive criminal charges.

The problem gets worse. Your RAG system hallucinates a forward-looking statement: 'Revenue will grow 20% next quarter.' A retail investor reads it, makes a trade, loses money when the prediction doesn't pan out. Now you're facing 'investment advice without registration' claims and FINRA Rule 2210 violations.

The driving question: **How do you build regulatory guardrails into LLM outputs to prevent MNPI disclosure, ensure proper disclaimers, and comply with Safe Harbor requirements—without breaking the user experience?**

Today, we're building a **Regulatory Output Filter** that detects prohibited content, adds required disclaimers, and implements Safe Harbor protections..."

**INSTRUCTOR GUIDANCE:**
- Open with urgency—SEC investigations are career-ending
- Make MNPI feel real: executives go to jail for this
- Emphasize that accuracy isn't enough—compliance matters
- Reference their M9.1/M9.2 work to show progression

---

**[0:30-1:30] What We're Building Today**

[SLIDE: Regulatory Output Filter Architecture showing:
- LLM output flowing through multiple compliance layers
- MNPI detection engine checking against internal database
- Forward-looking statement detector
- Disclaimer injection system
- Safe Harbor template library
- Audit logging capturing all violations]

**NARRATION:**
"Here's what we're building today:

A **Regulatory Output Filter** that sits between your LLM and the user, analyzing every generated response for compliance violations before it reaches the screen.

This system will:
1. **Detect Material Non-Public Information (MNPI)** by cross-referencing against internal sources and checking materiality indicators
2. **Identify forward-looking statements** and inject Safe Harbor disclaimers automatically
3. **Flag investment advice language** and either block it or add 'Not Investment Advice' disclaimers
4. **Implement information barriers** to prevent selective disclosure (Chinese Walls)
5. **Create audit trails** showing what was filtered and why—critical for SEC investigations

By the end of this video, you'll have a production-ready compliance filter that catches 98%+ of MNPI violations, adds required disclaimers systematically, and protects your company from Regulation FD enforcement action.

This isn't optional protection—it's the difference between a compliant financial AI system and an SEC liability."

**INSTRUCTOR GUIDANCE:**
- Show visual architecture diagram
- Emphasize 98% detection rate (false negatives are catastrophic)
- Connect to M9.1's audit trail work
- Make compliance feel like engineering challenge, not legal abstraction

---

**[1:30-2:30] Learning Objectives**

[SLIDE: Learning Objectives (4 bullet points)]

**NARRATION:**
"In this video, you'll learn:

1. **Detect Material Non-Public Information (MNPI)** in LLM outputs using pattern matching, source validation, and materiality thresholds (98%+ recall required)
2. **Implement systematic disclaimers** ('Not Investment Advice', Safe Harbor statements) that meet FINRA Rule 2210 and Private Securities Litigation Reform Act requirements
3. **Build information barriers (Chinese Walls)** to prevent selective disclosure and Regulation FD violations
4. **Create compliance audit trails** that survive SEC investigations and shareholder lawsuits

These aren't theoretical exercises. You're building production guardrails that protect your company from federal securities violations and multi-million dollar liability."

**INSTRUCTOR GUIDANCE:**
- Use specific regulations (Reg FD, FINRA 2210, PSLRA)
- Emphasize 98%+ recall on MNPI—false negatives destroy companies
- Connect to M9.1's citation tracking and M9.2's risk assessment
- Make objectives feel high-stakes

---

**[2:30-3:00] Context from Previous Videos**

[SLIDE: Journey So Far - M9.1, M9.2, M9.3]

**NARRATION:**
"Let me connect this to what you've already built.

**From M9.1 (Explainability):** You created citation tracking so every financial claim is backed by a source document. Now we're validating that source isn't MNPI.

**From M9.2 (Risk Assessment):** You built a risk classifier that flags high-stakes queries. Now we're adding output filtering to prevent high-risk responses from ever reaching users.

**Today (M9.3):** We're completing the compliance triad—explainable inputs, risk-assessed retrieval, and now regulated outputs. This is the final layer protecting your company from securities violations.

In M9.4, we'll implement human-in-the-loop workflows for escalating borderline cases to compliance officers. But first, you need automated guardrails that catch 98% of violations without human intervention."

**INSTRUCTOR GUIDANCE:**
- Show clear progression: inputs → retrieval → outputs
- Reference specific M9.1/M9.2 components
- Preview M9.4 to maintain continuity
- Keep under 30 seconds—concise context setting

---

## SECTION 2: CONCEPT EXPLANATION (5-7 minutes, 1,000-1,400 words)

**[3:00-5:00] Core Concepts: MNPI, Reg FD, Safe Harbor**

[SLIDE: Three-layer compliance framework showing:
- Layer 1: MNPI Detection (prevent insider trading)
- Layer 2: Disclaimer Requirements (FINRA, safe harbor)
- Layer 3: Information Barriers (Chinese Walls)
- All layers feeding into compliance audit trail]

**NARRATION:**
"Let's break down the three types of regulatory constraints on financial LLM outputs.

**1. Material Non-Public Information (MNPI) - The Insider Trading Problem**

MNPI is information that:
- **Material:** Could reasonably affect a company's stock price
- **Non-Public:** Has not been disclosed to all investors simultaneously

Think of materiality like this: *If you wouldn't want your competitor to know it before your shareholders do, it's probably material.*

**Examples of MNPI:**
- ✅ **Public:** 'Q3 earnings were $2.5 billion' (from filed 10-Q report)
- ❌ **MNPI:** 'Q4 earnings will be $3 billion' (from internal forecast, not yet disclosed)
- ✅ **Public:** 'CEO announced merger with XYZ Corp' (from press release)
- ❌ **MNPI:** 'Company is negotiating merger with XYZ Corp' (from internal email)
- ✅ **Public:** 'Stock price is $150' (from public market data)
- ❌ **MNPI:** 'New product will launch next month' (from internal roadmap)

**Why RAG Systems Create MNPI Risk:**

Your RAG system doesn't distinguish between:
- Public SEC filings vs. internal financial planning documents
- Press releases vs. board meeting minutes
- Published earnings vs. pre-announcement forecasts

Semantic search just finds the 'most relevant' information. If an internal document is more relevant than a public filing, RAG will surface it. That's a Regulation FD violation.

**Regulation Fair Disclosure (Reg FD):**

Reg FD requires companies to disclose material information to **ALL investors simultaneously**. You can't tell one investor about earnings before announcing publicly—that's selective disclosure.

**The RAG Problem:** If your system gives one user access to MNPI that other users don't have, you've violated Reg FD. Even if both users are employees, different access levels create selective disclosure risk.

**Real Consequence:** SEC fines for Reg FD violations range from $50,000 to $500,000 per violation. Executives can face personal liability and criminal charges for intentional insider trading.

---

**2. Disclaimer Requirements - The 'Not Investment Advice' Problem**

**Why Disclaimers Exist:**

Providing investment advice without registration is illegal under the Investment Advisers Act. A Registered Investment Adviser (RIA) requires:
- Federal registration (SEC or state)
- Fiduciary duty to clients
- Compliance infrastructure
- Professional liability insurance

**Your RAG system is NOT a registered investment adviser.** If it gives advice ('Buy Tesla stock', 'Apple is undervalued'), you're engaging in unauthorized investment advice.

**Required Disclaimers:**

**'Not Investment Advice' Disclaimer (FINRA Rule 2210):**
'This information is for educational purposes only. It is not investment advice. Consult a licensed financial advisor before making investment decisions.'

**When Required:**
- Any comparison of investment options ('Stock A vs. Stock B')
- Valuation analysis ('Undervalued', 'Overvalued')
- Buy/sell/hold recommendations
- Forward-looking performance predictions

**Safe Harbor Statements (Private Securities Litigation Reform Act):**

Forward-looking statements (predictions about future performance) are protected from liability IF you include a Safe Harbor disclaimer:

'Forward-looking statements are subject to risks and uncertainties. Actual results may differ materially from those expressed or implied. See Risk Factors in our SEC filings for more information.'

**When Required:**
- Any use of future tense ('will', 'expect', 'anticipate', 'believe')
- Earnings forecasts, revenue projections
- Market predictions, growth estimates

**Real Consequence:** Investment advice without RIA registration = $10,000+ fine per violation under Investment Advisers Act. Forward-looking statements without Safe Harbor = potential securities fraud liability.

---

**3. Information Barriers (Chinese Walls) - The Selective Disclosure Problem**

**What Are Information Barriers?**

Think of Chinese Walls like this: *In an investment bank, the M&A division can't share MNPI with the trading division. If traders knew about upcoming mergers, they could front-run the deal (insider trading).*

Your RAG system needs similar barriers:
- **Public data:** Available to all users
- **Internal data:** Restricted to authorized employees only
- **MNPI:** Restricted even from most employees until public disclosure

**Implementation in RAG:**
- Separate vector namespaces for public vs. internal data
- Role-based access control (RBAC) checking user permissions before retrieval
- Audit logs tracking who accessed pre-announcement data

**Why This Matters:**

If your RAG system lets a sales employee access MNPI about upcoming earnings, and that employee trades stock before the earnings call, you've facilitated insider trading. Your company faces SEC investigation.

**Real Consequence:** Insider trading penalties: Up to $5 million in fines (individuals), 20 years in prison for criminal violations. Companies face civil penalties and disgorgement of profits.

---

**Mental Model: Three Compliance Layers**

Think of regulatory output filtering as three security checkpoints:

**Checkpoint 1 (MNPI Detection):** Is this information public or non-public?
**Checkpoint 2 (Disclaimer Injection):** Does this response need a disclaimer?
**Checkpoint 3 (Information Barriers):** Is the user authorized to access this information?

Each checkpoint has different severity:
- MNPI violation = **BLOCK** (criminal liability)
- Missing disclaimer = **ADD DISCLAIMER** (regulatory compliance)
- Unauthorized access = **BLOCK** (information barrier)

If all three checkpoints pass, the response goes to the user. If any fail, the response is blocked or modified.

This is defense-in-depth for financial compliance."

**INSTRUCTOR GUIDANCE:**
- Use analogies: doctor-patient, bank vault, security checkpoints
- Make MNPI concrete: show public vs. non-public examples side-by-side
- Quantify consequences: $50K fines, 20-year prison sentences
- Connect to their M9.1 citation work (source validation)
- Keep pacing brisk—5-7 minutes is tight for this much content

---

**[5:00-7:00] How It Works: Regulatory Output Filter Architecture**

[SLIDE: Data flow diagram showing:
- LLM generates raw output
- Output flows into Regulatory Filter
- Filter checks: (1) MNPI database lookup, (2) Forward-looking detector, (3) Investment advice detector
- For each violation: Block, Add Disclaimer, or Escalate
- Filtered output goes to user
- All violations logged to compliance audit trail]

**NARRATION:**
"Let's walk through how the Regulatory Output Filter processes every LLM response.

**Step 1: LLM Generates Raw Output**

Your LLM (Claude, GPT-4) generates a response to the user's financial query. This is the unfiltered output—potentially containing MNPI, missing disclaimers, or investment advice.

**Step 2: Extract Context About the Response**

Before we can filter, we need to understand:
- What documents were cited? (from your M9.1 citation tracker)
- Are those documents from internal sources or public filings?
- What's the user's role and access level?
- What type of query was this? (from your M9.2 risk classifier)

**Step 3: MNPI Detection**

Run the output through three MNPI checks:

**Check 3a: Source Validation**
- Cross-reference citations against a 'Public Filings Database'
- If cited document is internal-only (emails, forecasts, board minutes) → **Flag as potential MNPI**

**Check 3b: Materiality Indicators**
- Does the output mention: earnings, revenue, M&A, product launches, executive changes, lawsuits?
- These are 'material event keywords'
- If yes + internal source → **Flag as MNPI**

**Check 3c: Temporal Check**
- Is this information forward-looking? ('Q4 earnings will be...')
- Has the information been publicly disclosed yet?
- Check against 'Public Disclosure Timeline Database' (what's been announced vs. what's still internal)

If **all three checks** detect MNPI → **BLOCK the response**. Do NOT add a disclaimer—MNPI should never reach users.

**Step 4: Forward-Looking Statement Detection**

Scan the output for future-tense verbs:
- 'will', 'expect', 'anticipate', 'believe', 'estimate', 'forecast', 'plan', 'project', 'should', 'intend', 'may', 'could'

If found → **Add Safe Harbor disclaimer** at the end of response.

**Step 5: Investment Advice Detection**

Scan the output for advice indicators:
- 'you should', 'recommend', 'good investment', 'undervalued', 'overvalued', 'buy', 'sell', 'strong buy', 'hold', 'rating'

If found → Either:
- **Block** and escalate to human financial advisor (high-risk approach)
- **Add 'Not Investment Advice' disclaimer** (lower-risk approach)

Your M9.2 risk classifier can help: if query was flagged as 'HIGH_RISK_INVESTMENT_ADVICE', always escalate.

**Step 6: Information Barrier Check**

Even if the output passes MNPI checks, verify:
- Does the user's role allow access to the cited documents?
- Are we creating selective disclosure (some users get info, others don't)?

If user lacks permission → **BLOCK with 'Access Restricted' message**

**Step 7: Audit Logging**

Every violation (blocked or disclaimer-added) goes to the compliance audit trail:
- What was flagged?
- Why was it flagged? (MNPI, missing disclaimer, unauthorized access)
- What action was taken? (blocked, escalated, disclaimer added)
- User ID, timestamp, query text, raw output, filtered output

This audit trail is your evidence if the SEC investigates.

**Step 8: Return Filtered Output to User**

If all checks pass (or disclaimers are added), the response goes to the user. If blocked, show a generic 'Cannot answer this query' message and log the incident.

**Key Principle: False Positives Are Acceptable**

Better to block 10 legitimate queries than to leak 1 MNPI response. Your goal is 98%+ **recall** on MNPI detection (catching actual violations), even if precision is lower (false positives)."

**INSTRUCTOR GUIDANCE:**
- Walk through the flow step-by-step with the diagram
- Emphasize: MNPI = BLOCK, not disclaimer
- Connect to M9.1 (citations) and M9.2 (risk assessment)
- Make the '3 checks' pattern memorable: Source, Materiality, Temporal
- Stress the audit trail requirement—it's your defense in investigations

---

## SECTION 3: TECHNOLOGY STACK & SETUP (3-4 minutes, 600-800 words)

**[7:00-9:00] Required Tools and Libraries**

[SLIDE: Technology stack diagram showing:
- Python 3.11+ (core language)
- Regular expressions library (pattern matching)
- PostgreSQL (public filings database, MNPI indicators)
- Redis (caching for disclaimer templates)
- spaCy or NLTK (NLP for tense detection)
- Logging library (compliance audit trail)
- Integration with M9.1 citation tracker
- Integration with M9.2 risk classifier]

**NARRATION:**
"Let's set up the technology stack for regulatory output filtering.

**Core Dependencies (from Generic CCC M1-M4):**
```bash
# Already installed from previous modules
pip install langchain openai python-dotenv redis structlog --break-system-packages
```

**New Dependencies for M9.3:**
```bash
# NLP for linguistic analysis
pip install spacy --break-system-packages
python -m spacy download en_core_web_sm

# Database for MNPI tracking
pip install psycopg2-binary sqlalchemy --break-system-packages

# Pattern matching and text analysis
pip install regex python-dateutil --break-system-packages
```

**Why These Tools?**

**spaCy:** Detects forward-looking statements by analyzing verb tenses and dependency parsing. Better than regex for linguistic patterns like 'will be', 'is expected to', 'anticipate that'.

**PostgreSQL:** Stores:
- Public Filings Database (what's been disclosed publicly)
- MNPI Indicator Patterns (keywords that suggest materiality)
- Public Disclosure Timeline (when information became public)

**Redis:** Caches disclaimer templates so we're not fetching from database on every request. Disclaimers don't change often—perfect for caching.

**regex library:** More powerful than Python's built-in `re` for complex pattern matching (overlapping patterns, lookbehinds).

---

**Database Schema (PostgreSQL):**

```sql
-- Track what information has been publicly disclosed
CREATE TABLE public_disclosures (
    id SERIAL PRIMARY KEY,
    company_ticker VARCHAR(10),
    disclosure_type VARCHAR(50), -- 'earnings', 'merger', 'product_launch'
    disclosure_date TIMESTAMP,
    document_type VARCHAR(20), -- '8-K', '10-Q', 'press_release'
    document_url TEXT,
    content_summary TEXT,
    keywords TEXT[] -- For fast lookup
);

-- MNPI indicators (material event keywords)
CREATE TABLE mnpi_indicators (
    id SERIAL PRIMARY KEY,
    pattern TEXT, -- Regex pattern or keyword
    category VARCHAR(50), -- 'earnings', 'merger', 'executive_change'
    severity VARCHAR(20) -- 'HIGH', 'MEDIUM', 'LOW'
);

-- Disclaimer templates
CREATE TABLE disclaimer_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(100),
    template_text TEXT,
    applies_to VARCHAR(50) -- 'forward_looking', 'investment_advice', 'general'
);

-- Compliance violations log
CREATE TABLE compliance_violations (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(100),
    query_text TEXT,
    raw_output TEXT,
    violation_type VARCHAR(50), -- 'MNPI', 'MISSING_DISCLAIMER', 'UNAUTHORIZED_ACCESS'
    action_taken VARCHAR(50), -- 'BLOCKED', 'DISCLAIMER_ADDED', 'ESCALATED'
    severity VARCHAR(20),
    flagged_patterns TEXT[]
);
```

**Why This Schema?**

**public_disclosures:** Your source of truth for 'what's public'. If information isn't in this table, it's potentially MNPI.

**mnpi_indicators:** Preloaded patterns for material events. Example: 'earnings will', 'merger with', 'product launch', 'CEO resign'.

**disclaimer_templates:** Centralized disclaimer management. Legal team can update templates without code changes.

**compliance_violations:** Your SEC investigation defense. Shows you had controls in place, what you blocked, and why.

---

**Environment Variables:**

```bash
# PostgreSQL connection
POSTGRES_HOST=your-postgres-host
POSTGRES_DB=finance_compliance
POSTGRES_USER=compliance_user
POSTGRES_PASSWORD=your-secure-password

# Redis for caching
REDIS_HOST=your-redis-host
REDIS_PORT=6379

# LLM API (from M9.1)
ANTHROPIC_API_KEY=your-api-key

# Compliance settings
MNPI_DETECTION_THRESHOLD=0.85  # Confidence threshold for blocking
ENABLE_AUTO_DISCLAIMERS=true
ESCALATE_INVESTMENT_ADVICE=true  # If true, block advice queries; if false, add disclaimer
```

**Why These Settings?**

**MNPI_DETECTION_THRESHOLD:** Balance between false positives and false negatives. 0.85 means we need 85% confidence to block as MNPI. Lower = more conservative (more blocking).

**ESCALATE_INVESTMENT_ADVICE:** Policy decision. Conservative approach: block all investment advice. Aggressive approach: add disclaimer and allow.

---

**Integration with M9.1 and M9.2:**

Your Regulatory Output Filter sits **after** M9.1's citation tracker and M9.2's risk classifier:

```
User Query 
  ↓
M9.2 Risk Classifier → Flags HIGH_RISK queries
  ↓
M9.1 RAG Retrieval → Returns cited documents
  ↓
LLM Generation → Creates response with citations
  ↓
**M9.3 Regulatory Filter** → Checks MNPI, adds disclaimers
  ↓
Filtered Response to User
```

You'll access M9.1's citation metadata (`source_type`, `document_url`, `filing_date`) to validate if citations are from public sources.

You'll use M9.2's risk score to decide: Should we auto-add disclaimer or escalate to human?"

**INSTRUCTOR GUIDANCE:**
- Show clear dependency on M9.1 and M9.2 work
- Emphasize database schema—this is your compliance evidence
- Explain threshold tuning: false positives vs. false negatives
- Connect environment variables to risk management decisions
- Keep setup under 3 minutes—they'll see details in code

---

## SECTION 4: TECHNICAL IMPLEMENTATION (12-15 minutes, 2,500-3,200 words)

**[9:00-13:00] Building the MNPI Detection Engine**

[SLIDE: MNPI Detection Flow showing:
- Input: LLM output + citation metadata
- Step 1: Source validation (public vs. internal)
- Step 2: Materiality indicator matching
- Step 3: Temporal check (disclosed or not?)
- Output: MNPI_DETECTED (BLOCK) or CLEAN (continue to disclaimer check)]

**NARRATION:**
"Let's build the MNPI detection engine—the most critical component. This is what prevents insider trading.

**Implementation Strategy:**

We'll use a three-layer detection approach:
1. **Source Validation:** Is the cited document from a public filing or internal source?
2. **Materiality Indicator Matching:** Does the output contain material event keywords?
3. **Temporal Check:** Has this information been publicly disclosed yet?

If **any two** of these layers flag MNPI, we block the response.

Here's the code:"

```python
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import psycopg2
from dataclasses import dataclass

@dataclass
class MNPIViolation:
    """Represents a detected MNPI violation"""
    violation_type: str
    confidence: float
    flagged_content: str
    reason: str
    citation_source: Optional[str] = None

class MNPIDetector:
    """
    Detects Material Non-Public Information (MNPI) in LLM outputs.
    
    MNPI = Material (affects stock price) + Non-Public (not disclosed to all investors)
    
    Strategy: Three-layer detection
    1. Source validation (internal vs. public documents)
    2. Materiality indicators (earnings, M&A, product launches)
    3. Temporal check (disclosed publicly or still internal?)
    
    Conservative bias: False positives acceptable, false negatives catastrophic.
    """
    
    def __init__(self, db_connection_string: str):
        self.db = psycopg2.connect(db_connection_string)
        
        # Load MNPI indicator patterns from database
        # These are material event keywords: earnings, mergers, executive changes, etc.
        self.mnpi_patterns = self._load_mnpi_patterns()
        
        # Load public disclosure timeline
        # Tracks what's been announced publicly and when
        self.public_disclosures = self._load_public_disclosures()
        
        # Materiality threshold: How severe does an indicator need to be?
        # 'HIGH' = definitely material (earnings, M&A)
        # 'MEDIUM' = possibly material (product updates)
        # 'LOW' = unlikely material (minor operational changes)
        self.materiality_threshold = "MEDIUM"
    
    def detect_mnpi(
        self, 
        generated_text: str, 
        citation_metadata: List[Dict],
        user_context: Dict
    ) -> Optional[MNPIViolation]:
        """
        Detect MNPI in generated text using three-layer approach.
        
        Args:
            generated_text: LLM output to check
            citation_metadata: List of cited documents with source info (from M9.1)
            user_context: User role, permissions, access level
        
        Returns:
            MNPIViolation if detected, None if clean
        """
        violations = []
        
        # Layer 1: Source Validation
        # Check if citations come from internal (non-public) sources
        internal_sources = self._check_source_type(citation_metadata)
        if internal_sources:
            violations.append({
                "layer": "SOURCE_VALIDATION",
                "confidence": 0.9,
                "reason": f"Cited {len(internal_sources)} internal documents",
                "sources": internal_sources
            })
        
        # Layer 2: Materiality Indicator Matching
        # Scan for material event keywords: earnings, mergers, etc.
        material_indicators = self._match_materiality_indicators(generated_text)
        if material_indicators:
            violations.append({
                "layer": "MATERIALITY_MATCHING",
                "confidence": self._calculate_materiality_confidence(material_indicators),
                "reason": f"Found {len(material_indicators)} material event indicators",
                "indicators": material_indicators
            })
        
        # Layer 3: Temporal Check
        # Has this information been publicly disclosed yet?
        undisclosed_info = self._check_public_disclosure(
            generated_text, 
            citation_metadata
        )
        if undisclosed_info:
            violations.append({
                "layer": "TEMPORAL_CHECK",
                "confidence": 0.95,
                "reason": "Information not yet publicly disclosed",
                "details": undisclosed_info
            })
        
        # Decision Logic: If ANY TWO layers flag violation, block as MNPI
        # Conservative approach: Better to block false positives than leak true MNPI
        if len(violations) >= 2:
            return MNPIViolation(
                violation_type="MNPI_DISCLOSURE",
                confidence=max(v["confidence"] for v in violations),
                flagged_content=generated_text[:200],  # First 200 chars for audit
                reason=f"Multiple MNPI indicators: {', '.join(v['layer'] for v in violations)}",
                citation_source=internal_sources[0] if internal_sources else None
            )
        
        # Edge case: Single HIGH-confidence violation (e.g., temporal check = 0.95)
        # Even one strong signal can justify blocking
        high_confidence_violations = [v for v in violations if v["confidence"] >= 0.9]
        if high_confidence_violations:
            return MNPIViolation(
                violation_type="MNPI_DISCLOSURE_HIGH_CONFIDENCE",
                confidence=high_confidence_violations[0]["confidence"],
                flagged_content=generated_text[:200],
                reason=high_confidence_violations[0]["reason"]
            )
        
        # Clean: No MNPI detected
        return None
    
    def _check_source_type(self, citation_metadata: List[Dict]) -> List[str]:
        """
        Layer 1: Source Validation
        
        Check if citations are from internal (non-public) sources.
        
        Internal sources include:
        - Email threads
        - Board meeting minutes
        - Internal financial forecasts
        - Executive memos
        - Pre-announcement drafts
        
        Public sources include:
        - SEC filings (10-K, 10-Q, 8-K)
        - Press releases
        - Earnings call transcripts (after the call)
        - Investor presentations (after public release)
        """
        internal_sources = []
        
        # Define internal source patterns
        # These indicate non-public documents
        internal_patterns = [
            r'internal',
            r'draft',
            r'confidential',
            r'board.*minutes',
            r'email',
            r'memo',
            r'forecast.*\d{4}',  # Forecast documents (e.g., "Forecast 2024")
            r'planning.*document'
        ]
        
        for citation in citation_metadata:
            source = citation.get("source", "").lower()
            document_type = citation.get("document_type", "").lower()
            
            # Check if source matches internal patterns
            is_internal = any(
                re.search(pattern, source) or re.search(pattern, document_type)
                for pattern in internal_patterns
            )
            
            # Alternative check: Is this source in our public_disclosures database?
            # If not in database, assume internal
            is_public = self._is_in_public_database(
                citation.get("document_url"),
                citation.get("filing_date")
            )
            
            if is_internal or not is_public:
                internal_sources.append(source)
        
        return internal_sources
    
    def _match_materiality_indicators(self, text: str) -> List[Dict]:
        """
        Layer 2: Materiality Indicator Matching
        
        Scan text for material event keywords that could affect stock price.
        
        Material events (SEC definition):
        - Events a reasonable investor would consider important in making investment decisions
        - Events likely to have a significant effect on market price of securities
        
        Categories:
        - Earnings/Financial Performance
        - Mergers & Acquisitions
        - Executive Changes
        - Product Launches/Discontinuations
        - Legal Proceedings/Regulatory Actions
        """
        matched_indicators = []
        
        # Load patterns from database (cached in __init__)
        for pattern_row in self.mnpi_patterns:
            pattern = pattern_row["pattern"]
            category = pattern_row["category"]
            severity = pattern_row["severity"]
            
            # Skip LOW severity if we're only flagging MEDIUM+
            if severity == "LOW" and self.materiality_threshold != "LOW":
                continue
            
            # Search for pattern in text
            # Use word boundaries to avoid false matches (e.g., 'merger' in 'emergency')
            if re.search(rf'\b{pattern}\b', text.lower()):
                matched_indicators.append({
                    "pattern": pattern,
                    "category": category,
                    "severity": severity
                })
        
        return matched_indicators
    
    def _calculate_materiality_confidence(self, indicators: List[Dict]) -> float:
        """
        Calculate confidence score based on severity and count of indicators.
        
        Logic:
        - Each HIGH severity indicator adds 0.4 to confidence
        - Each MEDIUM severity indicator adds 0.25
        - Each LOW severity indicator adds 0.1
        - Cap at 1.0 (100% confidence)
        
        Example: 1 HIGH + 1 MEDIUM = 0.4 + 0.25 = 0.65 confidence
        """
        severity_weights = {"HIGH": 0.4, "MEDIUM": 0.25, "LOW": 0.1}
        
        confidence = sum(
            severity_weights.get(ind["severity"], 0)
            for ind in indicators
        )
        
        return min(confidence, 1.0)  # Cap at 100%
    
    def _check_public_disclosure(
        self, 
        text: str, 
        citation_metadata: List[Dict]
    ) -> Optional[Dict]:
        """
        Layer 3: Temporal Check
        
        Determine if information in text has been publicly disclosed yet.
        
        Strategy:
        1. Extract key entities/events from text (earnings, mergers, etc.)
        2. Check public_disclosures database for matching disclosures
        3. If no matching disclosure found → Likely MNPI
        4. If disclosure found but AFTER citation date → Information was internal at time
        
        Example:
        - Text: "Q4 earnings will be $3B"
        - Citation date: Jan 5, 2024
        - Public disclosure: Jan 15, 2024 (earnings call)
        - Result: MNPI (information was internal on Jan 5)
        """
        # Extract potential material events from text
        # Look for forward-looking statements about earnings, revenue, etc.
        forward_looking_patterns = [
            (r'(Q[1-4]|quarterly|annual) earnings.*?(\$[\d.]+[BM]|exceed|below)', 'earnings'),
            (r'(revenue|sales) (will|expected to).*?(\$[\d.]+[BM])', 'revenue'),
            (r'(acquiring|merger with|acquisition of)\s+(\w+)', 'merger'),
            (r'(launch|release|unveil).*?(product|service)', 'product_launch')
        ]
        
        for pattern, event_type in forward_looking_patterns:
            match = re.search(pattern, text.lower())
            if match:
                # Check if this event type has been publicly disclosed
                # Get the most recent citation date to establish timeline
                citation_dates = [
                    datetime.fromisoformat(c.get("filing_date", "1970-01-01"))
                    for c in citation_metadata
                    if c.get("filing_date")
                ]
                
                if not citation_dates:
                    # No dates in citations → Cannot verify disclosure timeline
                    # Conservative: Flag as potential MNPI
                    return {
                        "event_type": event_type,
                        "reason": "No citation dates to verify disclosure timeline",
                        "matched_text": match.group(0)
                    }
                
                latest_citation_date = max(citation_dates)
                
                # Query database: Was this event type disclosed publicly before citation date?
                is_disclosed = self._was_publicly_disclosed_before(
                    event_type,
                    latest_citation_date
                )
                
                if not is_disclosed:
                    return {
                        "event_type": event_type,
                        "reason": f"No public disclosure found before {latest_citation_date.date()}",
                        "matched_text": match.group(0)
                    }
        
        return None  # All events appear to be publicly disclosed
    
    def _is_in_public_database(self, document_url: str, filing_date: str) -> bool:
        """Check if document is in public_disclosures database"""
        if not document_url:
            return False
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM public_disclosures
            WHERE document_url = %s
        """, (document_url,))
        
        count = cursor.fetchone()[0]
        cursor.close()
        
        return count > 0
    
    def _was_publicly_disclosed_before(
        self, 
        event_type: str, 
        before_date: datetime
    ) -> bool:
        """Check if event type was publicly disclosed before given date"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM public_disclosures
            WHERE disclosure_type = %s
            AND disclosure_date <= %s
        """, (event_type, before_date))
        
        count = cursor.fetchone()[0]
        cursor.close()
        
        return count > 0
    
    def _load_mnpi_patterns(self) -> List[Dict]:
        """Load MNPI indicator patterns from database (called once in __init__)"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT pattern, category, severity
            FROM mnpi_indicators
            ORDER BY severity DESC
        """)
        
        patterns = [
            {"pattern": row[0], "category": row[1], "severity": row[2]}
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        return patterns
    
    def _load_public_disclosures(self) -> List[Dict]:
        """Load public disclosure timeline from database"""
        # This could be cached in Redis for performance
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT company_ticker, disclosure_type, disclosure_date, document_url
            FROM public_disclosures
            WHERE disclosure_date >= NOW() - INTERVAL '2 years'
            ORDER BY disclosure_date DESC
        """)
        
        disclosures = [
            {
                "ticker": row[0],
                "type": row[1],
                "date": row[2],
                "url": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        return disclosures
```

**Key Implementation Notes:**

1. **Three-layer detection** catches MNPI from multiple angles. Even if one layer fails, two others provide redundancy.

2. **Conservative bias:** We prefer false positives (blocking legitimate responses) over false negatives (leaking MNPI). Better to frustrate users than face SEC investigation.

3. **Database-driven patterns:** Legal team can update MNPI indicators without code changes. Just insert new patterns into `mnpi_indicators` table.

4. **Temporal checking** is critical: Information that's public TODAY might have been MNPI when the document was created. Always check disclosure timeline.

5. **Audit trail:** Every check is logged. If SEC asks 'Why did you block this?', you have documentation.

**Testing the MNPI Detector:**

```python
# Test Case 1: Public information (should be CLEAN)
detector = MNPIDetector("postgresql://user:pass@localhost/compliance")

public_text = "According to the Q3 2023 10-Q filed on Oct 15, 2023, revenue was $2.5 billion."
public_citations = [
    {
        "source": "SEC EDGAR - 10-Q Filing",
        "document_url": "https://sec.gov/...",
        "filing_date": "2023-10-15",
        "document_type": "10-Q"
    }
]

violation = detector.detect_mnpi(
    generated_text=public_text,
    citation_metadata=public_citations,
    user_context={"role": "analyst"}
)

assert violation is None, "Should NOT flag public SEC filing as MNPI"

# Test Case 2: MNPI from internal forecast (should be BLOCKED)
mnpi_text = "Q4 earnings are projected to reach $3 billion based on current pipeline."
internal_citations = [
    {
        "source": "Internal Financial Forecast 2024",
        "document_url": None,  # No public URL
        "filing_date": "2024-01-05",
        "document_type": "internal_forecast"
    }
]

violation = detector.detect_mnpi(
    generated_text=mnpi_text,
    citation_metadata=internal_citations,
    user_context={"role": "analyst"}
)

assert violation is not None, "Should flag internal forecast as MNPI"
assert violation.violation_type == "MNPI_DISCLOSURE"
assert violation.confidence >= 0.8

# Test Case 3: Forward-looking statement before public disclosure (MNPI)
pre_disclosure_text = "The company will announce a merger with XYZ Corp next week."
pre_disclosure_citations = [
    {
        "source": "Board Meeting Minutes - Jan 10, 2024",
        "document_url": None,
        "filing_date": "2024-01-10",
        "document_type": "board_minutes"
    }
]

violation = detector.detect_mnpi(
    generated_text=pre_disclosure_text,
    citation_metadata=pre_disclosure_citations,
    user_context={"role": "executive"}
)

assert violation is not None, "Should flag pre-disclosure merger info as MNPI"
```

**Instructor Demo:**
- Show test cases running live
- Demonstrate false positive (blocking legitimate query) vs. false negative (missing MNPI)
- Explain why we tolerate false positives in compliance
- Show how database updates change detection behavior"

**INSTRUCTOR GUIDANCE:**
- Code walkthrough: Explain each layer clearly
- Emphasize defensive coding: assume worst case
- Show test cases that prove it works
- Connect to M9.1: citation_metadata comes from citation tracker
- Make clear: This is your SEC investigation defense

---

**[13:00-17:00] Implementing Disclaimer Injection**

[SLIDE: Disclaimer Injection Flow showing:
- Input: Filtered LLM output (passed MNPI check)
- Detector 1: Forward-looking statement detector (spaCy tense analysis)
- Detector 2: Investment advice detector (keyword matching)
- For each detected type: Fetch appropriate disclaimer template
- Output: Original response + injected disclaimers]

**NARRATION:**
"Now that we've blocked MNPI, let's handle disclaimers for content that's legally permissible but requires warnings.

**Two Types of Disclaimers:**

1. **Safe Harbor (for forward-looking statements)** - Required by Private Securities Litigation Reform Act
2. **'Not Investment Advice'** - Required by FINRA Rule 2210 and Investment Advisers Act

Here's the implementation:"

```python
import spacy
from typing import List, Tuple
import redis

class DisclaimerInjector:
    """
    Injects required disclaimers into LLM outputs.
    
    Two disclaimer types:
    1. Safe Harbor: For forward-looking statements (PSLRA requirement)
    2. Not Investment Advice: For investment-related content (FINRA Rule 2210)
    
    Strategy: Detect triggers, fetch template, append to response.
    """
    
    def __init__(self, db_connection_string: str, redis_client: redis.Redis):
        self.db = psycopg2.connect(db_connection_string)
        self.redis = redis_client
        
        # Load spaCy for linguistic analysis (verb tense detection)
        # Used for forward-looking statement detection
        self.nlp = spacy.load("en_core_web_sm")
        
        # Cache disclaimer templates in Redis (they rarely change)
        self._cache_disclaimer_templates()
    
    def inject_disclaimers(self, generated_text: str) -> Tuple[str, List[str]]:
        """
        Inject required disclaimers into text.
        
        Returns:
            Tuple of (modified_text, list_of_added_disclaimers)
        """
        added_disclaimers = []
        modified_text = generated_text
        
        # Check 1: Forward-looking statements
        if self._contains_forward_looking(generated_text):
            disclaimer = self._get_disclaimer_template("safe_harbor")
            modified_text += f"\n\n{disclaimer}"
            added_disclaimers.append("SAFE_HARBOR")
        
        # Check 2: Investment advice language
        if self._contains_investment_advice(generated_text):
            disclaimer = self._get_disclaimer_template("not_investment_advice")
            modified_text += f"\n\n{disclaimer}"
            added_disclaimers.append("NOT_INVESTMENT_ADVICE")
        
        # Check 3: FINRA Rule 2210 (communications with retail investors)
        # If response mentions specific securities, add general disclaimer
        if self._mentions_specific_securities(generated_text):
            disclaimer = self._get_disclaimer_template("finra_2210")
            modified_text += f"\n\n{disclaimer}"
            added_disclaimers.append("FINRA_2210")
        
        return modified_text, added_disclaimers
    
    def _contains_forward_looking(self, text: str) -> bool:
        """
        Detect forward-looking statements using linguistic analysis.
        
        Forward-looking indicators:
        - Future tense verbs: 'will', 'shall', 'would'
        - Modal verbs: 'may', 'might', 'could', 'should'
        - Expectation verbs: 'expect', 'anticipate', 'believe', 'estimate', 'project'
        
        Uses spaCy for dependency parsing to avoid false positives.
        Example false positive: 'will' in "the will was probated" (noun, not future tense)
        """
        doc = self.nlp(text)
        
        # Forward-looking verb patterns
        forward_looking_verbs = {
            'will', 'shall', 'would', 'may', 'might', 'could', 'should',
            'expect', 'anticipate', 'believe', 'estimate', 'project', 'forecast',
            'plan', 'intend', 'seek', 'target'
        }
        
        for token in doc:
            # Check if token is a verb (or modal) and matches forward-looking pattern
            if token.pos_ in ('VERB', 'AUX') and token.lemma_ in forward_looking_verbs:
                # Additional context check: Is this actually future-oriented?
                # Example: "we believe revenue will grow" → forward-looking
                # Example: "I believe in honesty" → NOT forward-looking (opinion, not prediction)
                
                # Look for financial context nearby (within 5 tokens)
                financial_context = {'revenue', 'earnings', 'profit', 'growth', 'sales', 
                                    'performance', 'results', 'margin', 'share', 'stock'}
                
                nearby_tokens = [
                    t.lemma_.lower() 
                    for t in doc[max(0, token.i-5):min(len(doc), token.i+5)]
                ]
                
                if any(fin_word in nearby_tokens for fin_word in financial_context):
                    return True
        
        # Regex fallback for phrases spaCy might miss
        # Example: "is expected to", "are projected to"
        forward_looking_phrases = [
            r'is expected to',
            r'are expected to',
            r'is projected to',
            r'are projected to',
            r'is anticipated to',
            r'is forecast to'
        ]
        
        for phrase in forward_looking_phrases:
            if re.search(phrase, text.lower()):
                return True
        
        return False
    
    def _contains_investment_advice(self, text: str) -> bool:
        """
        Detect investment advice language.
        
        Investment advice indicators:
        - Recommendations: 'you should buy', 'recommend', 'suggest'
        - Valuations: 'undervalued', 'overvalued', 'fairly priced'
        - Actions: 'buy', 'sell', 'hold', 'accumulate', 'reduce'
        - Ratings: 'strong buy', 'outperform', 'neutral'
        
        Note: Generic info ('Apple's stock price is $150') is NOT advice.
        Advice requires a recommendation or opinion on action.
        """
        advice_patterns = [
            # Direct recommendations
            r'\b(you should|i recommend|i suggest|consider|worth)\b.*\b(buy|sell|invest)',
            
            # Valuation opinions
            r'\b(undervalued|overvalued|fairly priced|cheap|expensive)\b',
            
            # Action verbs with securities
            r'\b(buy|sell|hold|accumulate|reduce|exit)\b.*\b(stock|shares|securities)',
            
            # Rating language
            r'\b(strong buy|buy|hold|sell|outperform|underperform|neutral)\b.*rating',
            
            # Comparative recommendations
            r'\b(better|worse) investment than\b',
            r'\bprefer\b.*\bover\b',
            
            # ROI predictions
            r'\b(will (gain|lose|return|yield))\b.*\b(percent|%|\$)',
        ]
        
        for pattern in advice_patterns:
            if re.search(pattern, text.lower()):
                return True
        
        return False
    
    def _mentions_specific_securities(self, text: str) -> bool:
        """
        Check if text mentions specific stocks, bonds, or other securities.
        
        Triggers FINRA Rule 2210 disclaimer if we're discussing specific investments.
        
        Detection:
        - Ticker symbols (3-5 uppercase letters)
        - Company names followed by financial terms
        - Bond identifiers (CUSIP format)
        """
        # Ticker symbol pattern: 1-5 uppercase letters (AAPL, MSFT, BRK.A)
        ticker_pattern = r'\b[A-Z]{1,5}(?:\.[A-Z])?\b'
        
        # Exclude common false positives (acronyms, abbreviations)
        exclusions = {'US', 'USA', 'CEO', 'CFO', 'COO', 'CTO', 'VP', 'SVP', 
                     'SEC', 'GAAP', 'IFRS', 'IPO', 'M&A', 'ROI', 'ROE', 'EPS'}
        
        matches = re.findall(ticker_pattern, text)
        tickers = [m for m in matches if m not in exclusions]
        
        if tickers:
            return True
        
        # Check for company names with financial context
        # Example: "Apple's revenue", "Microsoft earnings"
        company_financial_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b.*\b(stock|shares|revenue|earnings|profit)\b'
        
        if re.search(company_financial_pattern, text):
            return True
        
        return False
    
    def _get_disclaimer_template(self, template_name: str) -> str:
        """
        Fetch disclaimer template from Redis cache (or database if not cached).
        
        Templates are defined in database, cached in Redis for performance.
        Legal team can update templates via database without code deployment.
        """
        # Try Redis cache first
        cache_key = f"disclaimer:{template_name}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return cached.decode('utf-8')
        
        # Cache miss: Fetch from database
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT template_text FROM disclaimer_templates
            WHERE template_name = %s
        """, (template_name,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            # Fallback if template not in database
            return self._get_fallback_disclaimer(template_name)
        
        template_text = result[0]
        
        # Cache in Redis (TTL = 1 day, templates rarely change)
        self.redis.setex(cache_key, 86400, template_text)
        
        return template_text
    
    def _get_fallback_disclaimer(self, template_name: str) -> str:
        """
        Fallback disclaimers if database is unavailable.
        
        These are hardcoded minimal disclaimers that meet legal requirements.
        """
        fallback_disclaimers = {
            "safe_harbor": """
[Safe Harbor Statement]
Forward-looking statements are subject to risks and uncertainties. 
Actual results may differ materially from those expressed or implied. 
See Risk Factors in our SEC filings for more information.
            """.strip(),
            
            "not_investment_advice": """
[Disclaimer]
This information is for educational purposes only. It is not investment 
advice, tax advice, or legal advice. Consult a licensed financial advisor 
before making investment decisions.
            """.strip(),
            
            "finra_2210": """
[FINRA Rule 2210 Compliance]
This communication is for informational purposes only and does not 
constitute an offer, solicitation, or recommendation to buy or sell 
securities. Past performance does not guarantee future results.
            """.strip()
        }
        
        return fallback_disclaimers.get(template_name, "[Disclaimer: Consult a professional advisor.]")
    
    def _cache_disclaimer_templates(self):
        """
        Pre-load disclaimer templates into Redis cache on initialization.
        
        Called once when DisclaimerInjector is instantiated.
        Reduces database queries during request processing.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT template_name, template_text FROM disclaimer_templates")
        
        for template_name, template_text in cursor.fetchall():
            cache_key = f"disclaimer:{template_name}"
            # Cache for 1 day (templates are stable)
            self.redis.setex(cache_key, 86400, template_text)
        
        cursor.close()
```

**Testing Disclaimer Injection:**

```python
import redis

# Setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)
injector = DisclaimerInjector(
    db_connection_string="postgresql://user:pass@localhost/compliance",
    redis_client=redis_client
)

# Test Case 1: Forward-looking statement
forward_looking_text = """
Based on current pipeline, we expect Q4 revenue to exceed $3 billion, 
representing 20% year-over-year growth.
"""

modified, disclaimers = injector.inject_disclaimers(forward_looking_text)

assert "SAFE_HARBOR" in disclaimers, "Should detect forward-looking statement"
assert "Forward-looking statements are subject to risks" in modified

# Test Case 2: Investment advice
advice_text = """
Apple is undervalued at current prices. Investors should consider accumulating 
shares for long-term growth potential.
"""

modified, disclaimers = injector.inject_disclaimers(advice_text)

assert "NOT_INVESTMENT_ADVICE" in disclaimers, "Should detect investment advice"
assert "not investment advice" in modified.lower()

# Test Case 3: Specific securities mention
securities_text = """
AAPL reported earnings of $1.50 per share, beating analyst estimates of $1.45.
"""

modified, disclaimers = injector.inject_disclaimers(securities_text)

assert "FINRA_2210" in disclaimers, "Should detect ticker symbol"
assert "informational purposes only" in modified.lower()

# Test Case 4: Neutral factual statement (no disclaimers needed)
factual_text = """
According to the latest 10-Q filing, revenue for Q3 was $2.5 billion.
"""

modified, disclaimers = injector.inject_disclaimers(factual_text)

assert len(disclaimers) == 0, "Should NOT add disclaimers to neutral facts"
assert modified == factual_text, "Text should be unchanged"
```

**Key Implementation Notes:**

1. **spaCy for linguistic analysis** avoids false positives. Regex alone would flag "will" in "last will and testament" as forward-looking.

2. **Contextual detection**: We only flag forward-looking statements if they're in a financial context. "I believe in honesty" isn't a forward-looking statement, but "I believe revenue will grow" is.

3. **Redis caching**: Disclaimer templates are fetched once and cached. No database hit on every request.

4. **Fallback disclaimers**: If database is down, we use hardcoded minimal disclaimers. Better to have basic disclaimer than none.

5. **Multiple disclaimers**: A single response can trigger multiple disclaimers. Example: Forward-looking investment advice gets BOTH Safe Harbor AND Not Investment Advice."

**INSTRUCTOR GUIDANCE:**
- Demo spaCy dependency parsing (show how it catches linguistic nuances)
- Explain false positives vs. false negatives trade-off
- Show Redis caching improving performance
- Test with real financial text examples
- Make clear: Disclaimers are LEGAL requirements, not optional

---

**[17:00-21:00] Building the Complete Regulatory Output Filter**

[SLIDE: Complete filter architecture showing:
- Input: LLM raw output + M9.1 citations + M9.2 risk score
- Step 1: MNPI Detection (block if violation)
- Step 2: Disclaimer Injection (add if needed)
- Step 3: Information Barrier Check (verify user access)
- Step 4: Compliance Audit Log (record all actions)
- Output: Filtered response OR block message]

**NARRATION:**
"Now let's integrate MNPI detection and disclaimer injection into a complete Regulatory Output Filter.

This filter is the final gate before responses reach users—your last line of defense against securities violations."

```python
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog

# Structured logging for compliance audit trail
# Every filter decision is logged with user_id, query, violation type
logger = structlog.get_logger()

@dataclass
class FilterResult:
    """Result of regulatory filtering"""
    allowed: bool  # Can response be shown to user?
    filtered_text: Optional[str]  # Modified response (with disclaimers)
    violations: List[str]  # List of violation types detected
    action_taken: str  # 'ALLOWED', 'BLOCKED', 'DISCLAIMER_ADDED'
    audit_id: str  # Unique ID for compliance audit trail

class RegulatoryOutputFilter:
    """
    Complete regulatory compliance filter for LLM outputs.
    
    Combines:
    1. MNPI Detection (prevent insider trading)
    2. Disclaimer Injection (meet FINRA/PSLRA requirements)
    3. Information Barriers (Chinese Walls)
    4. Compliance Audit Logging (SEC investigation defense)
    
    Used by: Financial RAG systems, investment research platforms, analyst tools
    """
    
    def __init__(
        self, 
        db_connection_string: str,
        redis_client: redis.Redis,
        mnpi_threshold: float = 0.85,
        escalate_investment_advice: bool = True
    ):
        # Initialize sub-components
        self.mnpi_detector = MNPIDetector(db_connection_string)
        self.disclaimer_injector = DisclaimerInjector(db_connection_string, redis_client)
        
        # Configuration
        self.mnpi_threshold = mnpi_threshold  # Confidence threshold for blocking
        self.escalate_investment_advice = escalate_investment_advice
        
        # Database connection for audit logging
        self.db = psycopg2.connect(db_connection_string)
    
    def filter_output(
        self,
        generated_text: str,
        citation_metadata: List[Dict],  # From M9.1 citation tracker
        user_context: Dict,  # User ID, role, permissions
        query_text: str,
        risk_score: Optional[float] = None  # From M9.2 risk classifier
    ) -> FilterResult:
        """
        Filter LLM output through three compliance layers.
        
        Args:
            generated_text: Raw LLM output (unfiltered)
            citation_metadata: List of cited documents (from M9.1)
            user_context: User ID, role, access permissions
            query_text: Original user query (for audit trail)
            risk_score: Risk score from M9.2 classifier (optional)
        
        Returns:
            FilterResult with allowed/blocked status and filtered text
        """
        violations = []
        filtered_text = generated_text
        
        # Generate unique audit ID for this filtering event
        audit_id = self._generate_audit_id()
        
        try:
            # LAYER 1: MNPI Detection (CRITICAL - blocks if violated)
            mnpi_violation = self.mnpi_detector.detect_mnpi(
                generated_text=generated_text,
                citation_metadata=citation_metadata,
                user_context=user_context
            )
            
            if mnpi_violation and mnpi_violation.confidence >= self.mnpi_threshold:
                # MNPI DETECTED - BLOCK RESPONSE
                # Do NOT show to user, do NOT add disclaimer
                # This is potential insider trading
                
                self._log_violation(
                    audit_id=audit_id,
                    user_id=user_context.get("user_id"),
                    query_text=query_text,
                    raw_output=generated_text,
                    violation_type="MNPI_DISCLOSURE",
                    action="BLOCKED",
                    severity="CRITICAL",
                    details=mnpi_violation.reason
                )
                
                return FilterResult(
                    allowed=False,
                    filtered_text=None,
                    violations=["MNPI_DISCLOSURE"],
                    action_taken="BLOCKED",
                    audit_id=audit_id
                )
            
            # LAYER 2: Information Barrier Check (verify user access)
            # Even if not MNPI, user might lack permission for cited documents
            barrier_violation = self._check_information_barriers(
                citation_metadata,
                user_context
            )
            
            if barrier_violation:
                # User doesn't have access to cited documents
                # This creates selective disclosure risk (Reg FD violation)
                
                self._log_violation(
                    audit_id=audit_id,
                    user_id=user_context.get("user_id"),
                    query_text=query_text,
                    raw_output=generated_text,
                    violation_type="INFORMATION_BARRIER",
                    action="BLOCKED",
                    severity="HIGH",
                    details=barrier_violation
                )
                
                return FilterResult(
                    allowed=False,
                    filtered_text=None,
                    violations=["INFORMATION_BARRIER"],
                    action_taken="BLOCKED",
                    audit_id=audit_id
                )
            
            # LAYER 3: Disclaimer Injection (add required disclaimers)
            filtered_text, added_disclaimers = self.disclaimer_injector.inject_disclaimers(
                generated_text
            )
            
            if added_disclaimers:
                violations.extend(added_disclaimers)
            
            # SPECIAL CASE: Investment Advice Escalation
            # If configured to escalate investment advice queries, block and create ticket
            if self.escalate_investment_advice and "NOT_INVESTMENT_ADVICE" in added_disclaimers:
                # High-risk query: Investment advice
                # Escalate to human financial advisor instead of auto-disclaimer
                
                escalation_ticket_id = self._create_escalation_ticket(
                    user_id=user_context.get("user_id"),
                    query_text=query_text,
                    generated_text=generated_text
                )
                
                self._log_violation(
                    audit_id=audit_id,
                    user_id=user_context.get("user_id"),
                    query_text=query_text,
                    raw_output=generated_text,
                    violation_type="INVESTMENT_ADVICE_ESCALATION",
                    action="ESCALATED",
                    severity="MEDIUM",
                    details=f"Escalation ticket: {escalation_ticket_id}"
                )
                
                return FilterResult(
                    allowed=False,
                    filtered_text=None,
                    violations=["INVESTMENT_ADVICE_ESCALATION"],
                    action_taken="ESCALATED",
                    audit_id=audit_id
                )
            
            # All checks passed (or disclaimers added)
            # Log successful filtering
            self._log_success(
                audit_id=audit_id,
                user_id=user_context.get("user_id"),
                query_text=query_text,
                filtered_text=filtered_text,
                disclaimers_added=added_disclaimers
            )
            
            return FilterResult(
                allowed=True,
                filtered_text=filtered_text,
                violations=violations if violations else [],
                action_taken="DISCLAIMER_ADDED" if violations else "ALLOWED",
                audit_id=audit_id
            )
            
        except Exception as e:
            # Filter failure: Log error and fail-safe to BLOCK
            # Better to block than to accidentally leak MNPI due to system error
            
            logger.error(
                "regulatory_filter_error",
                audit_id=audit_id,
                user_id=user_context.get("user_id"),
                error=str(e)
            )
            
            self._log_violation(
                audit_id=audit_id,
                user_id=user_context.get("user_id"),
                query_text=query_text,
                raw_output=generated_text,
                violation_type="FILTER_ERROR",
                action="BLOCKED",
                severity="CRITICAL",
                details=f"Filter error: {str(e)}"
            )
            
            # Fail-safe: Block response if filter fails
            return FilterResult(
                allowed=False,
                filtered_text=None,
                violations=["FILTER_ERROR"],
                action_taken="BLOCKED",
                audit_id=audit_id
            )
    
    def _check_information_barriers(
        self,
        citation_metadata: List[Dict],
        user_context: Dict
    ) -> Optional[str]:
        """
        Check if user has access to all cited documents.
        
        Information barriers (Chinese Walls) prevent selective disclosure.
        Example: Sales team shouldn't access MNPI available to M&A team.
        
        Returns violation reason if barrier violated, None if clean.
        """
        user_role = user_context.get("role")
        user_permissions = user_context.get("permissions", [])
        
        for citation in citation_metadata:
            required_permission = citation.get("required_permission")
            document_type = citation.get("document_type", "")
            
            # If document requires special permission and user lacks it → Barrier violation
            if required_permission and required_permission not in user_permissions:
                return f"User role '{user_role}' lacks permission '{required_permission}' for document type '{document_type}'"
            
            # Check for MNPI-tagged documents
            # Even if not detected by MNPI detector, manually tagged documents require extra access
            if citation.get("is_mnpi") and "mnpi_access" not in user_permissions:
                return f"Document tagged as MNPI, user lacks 'mnpi_access' permission"
        
        return None  # No barrier violations
    
    def _create_escalation_ticket(
        self,
        user_id: str,
        query_text: str,
        generated_text: str
    ) -> str:
        """
        Create escalation ticket for human financial advisor review.
        
        Used when:
        - Investment advice detected and escalation enabled
        - Borderline MNPI cases (confidence 0.7-0.85)
        - High-risk queries from M9.2 classifier
        
        Returns ticket ID for tracking.
        """
        # In production: Integrate with Jira, ServiceNow, or internal ticketing system
        # For now: Insert into database escalation queue
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO escalation_tickets (
                user_id,
                query_text,
                generated_text,
                escalation_reason,
                status,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            query_text,
            generated_text,
            "INVESTMENT_ADVICE_DETECTED",
            "PENDING",
            datetime.now()
        ))
        
        ticket_id = cursor.fetchone()[0]
        self.db.commit()
        cursor.close()
        
        # In M9.4, we'll implement notification to financial advisors
        # For now: Ticket created, advisor checks queue manually
        
        return f"ESC-{ticket_id}"
    
    def _log_violation(
        self,
        audit_id: str,
        user_id: str,
        query_text: str,
        raw_output: str,
        violation_type: str,
        action: str,
        severity: str,
        details: str
    ):
        """
        Log compliance violation to database audit trail.
        
        This audit trail is your defense if SEC investigates.
        Shows you had controls in place, what you blocked, and why.
        
        Retention: 7+ years (SOX requirement for financial records)
        """
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO compliance_violations (
                audit_id,
                timestamp,
                user_id,
                query_text,
                raw_output,
                violation_type,
                action_taken,
                severity,
                flagged_patterns
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            audit_id,
            datetime.now(),
            user_id,
            query_text,
            raw_output,
            violation_type,
            action,
            severity,
            [details]  # PostgreSQL array
        ))
        
        self.db.commit()
        cursor.close()
        
        # Structured logging for real-time monitoring
        logger.warning(
            "compliance_violation",
            audit_id=audit_id,
            user_id=user_id,
            violation_type=violation_type,
            action=action,
            severity=severity
        )
    
    def _log_success(
        self,
        audit_id: str,
        user_id: str,
        query_text: str,
        filtered_text: str,
        disclaimers_added: List[str]
    ):
        """
        Log successful filtering (for analytics and compliance audit).
        
        Even non-violations are logged to show system is working.
        """
        # Log to database for long-term retention
        # (Could use separate table for successes vs. violations)
        
        logger.info(
            "filter_success",
            audit_id=audit_id,
            user_id=user_id,
            disclaimers_added=disclaimers_added,
            output_length=len(filtered_text)
        )
    
    def _generate_audit_id(self) -> str:
        """Generate unique audit ID for tracking"""
        import uuid
        return f"AUD-{uuid.uuid4().hex[:12]}"
```

**Integration with M9.1 and M9.2:**

```python
# Complete workflow: Query → RAG → Filter → User

from your_m9_1_module import ExplainableFinancialRAG  # From M9.1
from your_m9_2_module import RiskClassifier  # From M9.2

def handle_financial_query(
    query: str,
    user_id: str,
    user_role: str,
    user_permissions: List[str]
):
    """
    Complete compliance-aware financial RAG pipeline.
    
    Steps:
    1. M9.2: Classify query risk
    2. M9.1: RAG retrieval with citations
    3. M9.3: Filter output for compliance
    4. Return to user (or block)
    """
    
    # Step 1: Risk Classification (M9.2)
    risk_classifier = RiskClassifier()
    risk_result = risk_classifier.classify_query(query, user_context={"role": user_role})
    
    if risk_result["risk_level"] == "CRITICAL":
        # Extremely high-risk query (e.g., "How can I insider trade?")
        # Block immediately, don't even call RAG
        return {
            "response": "This query cannot be answered due to compliance constraints.",
            "blocked": True,
            "reason": "CRITICAL_RISK"
        }
    
    # Step 2: RAG Retrieval with Citations (M9.1)
    rag_system = ExplainableFinancialRAG()
    rag_result = rag_system.generate_with_citations(
        query=query,
        user_id=user_id
    )
    
    # Step 3: Regulatory Filtering (M9.3)
    filter_system = RegulatoryOutputFilter(
        db_connection_string="postgresql://...",
        redis_client=redis.Redis(),
        mnpi_threshold=0.85,
        escalate_investment_advice=True
    )
    
    filter_result = filter_system.filter_output(
        generated_text=rag_result["response"],
        citation_metadata=rag_result["citations"],
        user_context={
            "user_id": user_id,
            "role": user_role,
            "permissions": user_permissions
        },
        query_text=query,
        risk_score=risk_result["risk_score"]
    )
    
    # Step 4: Return Filtered Response
    if filter_result.allowed:
        return {
            "response": filter_result.filtered_text,
            "blocked": False,
            "disclaimers": filter_result.violations,
            "audit_id": filter_result.audit_id
        }
    else:
        return {
            "response": "This response has been blocked due to regulatory constraints.",
            "blocked": True,
            "reason": filter_result.violations[0],
            "audit_id": filter_result.audit_id
        }
```

**Testing the Complete Filter:**

```python
# Test: MNPI violation (should be BLOCKED)
result = handle_financial_query(
    query="What are our Q4 earnings projections?",
    user_id="analyst_123",
    user_role="financial_analyst",
    user_permissions=["read_public_filings"]
)

assert result["blocked"] == True
assert "MNPI" in result["reason"]

# Test: Forward-looking statement (should add Safe Harbor disclaimer)
result = handle_financial_query(
    query="What is the company's revenue growth forecast?",
    user_id="analyst_123",
    user_role="financial_analyst",
    user_permissions=["read_public_filings"]
)

assert result["blocked"] == False
assert "SAFE_HARBOR" in result["disclaimers"]
assert "Forward-looking statements" in result["response"]

# Test: Investment advice (should escalate)
result = handle_financial_query(
    query="Should I buy Apple stock at current prices?",
    user_id="retail_investor_456",
    user_role="retail_investor",
    user_permissions=["basic_access"]
)

assert result["blocked"] == True
assert "INVESTMENT_ADVICE_ESCALATION" in result["reason"]
```

**Instructor Demo:**
- Run live tests showing MNPI blocking, disclaimer addition, escalation
- Show audit trail in database after each test
- Demonstrate fail-safe behavior (filter error → block response)
- Connect to M9.1 and M9.2: show complete pipeline"

**INSTRUCTOR GUIDANCE:**
- Emphasize: This is defense-in-depth (3 layers)
- Show real queries triggering each filter type
- Demonstrate audit trail—critical for SEC investigations
- Connect to M9.1 (citations) and M9.2 (risk scores)
- Make clear: Filter failures default to BLOCK (fail-safe)

---

## SECTION 5: REALITY CHECK (3-4 minutes, 600-800 words)

**[21:00-24:00] Production Limitations & Honest Constraints**

[SLIDE: Reality check - what this system can and cannot do]

**NARRATION:**
"Let's talk about what regulatory filtering CAN and CANNOT do in production.

**What This System CANNOT Do:**

❌ **Guarantee 100% MNPI detection:** Even with 98% recall, 2% of MNPI might slip through. That's 1 in 50 violations. In high-volume systems (10,000 queries/day), that's 200 potential violations per day. You MUST combine automated filtering with human oversight.

❌ **Replace legal counsel:** This system makes technical decisions (block/allow), not legal judgment. Borderline cases require attorney review. Example: Is a 15% revenue forecast 'material' enough to be MNPI? Depends on context, industry norms, company size—legal question, not technical.

❌ **Protect against adversarial users:** A determined insider can rephrase queries to evade detection. Example: Instead of 'What are Q4 earnings?', they ask 'What's the sum of October, November, December revenue?' Pattern matching has limits.

❌ **Handle novel regulatory requirements:** If a new SEC rule changes MNPI definition or disclaimer requirements, your patterns become outdated instantly. You need a regulatory change management process (legal team updates database patterns).

**What This System CAN Do:**

âœ… **Catch 95-98% of obvious MNPI violations:** Internal forecasts, pre-announcement data, merger negotiations—these are reliably detected IF your public_disclosures database is current.

✅ **Systematically add required disclaimers:** 100% of forward-looking statements get Safe Harbor disclaimers. 100% of investment advice gets 'Not Investment Advice' warnings. This is enforceable consistency.

✅ **Create defensible audit trail:** Every blocked response, every added disclaimer, every filter decision is logged. If SEC investigates, you have evidence of controls.

✅ **Reduce human review workload:** Instead of attorneys reviewing 10,000 queries/day, they review only the 200 escalated cases. 98% automation, 2% human oversight.

**Production Constraints:**

**False Positive Problem:**
- Your filter blocks 'What was Q3 revenue?' because it pattern-matches 'revenue' with 'material event'
- But Q3 has already been publicly disclosed in the 10-Q filing
- User frustration: 'Why can't I get public information?'
- **Solution:** Continuously update public_disclosures database. Automate SEC EDGAR scraping to import filings daily.

**Temporal Lag:**
- Earnings call happens at 9am. Your database updates at 5pm.
- Between 9am-5pm, legitimate queries are blocked because system thinks data is still MNPI.
- **Solution:** Real-time integration with public disclosure events. As soon as 8-K is filed with SEC, update database.

**Context Limitations:**
- Query: 'How did we perform last quarter?' (refers to Q3, already public)
- System blocks because it doesn't understand 'we' = the user's company, and 'last quarter' = Q3.
- Pronoun resolution and temporal understanding require advanced NLP.
- **Solution:** Entity resolution preprocessing. Convert 'we' to company name, 'last quarter' to specific fiscal period.

**Regulatory Interpretation:**
- Is a 5% revenue increase 'material'? 10%? 15%?
- Materiality is context-dependent (5% might be huge for a stable company, small for a startup).
- **Solution:** Materiality thresholds per company, industry, and metric type. Requires domain expertise input.

**Human Escalation Bottleneck:**
- If you escalate 10% of queries to human advisors, and you have 10,000 queries/day, that's 1,000 escalations/day.
- Your compliance team is 5 people. They can't review 200 cases each per day.
- **Solution:** Prioritize escalations by risk score (M9.2). Only highest-risk cases go to humans. Medium-risk gets auto-disclaimer.

**Hallucination Risk:**
- LLM hallucinates: 'Q4 earnings will be $3 billion' (not from any document).
- Your filter checks citations, finds no MNPI sources, allows response.
- But the information itself is false and could mislead investors.
- **Solution:** Hallucination detection (M9.1's citation verification). If no citations support claim, block as unreliable—even if not MNPI.

**Cost Reality:**

Running this system at scale:
- PostgreSQL: ₹3,000/month ($35) for compliance database
- Redis: ₹1,500/month ($18) for disclaimer template caching
- Database queries: 2-3 per filter operation
- Filter latency: +200-300ms per response (3 database lookups + NLP)
- **For 10,000 queries/day:** ~₹5,000/month ($60) infrastructure, +300ms P95 latency

Compare to human review:
- Compliance attorney: ₹2,00,000/month ($2,400) salary
- Can review ~50 queries/day carefully
- To review 10,000 queries/day: Need 200 attorneys = ₹4,00,00,000/month ($480,000)

**Automation ROI:** Spend ₹5,000/month on filtering, save ₹3,99,95,000/month in manual review. 799,900% ROI.

**When This Approach Fails:**

🚨 **Adversarial compliance evasion:** If users know the filter exists, they'll game it. Example: Insider asks 'What's total revenue for last 3 months?' instead of 'What are Q4 earnings?' to evade quarterly keyword detection.

🚨 **Regulatory gray areas:** Not all MNPI is clear-cut. Example: 'We hired 500 engineers this quarter'—is this material? Depends on company size, hiring context, whether it signals growth or backfill.

🚨 **Multi-turn conversation context:** User asks 'What's our revenue trend?' (allowed), then 'What about next quarter?' (MNPI). Filter only sees second query, misses context that makes it MNPI.

🚨 **Non-English queries:** If your system supports Hindi, Spanish, French queries, your regex patterns won't work. Requires multilingual MNPI indicators and disclaimer templates.

**The Honest Answer:**

Regulatory filtering is **risk reduction, not elimination**. You're moving from 100% human-dependent to 98% automated + 2% human oversight. That's a massive improvement, but not perfection.

**Your job:** Combine automated filtering with:
- Human review of escalated cases (M9.4)
- Regular audit of filter performance (false positive/negative rates)
- Legal team oversight of pattern updates
- User training on system limitations

**This is your SEC investigation defense:** 'We implemented industry-standard automated controls, maintained audit trails, and human oversight for high-risk cases.' That's reasonable effort—not perfect, but defensible."

**INSTRUCTOR GUIDANCE:**
- Be brutally honest: 98% is impressive but not 100%
- Quantify the human review bottleneck
- Show ROI calculation (automation vs. manual review)
- Acknowledge adversarial users can game the system
- Emphasize: This is risk reduction, not elimination
- Connect to M9.4 preview: human-in-the-loop handles the 2%

---

## SECTION 6: ALTERNATIVE SOLUTIONS (3-4 minutes, 600-800 words)

**[24:00-27:00] Other Approaches to Regulatory Compliance**

[SLIDE: Decision matrix comparing 5 approaches]

**NARRATION:**
"Our approach isn't the only way to handle regulatory constraints. Let's compare five alternatives.

**Alternative 1: Full Human Review (No Automation)**

**How it works:**
- Every LLM response goes to compliance officer for manual review
- Officer checks: Is this MNPI? Does it need disclaimer? Is user authorized?
- Approved responses go to user, blocked responses logged

**Pros:**
- ✅ 100% accuracy (human judgment on every case)
- ✅ No false positives (humans understand context)
- ✅ Handles regulatory gray areas better than algorithms

**Cons:**
- ❌ Unscalable: 50 queries/day per reviewer max
- ❌ Expensive: ₹2,00,000/month per reviewer salary
- ❌ Slow: 10-30 minute review time per query
- ❌ User experience disaster (wait times kill adoption)

**When to use:**
- Ultra-high-stakes scenarios (M&A deals, IPO preparation)
- <100 queries/day volume
- Queries where errors cause >₹10,00,000 liability each

**When NOT to use:**
- High-volume systems (>1,000 queries/day)
- Real-time user expectations (<5 second response)
- Cost-sensitive deployments

**Cost Comparison:**
- Our automated approach: ₹5,000/month for 10,000 queries/day
- Full human review: ₹4,00,00,000/month (200 reviewers × ₹2,00,000 salary)
- **ROI:** Automation is 799,900% cheaper

---

**Alternative 2: LLM-Based Classification (GPT-4/Claude as Filter)**

**How it works:**
- Use LLM to classify: 'Is this response MNPI? Does it need disclaimer?'
- Prompt: 'Analyze this financial response for material non-public information. Return YES if MNPI detected, NO if clean.'

**Pros:**
- ✅ Better context understanding than regex
- ✅ Handles pronoun resolution ('we', 'last quarter')
- ✅ Adapts to novel phrasing

**Cons:**
- ❌ LLMs hallucinate classifications (false confidence)
- ❌ No audit trail of WHY something was classified as MNPI
- ❌ Expensive: +$0.01 per classification = ₹850/day for 10,000 queries
- ❌ Latency: +2-3 seconds for LLM call
- ❌ Regulatory risk: Can't explain to SEC why LLM classified something as MNPI

**When to use:**
- As a supplement to rule-based detection (hybrid approach)
- For borderline cases flagged by rules (LLM does final check)
- When context understanding is critical

**When NOT to use:**
- As sole classifier (hallucination risk)
- When explainability required (SEC audit)
- Latency-sensitive applications

**Hybrid Approach:**
- Use our rule-based filter first (fast, explainable)
- For 0.7-0.85 confidence cases (borderline), escalate to LLM classifier
- LLM provides second opinion, final decision by human

---

**Alternative 3: Block All Financial Queries (Ultra-Conservative)**

**How it works:**
- Don't allow RAG for financial queries at all
- Route all financial questions to human financial advisors
- RAG only used for non-financial content (HR policies, IT documentation)

**Pros:**
- ✅ Zero MNPI risk (no financial responses)
- ✅ Zero liability for investment advice
- ✅ Simplest compliance (no filtering needed)

**Cons:**
- ❌ Defeats the purpose of financial RAG
- ❌ Users bypass system (use public ChatGPT instead, worse)
- ❌ Competitive disadvantage (competitors offer financial AI)

**When to use:**
- Extremely risk-averse organizations
- Industries with unclear AI regulations (waiting for clarity)
- Temporary solution while building filtering infrastructure

**When NOT to use:**
- If your goal is financial AI assistance
- Competitive environments (fintech, investment research)

---

**Alternative 4: Whitelist-Only Approach (Only Answer Safe Queries)**

**How it works:**
- Maintain whitelist of 'safe queries' and 'safe responses'
- Example: 'What is GAAP?' → Pre-approved answer from accounting glossary
- Any query not on whitelist is blocked

**Pros:**
- ✅ 100% control over what's said
- ✅ No MNPI risk (whitelist doesn't include non-public data)
- ✅ Predictable, auditable responses

**Cons:**
- ❌ Extremely limited utility (can't handle novel queries)
- ❌ High maintenance (whitelist updates for every new query pattern)
- ❌ Poor user experience (blocked frequently)
- ❌ Doesn't leverage LLM capabilities (just retrieval)

**When to use:**
- FAQ-style systems (limited query diversity)
- Highly regulated communications (must be scripted)
- Customer-facing chatbots (brand voice control)

**When NOT to use:**
- Analyst research tools (need flexibility)
- Internal knowledge systems (wide query variety)

---

**Alternative 5: Disclaimer Everywhere (Blanket Protection)**

**How it works:**
- Add 'Not Investment Advice' and Safe Harbor disclaimers to EVERY response
- No filtering, no MNPI detection, just universal disclaimers
- Assumes disclaimers protect from liability

**Pros:**
- ✅ Simple to implement (append text to all responses)
- ✅ Zero false positives (nothing blocked)
- ✅ Fast (no filtering latency)

**Cons:**
- ❌ Does NOT protect against MNPI disclosure (disclaimers don't legalize insider trading)
- ❌ Disclaimer fatigue (users ignore boilerplate)
- ❌ No audit trail of actual risks
- ❌ **Legal reality:** Disclaimers don't prevent securities violations, just mitigate some liability

**When to use:**
- As a baseline (all responses get general disclaimer)
- Combined with MNPI filtering (disclaimers for allowed, blocking for MNPI)

**When NOT to use:**
- As sole compliance strategy (insufficient for MNPI)
- In place of proper information barriers

**Our Approach vs. Universal Disclaimers:**
- We selectively add disclaimers (only when needed)
- We BLOCK MNPI (disclaimers can't legalize insider trading)
- We maintain audit trail (prove due diligence)

---

**Decision Matrix: Which Approach to Choose?**

| Approach | MNPI Protection | Disclaimer Coverage | Scalability | Cost | User Experience |
|----------|----------------|---------------------|-------------|------|-----------------|
| **Our Automated Filter** | 98% | 100% | 10,000+ queries/day | ₹5K/mo | Good (300ms latency) |
| Full Human Review | 100% | 100% | 50 queries/day | ₹4Cr/mo | Poor (10-30 min wait) |
| LLM Classifier | 85% | 90% | 1,000 queries/day | ₹25K/mo | Fair (2-3 sec latency) |
| Block All Financial | 100% | N/A | N/A | ₹0 | Terrible (no answers) |
| Whitelist Only | 100% | 100% | 100 queries/day | ₹10K/mo | Poor (blocked often) |
| Disclaimer Everywhere | 0% | 100% | Unlimited | ₹0 | Good (no blocking) |

**Recommended Hybrid:**
1. Use our automated filter for 95% of queries (fast, explainable, scalable)
2. Use LLM classifier for borderline cases (0.7-0.85 confidence)
3. Escalate to human review for investment advice and critical decisions
4. Add universal baseline disclaimer to ALL responses ('For informational purposes only')

This gives you: Speed (automated), Accuracy (LLM for hard cases), Safety (human for critical), and Compliance (audit trail)."

**INSTRUCTOR GUIDANCE:**
- Present alternatives fairly (each has valid use cases)
- Show decision matrix visual
- Emphasize: No perfect solution, only risk-reduction trade-offs
- Connect to learner's context: What's your query volume? Risk tolerance? Budget?
- Recommend hybrid approach for most production systems

---

## SECTION 7: WHEN NOT TO USE (2-3 minutes, 400-500 words)

**[27:00-29:00] Anti-Patterns & Red Flags**

[SLIDE: Warning signs - when NOT to use automated regulatory filtering]

**NARRATION:**
"Automated regulatory filtering is NOT appropriate for every scenario. Here are the red flags.

**Anti-Pattern #1: Unstructured Financial Advice to Retail Investors**

**Scenario:** You're building a consumer robo-advisor app that gives personalized investment recommendations to retail investors.

**Why filtering isn't enough:**
- Investment advice to retail investors requires RIA registration (Investment Advisers Act)
- You need fiduciary duty, compliance infrastructure, E&O insurance
- Disclaimers don't exempt you from registration requirements
- **Legal reality:** 'Not Investment Advice' disclaimer + giving actual investment advice = Unauthorized practice, SEC fine

**What to do instead:**
- Register as RIA or partner with registered firm
- Implement human-in-the-loop for ALL recommendations
- Use RAG for educational content only, not advice
- Clear separation: Information (allowed) vs. Advice (requires RIA)

**Red flag:** If your users ask 'Should I buy/sell stock X?', you're in advice territory. Filtering won't save you—you need registration.

---

**Anti-Pattern #2: High-Frequency Trading Signals**

**Scenario:** You're using RAG to generate trading signals based on news, filings, and market data. Traders execute these signals automatically.

**Why filtering isn't appropriate:**
- Trading decisions happen in milliseconds, filter adds 300ms (too slow)
- False positives block profitable trades (cost > compliance benefit)
- Adversarial environment (traders will game filter)
- **Better approach:** Pre-filtered data sources only (no MNPI in training data at all)

**What to do instead:**
- Don't use RAG for real-time trading signals
- Use RAG for research/analysis (human makes final trade decision)
- Implement data source validation upstream (only public filings in vector DB)
- Separate 'public data RAG' from 'all data RAG' with strict access controls

---

**Anti-Pattern #3: Adversarial Users (Intentional MNPI Seekers)**

**Scenario:** Users actively trying to extract MNPI by rephrasing queries, probing filter boundaries.

**Why filtering fails:**
- Determined insiders can evade pattern matching
- Example: Instead of 'Q4 earnings forecast?', they ask 'Sum of Oct+Nov+Dec revenue projections?'
- Or use euphemisms: 'How's the pipeline looking?' instead of 'Will we hit targets?'

**What to do instead:**
- Access control at source (remove MNPI from vector DB entirely for unauthorized roles)
- Behavioral monitoring (flag users making unusual query patterns)
- Human review of access logs (compliance team investigates suspicious activity)
- **Root cause:** If users WANT to violate compliance, filtering is whack-a-mole. Fix access controls.

---

**Anti-Pattern #4: Legal/Medical Advice in Regulated Professions**

**Scenario:** Using similar filtering for 'Not Legal Advice' or 'Not Medical Advice' disclaimers.

**Why this doesn't translate:**
- Legal advice liability is context-dependent (attorney-client relationship, state bar rules)
- Medical advice requires diagnosis (disclaimers don't prevent malpractice liability)
- **Regulatory difference:** Finance has clearer rules (Reg FD, FINRA 2210) than law/medicine

**What to do instead:**
- For legal AI: See Legal AI track M6-M9 (different compliance requirements)
- For medical AI: Requires FDA oversight, HIPAA compliance, different approach entirely
- Don't assume 'financial regulatory filtering' translates to other domains

---

**Anti-Pattern #5: Ignoring Jurisdiction Differences**

**Scenario:** You built this system for US SEC regulations, now deploying in EU (MiFID II), India (SEBI), Singapore (MAS).

**Why filtering breaks:**
- MNPI definition varies by country
- Disclaimer requirements differ (EU MiFID II ≠ US FINRA 2210)
- Example: India SEBI has different materiality thresholds than US SEC

**What to do instead:**
- Jurisdiction-specific MNPI patterns (separate tables per regulatory regime)
- Localized disclaimer templates (EU MiFID II, UK FCA, India SEBI)
- Legal counsel review per jurisdiction (can't copy-paste US compliance to EU)

---

**Red Flags Summary:**

🚨 **Don't use automated filtering if:**
- Users expect personalized investment advice (need RIA registration)
- Trading happens in real-time (filter too slow, false positives costly)
- Users are adversarial (they'll evade, fix access controls instead)
- You're in different regulated domain (law, medicine, etc.)
- You're operating across jurisdictions (need localization)

🚨 **Don't use filtering as:**
- Substitute for RIA registration
- Excuse for poor access controls
- Solution to data source problems (garbage in, filtered garbage out)
- One-size-fits-all for global deployments

**The Fundamental Principle:**

Filtering is **output-side defense**. But if you have MNPI in your system to begin with, you've already lost. **Input-side defense** (data source validation, access controls) is more robust.

**Ideal:** Combine both. Filter outputs (catch mistakes) + Control inputs (prevent MNPI ingestion)."

**INSTRUCTOR GUIDANCE:**
- Make anti-patterns feel real (scenarios learners might encounter)
- Emphasize: Filtering is necessary but not sufficient
- Don't let learners think filtering solves all compliance problems
- Connect to broader principle: Defense-in-depth (multiple layers)
- Preview M9.4: Human-in-the-loop handles cases filtering can't

---

## SECTION 8: COMMON FAILURES & FIXES (4-5 minutes, 800-1,000 words)

**[29:00-33:00] Production Failure Modes**

[SLIDE: 5 common failures with before/after code]

**NARRATION:**
"Let's walk through the top 5 failures in production and how to fix them.

**Failure #1: False Positive Storm (Blocking Too Much)**

**Symptom:**
- Users complain: 'I can't get ANY financial data from the system!'
- 80% of queries blocked as MNPI
- Investigation shows: Public earnings data being flagged as MNPI

**Root Cause:**
```python
# BROKEN CODE
def _check_public_disclosure(self, text, citation_metadata):
    # BUG: Only checks if disclosure EXISTS, not if it's CURRENT
    cursor.execute("""
        SELECT COUNT(*) FROM public_disclosures
        WHERE disclosure_type = 'earnings'
    """)
    
    count = cursor.fetchone()[0]
    return count == 0  # If no earnings ever disclosed → Flag as MNPI
```

**What's Wrong:**
- Checks if earnings disclosures exist historically, but doesn't check WHICH quarter
- Example: Q3 2023 earnings are public, but system flags 'What was Q3 revenue?' because it sees 'earnings' keyword and finds earnings disclosures (for other quarters)

**Fix:**
```python
# FIXED CODE
def _check_public_disclosure(self, text, citation_metadata):
    """
    Check if SPECIFIC information has been publicly disclosed.
    
    Key fix: Extract fiscal period from text and check for MATCHING disclosure.
    Example: 'Q3 2023 earnings' → Check for Q3 2023 earnings disclosure specifically
    """
    # Extract fiscal period mentions from text
    # Example: 'Q3 2023', 'third quarter 2023', 'September 2023 quarter'
    fiscal_period_pattern = r'(Q[1-4]|first|second|third|fourth)\s*(?:quarter)?\s*(\d{4})'
    match = re.search(fiscal_period_pattern, text, re.IGNORECASE)
    
    if match:
        quarter = match.group(1)
        year = int(match.group(2))
        
        # Map to standardized fiscal period (Q1 = 01-03, Q2 = 04-06, etc.)
        quarter_num = self._parse_quarter(quarter)
        
        # Check for disclosure of THIS SPECIFIC quarter
        cursor.execute("""
            SELECT COUNT(*) FROM public_disclosures
            WHERE disclosure_type = 'earnings'
            AND EXTRACT(YEAR FROM disclosure_date) = %s
            AND EXTRACT(QUARTER FROM disclosure_date) = %s
        """, (year, quarter_num))
        
        count = cursor.fetchone()[0]
        return count == 0  # Only flag as MNPI if THIS quarter not disclosed
    
    # If no specific fiscal period mentioned, conservative: Flag as potential MNPI
    return True

def _parse_quarter(self, quarter_text: str) -> int:
    """Convert quarter text to number (1-4)"""
    quarter_map = {
        'Q1': 1, 'first': 1,
        'Q2': 2, 'second': 2,
        'Q3': 3, 'third': 3,
        'Q4': 4, 'fourth': 4
    }
    return quarter_map.get(quarter_text.upper(), quarter_map.get(quarter_text.lower()))
```

**Prevention:**
- Test with real public data queries
- Monitor false positive rate (should be <10%)
- User feedback loop: 'Was this block incorrect?' button

---

**Failure #2: Stale Public Disclosures Database**

**Symptom:**
- 8-K filed with SEC at 9am announcing merger
- Users query merger details at 10am
- System blocks as MNPI (because database not updated yet)
- Database updates at 5pm (8 hours later)

**Root Cause:**
```python
# BROKEN CODE
def sync_public_disclosures():
    """Sync public disclosures from SEC EDGAR once per day at 5pm"""
    # Runs as daily cron job
    import_sec_filings(since=datetime.now() - timedelta(days=1))
```

**What's Wrong:**
- Batch update once per day creates temporal lag
- Material events between midnight and 5pm are treated as MNPI even after public disclosure

**Fix:**
```python
# FIXED CODE
def sync_public_disclosures_realtime():
    """
    Real-time sync of SEC filings using EDGAR RSS feed.
    
    SEC publishes filings to RSS within 15-30 minutes of acceptance.
    We poll every 5 minutes to catch new filings.
    """
    import feedparser
    
    # SEC EDGAR RSS feed (updated every 15 minutes)
    rss_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&output=atom"
    
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries:
        filing_url = entry.link
        filing_date = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%S%z")
        company_ticker = self._extract_ticker_from_filing(entry.summary)
        
        # Check if we've already imported this filing
        if not self._filing_exists(filing_url):
            # Parse 8-K to determine disclosure type
            disclosure_type = self._classify_8k_disclosure(filing_url)
            
            # Insert into public_disclosures
            cursor.execute("""
                INSERT INTO public_disclosures (
                    company_ticker,
                    disclosure_type,
                    disclosure_date,
                    document_type,
                    document_url
                ) VALUES (%s, %s, %s, %s, %s)
            """, (company_ticker, disclosure_type, filing_date, "8-K", filing_url))
            
            self.db.commit()
            
            # Invalidate Redis cache for this company
            # Forces next query for this company to check updated disclosures
            self.redis.delete(f"disclosures:{company_ticker}")

# Run as continuous background job (not daily cron)
while True:
    sync_public_disclosures_realtime()
    time.sleep(300)  # Poll every 5 minutes
```

**Prevention:**
- Real-time SEC EDGAR RSS polling
- Webhook integration with legal team (they notify system when 8-K filed)
- Cache invalidation strategy (flush cached disclosures when new filing arrives)

---

**Failure #3: Disclaimer Template Inconsistency**

**Symptom:**
- Legal team updates 'Not Investment Advice' disclaimer in database
- Some users see old disclaimer, others see new one
- Investigation: Redis cache holding stale template

**Root Cause:**
```python
# BROKEN CODE
def _cache_disclaimer_templates(self):
    """Cache templates with 1-day TTL"""
    for template_name, template_text in self._fetch_templates():
        self.redis.setex(f"disclaimer:{template_name}", 86400, template_text)  # 24 hour TTL
```

**What's Wrong:**
- 24-hour TTL means disclaimer changes take up to 24 hours to propagate
- Legal team changes disclaimer at 9am, some users see old version until next day
- Inconsistent disclaimers = potential compliance violation

**Fix:**
```python
# FIXED CODE
def _cache_disclaimer_templates(self):
    """
    Cache templates with versioning and instant invalidation.
    
    Strategy: Include version hash in cache key, invalidate on update.
    """
    for template_name, template_text in self._fetch_templates():
        # Generate version hash of template content
        import hashlib
        version_hash = hashlib.md5(template_text.encode()).hexdigest()[:8]
        
        cache_key = f"disclaimer:{template_name}:v{version_hash}"
        
        # Cache with long TTL (templates rarely change)
        # BUT: When template changes, version hash changes → new cache key
        self.redis.setex(cache_key, 86400 * 7, template_text)  # 7 day TTL
        
        # Store current version mapping
        self.redis.set(f"disclaimer_version:{template_name}", version_hash)

def _get_disclaimer_template(self, template_name: str) -> str:
    """Fetch template using version-aware cache key"""
    # Get current version
    version_hash = self.redis.get(f"disclaimer_version:{template_name}")
    
    if version_hash:
        version_hash = version_hash.decode('utf-8')
        cache_key = f"disclaimer:{template_name}:v{version_hash}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return cached.decode('utf-8')
    
    # Cache miss: Fetch from database and cache with new version
    return self._fetch_and_cache_template(template_name)

# When legal team updates template:
def update_disclaimer_template(template_name: str, new_text: str):
    """Update template and invalidate cache immediately"""
    # Update database
    cursor.execute("""
        UPDATE disclaimer_templates
        SET template_text = %s
        WHERE template_name = %s
    """, (new_text, template_name))
    self.db.commit()
    
    # Invalidate cache by updating version
    new_version_hash = hashlib.md5(new_text.encode()).hexdigest()[:8]
    self.redis.set(f"disclaimer_version:{template_name}", new_version_hash)
    
    # All subsequent requests use new version immediately
```

**Prevention:**
- Version-aware caching (content hash in cache key)
- Instant invalidation when legal team updates
- Monitoring: Alert if template version divergence detected

---

**Failure #4: Multilingual MNPI Evasion**

**Symptom:**
- User asks in Hindi: 'अगली तिमाही की कमाई क्या होगी?' (What will next quarter's earnings be?)
- System doesn't detect MNPI (patterns are English-only)
- MNPI leaks in non-English responses

**Root Cause:**
```python
# BROKEN CODE
# All MNPI patterns are English
mnpi_patterns = ['earnings will', 'revenue forecast', 'merger with']
```

**What's Wrong:**
- Users can evade detection by asking in Hindi, Spanish, French
- Even if LLM responds in English, query bypasses filter

**Fix:**
```python
# FIXED CODE
from googletrans import Translator

def detect_mnpi(self, generated_text: str, citation_metadata: List[Dict], user_context: Dict):
    """
    Multi-lingual MNPI detection.
    
    Strategy: Translate non-English text to English, then apply patterns.
    """
    # Detect language
    translator = Translator()
    detected = translator.detect(generated_text)
    
    # If not English, translate for pattern matching
    if detected.lang != 'en':
        translated_text = translator.translate(generated_text, dest='en').text
    else:
        translated_text = generated_text
    
    # Apply English MNPI patterns to translated text
    return self._apply_mnpi_patterns(translated_text, citation_metadata, user_context)

# Alternative: Maintain multilingual pattern database
def _load_mnpi_patterns_multilingual(self):
    """Load MNPI patterns for multiple languages"""
    cursor.execute("""
        SELECT pattern, language, category, severity
        FROM mnpi_indicators_multilingual
        WHERE language IN ('en', 'hi', 'es', 'fr', 'de')
    """)
    
    # Group by language
    patterns_by_lang = defaultdict(list)
    for pattern, lang, category, severity in cursor.fetchall():
        patterns_by_lang[lang].append({
            "pattern": pattern,
            "category": category,
            "severity": severity
        })
    
    return patterns_by_lang
```

**Prevention:**
- Translation layer before pattern matching
- Multilingual pattern database (hire native speakers to translate patterns)
- Language-specific disclaimer templates

---

**Failure #5: Filter Bypass via Markdown/Code Blocks**

**Symptom:**
- User asks: 'Show me Q4 earnings forecast in a markdown table'
- LLM responds with:
```
| Quarter | Earnings Forecast |
|---------|------------------|
| Q4 2024 | $3.1 billion     |
```
- Filter checks raw text, doesn't detect 'earnings' inside markdown table syntax
- MNPI leaks in structured format

**Root Cause:**
```python
# BROKEN CODE
def _match_materiality_indicators(self, text: str):
    # Only searches plain text, doesn't parse markdown
    return re.search(r'earnings.*\$[\d.]+[BM]', text)
```

**What's Wrong:**
- Markdown formatting breaks regex patterns
- Code blocks, tables, lists create whitespace/syntax that evades detection

**Fix:**
```python
# FIXED CODE
import markdown
from bs4 import BeautifulSoup

def _match_materiality_indicators(self, text: str):
    """
    Parse markdown before pattern matching.
    
    Strategy: Convert markdown to plain text, then match patterns.
    """
    # Convert markdown to HTML
    html = markdown.markdown(text)
    
    # Extract plain text from HTML
    soup = BeautifulSoup(html, 'html.parser')
    plain_text = soup.get_text()
    
    # Now apply patterns to plain text
    for pattern_row in self.mnpi_patterns:
        pattern = pattern_row["pattern"]
        if re.search(rf'\b{pattern}\b', plain_text.lower()):
            # Pattern matched in plain text extracted from markdown
            return True
    
    return False
```

**Prevention:**
- Parse structured formats (markdown, JSON, CSV) before pattern matching
- Test with adversarial formatting (tables, code blocks, Unicode tricks)

---

**Debugging Checklist:**

When filter fails in production:
1. Check public_disclosures database currency (last update time)
2. Verify fiscal period extraction (is system matching correct quarter?)
3. Test multilingual queries (are non-English queries translated?)
4. Inspect markdown/formatting (is structured data parsed correctly?)
5. Review cache invalidation (are disclaimer updates propagating?)

**Mental Model:**

Filter failures come from:
- **Temporal misalignment:** Database lags reality
- **Linguistic gaps:** English-only patterns, multilingual users
- **Format evasion:** Structured data bypasses regex
- **Cache staleness:** Updates don't propagate

Fix by: Real-time sync, translation, parsing, invalidation."

**INSTRUCTOR GUIDANCE:**
- Show before/after code for each failure
- Run live tests demonstrating each bug and fix
- Emphasize: These are REAL production failures (not theoretical)
- Create debugging mental model (temporal, linguistic, format, cache)
- Preview M10: Production monitoring catches these failures early

---

## SECTION 9: DOMAIN-SPECIFIC CONSIDERATIONS (5-6 minutes, 1,000-1,200 words)

### **9B: FINANCE AI - REGULATORY COMPLIANCE REQUIREMENTS**

**[33:00-39:00] Finance AI Domain Context**

[SLIDE: Finance AI regulatory landscape showing:
- SEC (Securities and Exchange Commission)
- FINRA (Financial Industry Regulatory Authority)
- SOX (Sarbanes-Oxley Act)
- Investment Advisers Act
- Private Securities Litigation Reform Act
- Regulation FD (Fair Disclosure)
- All connected to RAG system compliance requirements]

**NARRATION:**
"Because this is a Finance AI system, you have specific regulatory requirements beyond generic RAG compliance.

Let me explain the six core financial regulations that govern your RAG system's outputs.

---

**Regulation #1: Securities Exchange Act 1934 - Section 10(b) (Insider Trading)**

**What it regulates:**
- Material Non-Public Information (MNPI) disclosure
- Prohibits trading on MNPI or tipping others
- Applies to ALL securities (stocks, bonds, derivatives)

**Why it exists:**
Securities markets require fairness. If insiders trade on non-public information, retail investors are disadvantaged. The 1929 crash and resulting lack of trust led to this regulation.

**RAG implications:**
- Your system CAN leak MNPI if it retrieves from internal documents
- Example: Internal forecast document → RAG response → User trades → Insider trading
- **Your filter is the technical control preventing this violation**

**Penalties:**
- Civil: Up to $5 million per individual, $25 million per organization
- Criminal: Up to 20 years in prison for willful violations
- Disgorgement of profits (return all gains from illegal trades)

**Why this matters to you:**
If your RAG system facilitates insider trading, you're liable. 'We didn't know the LLM would say that' is not a defense. You need provable controls.

---

**Regulation #2: Regulation FD (Fair Disclosure)**

**What it regulates:**
- Companies must disclose material information to ALL investors simultaneously
- Cannot selectively disclose to analysts, institutional investors before public

**Why it exists:**
Before Reg FD (enacted 2000), companies would tip favored analysts with earnings hints before public announcements. Reg FD requires fair, simultaneous disclosure.

**RAG implications:**
- If your system gives some users access to MNPI and others don't → Selective disclosure violation
- Example: Analyst with 'internal_access' permission gets Q4 forecast, retail investor doesn't
- **Information barriers (Chinese Walls) prevent this**

**Penalties:**
- SEC enforcement action
- Fines: $50,000 to $500,000 per violation
- Requires public corrective disclosure (embarrassing)

**RAG implementation:**
- All users must get same information at same time
- OR: Block MNPI for ALL users until public disclosure
- Cannot create tiers where 'premium users' get pre-announcement data

---

**Regulation #3: Investment Advisers Act - Section 202(a)(11) (Investment Advice)**

**What it regulates:**
- Defines 'investment adviser' as anyone who:
  1. Provides advice about securities
  2. As a regular business
  3. For compensation
- Requires federal registration (or state, if <$100M AUM)

**Why it exists:**
Protects investors from unqualified advisors. Only registered advisers with fiduciary duty can give personalized investment recommendations.

**RAG implications:**
- If your system says 'You should buy Apple stock' → Investment advice
- Requires RIA registration, compliance infrastructure, insurance
- **'Not Investment Advice' disclaimer is mitigation, not exemption**

**Penalties:**
- SEC enforcement
- $10,000+ fine per violation (unauthorized practice)
- Cease-and-desist orders
- Criminal charges for willful violations

**RAG implementation:**
- Block queries asking for buy/sell recommendations
- OR: Add 'Not Investment Advice' disclaimer AND escalate to human RIA
- Provide information (company financials) but NOT recommendations (buy this stock)

---

**Regulation #4: Private Securities Litigation Reform Act (PSLRA) - Safe Harbor**

**What it regulates:**
- Protects companies from securities fraud liability for forward-looking statements
- IF they include 'meaningful cautionary statements' (Safe Harbor disclaimer)

**Why it exists:**
Before PSLRA (1995), companies were sued for missing earnings guidance. To encourage transparency, Congress created Safe Harbor for forward-looking statements.

**RAG implications:**
- LLMs generate forward-looking statements: 'Revenue will grow 20%'
- Without Safe Harbor disclaimer → Potential securities fraud liability if prediction wrong
- **Disclaimer injection protects from PSLRA liability**

**Penalties (if no Safe Harbor):**
- Securities fraud lawsuits
- Shareholder class actions (millions in legal costs)
- SEC investigation for misleading investors

**RAG implementation:**
- Detect future tense verbs: 'will', 'expect', 'believe', 'anticipate'
- Auto-inject Safe Harbor disclaimer
- Template: 'Forward-looking statements are subject to risks and uncertainties. Actual results may differ materially.'

---

**Regulation #5: FINRA Rule 2210 (Communications with the Public)**

**What it regulates:**
- All communications with retail investors must be:
  - Fair and balanced
  - Not misleading
  - Include required disclaimers
- Applies to broker-dealers, investment firms

**Why it exists:**
Retail investors need protection from misleading marketing. FINRA (self-regulatory organization for broker-dealers) enforces communication standards.

**RAG implications:**
- If your RAG system is customer-facing → FINRA 2210 applies
- Must include: 'Past performance does not guarantee future results'
- Cannot make exaggerated claims: 'Guaranteed 20% returns'

**Penalties:**
- FINRA fines: $5,000 to $100,000+ per violation
- Suspension of broker-dealer license
- Required retraining, compliance monitoring

**RAG implementation:**
- Add FINRA 2210 disclaimer when discussing specific securities
- Template: 'This communication is for informational purposes only and does not constitute an offer, solicitation, or recommendation to buy or sell securities.'

---

**Regulation #6: Sarbanes-Oxley Act (SOX) - Sections 302 & 404**

**What it regulates:**
- Section 302: CEO/CFO must certify accuracy of financial statements
- Section 404: Companies must maintain internal controls over financial reporting
- Applies to public companies

**Why it exists:**
Enron, WorldCom accounting scandals (2001-2002) destroyed investor trust. SOX created executive accountability and audit requirements.

**RAG implications:**
- Your RAG system provides financial data → Must have audit trail (SOX 404 control)
- If system generates incorrect financial statements → CEO/CFO liable (SOX 302)
- **Compliance audit trail proves internal controls exist**

**Penalties:**
- Criminal liability for executives: Up to 20 years in prison for false certification
- SEC fines for inadequate controls
- Auditor penalties (if they miss control failures)

**RAG implementation:**
- Audit trail: Log every query, response, citation, filter decision
- Retention: 7+ years (SOX requirement)
- Hash chain verification (prove logs not tampered with)
- Annual audit: Prove system didn't leak MNPI, had proper disclaimers

---

**Domain-Specific Tools Landscape (Finance AI)**

**Legal/Compliance Platforms:**
- **FINRA Gateway:** Compliance filing system for broker-dealers
- **SEC EDGAR API:** Programmatic access to public filings (use for public_disclosures sync)
- **Bloomberg Compliance:** Pre-built compliance templates, disclaimer libraries ($24K/year)
- **Thomson Reuters Regulatory Intelligence:** Tracks regulatory changes ($15K-25K/year)

**When to use:**
- EDGAR API: Real-time sync of public disclosures (required for avoiding false positives)
- Bloomberg Compliance: If budget allows, use pre-built disclaimer templates
- Regulatory Intelligence: Tracks SEC/FINRA rule changes (update MNPI patterns accordingly)

**Financial Data Providers:**
- **Public/Free:** yfinance, Alpha Vantage, SEC EDGAR
- **Paid/Premium:** Bloomberg Terminal ($24K/year), Refinitiv Eikon ($22K/year)

**Choose based on:**
- Free: Good for public market data, filings (acceptable for most RAG use cases)
- Paid: Required if you need real-time pricing, proprietary research, analyst estimates

---

**Required Disclaimers (Finance AI - Systematic Implementation)**

**Disclaimer #1: Not Investment Advice**

**When required:**
- Any response mentioning: buy, sell, hold, undervalued, overvalued, recommendation
- Comparison of investment options: 'Stock A vs. Stock B'
- Valuation analysis: 'Fair value is $150'

**Template:**
```
[Disclaimer: Not Investment Advice]
This information is for educational purposes only. It is not investment advice, 
tax advice, or legal advice. Consult a licensed financial advisor before making 
investment decisions.
```

**UI implementation:**
- Display prominently at top or bottom of every response
- Persistent disclaimer in footer: 'All information for educational purposes only'
- User must acknowledge disclaimer (checkbox) before accessing investment-related queries

---

**Disclaimer #2: Safe Harbor (Forward-Looking Statements)**

**When required:**
- Any future-tense statement: 'will', 'expect', 'anticipate', 'believe', 'estimate'
- Predictions: 'Revenue will grow', 'Stock price should reach $200'
- Forecasts: 'Q4 earnings are projected to...'

**Template:**
```
[Safe Harbor Statement]
Forward-looking statements are subject to risks and uncertainties. Actual 
results may differ materially from those expressed or implied. See Risk 
Factors in our SEC filings for more information.
```

---

**Disclaimer #3: FINRA Rule 2210 (Retail Communications)**

**When required:**
- Any communication with retail investors (non-institutional)
- Mentions of specific securities: AAPL, MSFT, bonds, ETFs
- Performance data: 'Stock returned 15% last year'

**Template:**
```
[FINRA Rule 2210 Compliance]
This communication is for informational purposes only and does not constitute 
an offer, solicitation, or recommendation to buy or sell securities. Past 
performance does not guarantee future results.
```

---

**Production Deployment Checklist (Finance AI Specific)**

Before deploying to production:

✅ **Legal Review:**
- [ ] Securities attorney reviews MNPI detection logic
- [ ] Compliance officer approves disclaimer templates
- [ ] Risk committee signs off on information barrier implementation

✅ **Regulatory Alignment:**
- [ ] SEC EDGAR integration configured (real-time public disclosures)
- [ ] FINRA Rule 2210 disclaimers implemented
- [ ] Safe Harbor templates validated by legal
- [ ] Investment Advisers Act compliance verified (RIA registration or proper disclaimers)

✅ **Technical Validation:**
- [ ] MNPI detection tested: 98%+ recall on test dataset
- [ ] Disclaimer injection tested: 100% of forward-looking statements covered
- [ ] Information barriers tested: Unauthorized users blocked from MNPI
- [ ] Audit trail tested: All violations logged, 7-year retention configured

✅ **Stakeholder Sign-Off:**
- [ ] CFO approves (financial data accuracy)
- [ ] Chief Compliance Officer approves (regulatory compliance)
- [ ] CTO approves (system architecture, security)
- [ ] Legal approves (disclaimers, liability protection)

✅ **Monitoring & Alerts:**
- [ ] MNPI violation alerts configured (Slack, email, PagerDuty)
- [ ] False positive rate monitored (should be <10%)
- [ ] Disclaimer coverage monitored (should be 100% for forward-looking statements)
- [ ] SEC EDGAR sync monitoring (should update within 30 min of filing)

✅ **Insurance & Liability:**
- [ ] E&O (Errors & Omissions) insurance updated to cover AI systems
- [ ] D&O (Directors & Officers) insurance includes AI-related securities violations
- [ ] Cyber insurance covers data breach of MNPI

✅ **User Training:**
- [ ] Analysts trained on system capabilities and limitations
- [ ] Compliance team trained on escalation workflows (M9.4)
- [ ] Executives briefed on liability implications (SOX 302)

✅ **Incident Response:**
- [ ] MNPI leak procedure documented (what to do if MNPI escapes filter)
- [ ] SEC self-reporting protocol (when to voluntarily disclose violations)
- [ ] Forensic audit capability (prove what user accessed when)

---

**Liability Landscape (Finance AI)**

**Scenario #1: MNPI Leak**
- **Violation:** Insider trading facilitation (Section 10(b))
- **Who's liable:** Company, executives, potentially engineers
- **Penalty:** $5M individual, $25M company, 20 years prison
- **Defense:** Audit trail proves you had controls, leak was despite reasonable effort

**Scenario #2: Missing Disclaimer on Forward-Looking Statement**
- **Violation:** Securities fraud (if statement is materially misleading)
- **Who's liable:** Company, CFO (SOX 302 certification)
- **Penalty:** Shareholder lawsuit, SEC investigation, $500K-$5M fine
- **Defense:** Safe Harbor disclaimer systematically added, this was isolated glitch

**Scenario #3: Investment Advice Without RIA Registration**
- **Violation:** Unauthorized practice (Investment Advisers Act)
- **Who's liable:** Company, individual providing advice
- **Penalty:** $10K per violation, cease-and-desist, potential criminal charges
- **Defense:** 'Not Investment Advice' disclaimer + human escalation (M9.4)

**Scenario #4: Selective Disclosure (Reg FD)**
- **Violation:** Providing MNPI to some users before public disclosure
- **Who's liable:** Company, executives
- **Penalty:** $50K-$500K, required corrective disclosure
- **Defense:** Information barriers (Chinese Walls) blocked unauthorized access, failure was technical glitch

**Risk Mitigation Strategy:**

1. **Insurance:** E&O, D&O, cyber insurance (cost: ₹5-10L/year)
2. **Legal Review:** Annual audit by securities attorney (cost: ₹2-5L/year)
3. **Compliance Monitoring:** Quarterly reviews by Chief Compliance Officer
4. **Technical Controls:** The filter you just built (cost: ₹5K/month infrastructure)

**Total Compliance Cost:** ₹12-20L/year for 10,000 queries/day system

**Compare to Manual Review:** ₹4 Cr/year (200 compliance officers)

**ROI:** Automated compliance = 95% cost savings + scalability

---

**Failure Modes (Finance AI Specific)**

**Failure #1: CEO Makes Forward-Looking Statement Without Safe Harbor**

**Scenario:**
- CEO interview: 'We expect 20% revenue growth next year'
- RAG system summarizes interview, includes quote
- No Safe Harbor disclaimer added (interview text bypasses filter)

**Consequence:**
- If growth doesn't materialize → Shareholder lawsuit
- 'CEO misled investors with false forecast'

**Fix:**
- Pre-process CEO interviews, earnings calls through filter
- Add Safe Harbor to ALL summaries of executive statements
- Metadata tagging: 'source=ceo_interview' triggers automatic Safe Harbor

---

**Failure #2: Analyst Asks in Code to Bypass Filter**

**Scenario:**
- Analyst knows filter blocks 'Q4 earnings forecast'
- Asks: 'What's f(Oct) + f(Nov) + f(Dec) where f = monthly revenue?'
- System doesn't recognize this as quarterly earnings query

**Consequence:**
- MNPI leak (Q4 = Oct+Nov+Dec)

**Fix:**
- Behavioral monitoring: Flag unusual query patterns (mathematical obfuscation)
- User intent classification: Detect when user is rephrasing to evade
- Escalate suspicious queries to compliance team (M9.4)

---

**Failure #3: Multilingual MNPI Leak**

**Scenario:**
- Hindi-speaking user asks: 'अगली तिमाही की कमाई क्या है?'
- Translation: 'What are next quarter's earnings?'
- English MNPI patterns don't match Hindi query

**Consequence:**
- MNPI leak in non-English response

**Fix (covered in Section 8):**
- Translate queries to English before pattern matching
- Multilingual MNPI pattern database
- Language-specific disclaimer templates

---

**Why Domain Expertise Matters:**

Finance AI isn't just 'RAG with financial data.' It's:
- Understanding SEC, FINRA, SOX regulations
- Knowing materiality thresholds (5% revenue = material for stable company, not for startup)
- Recognizing investment advice vs. information (subtle distinction with huge liability difference)
- Implementing compliance controls that survive SEC audit

**If you don't understand Reg FD, you'll build a system that violates it.**

**If you don't understand Safe Harbor, you'll expose company to securities fraud liability.**

**Domain expertise = difference between compliant system and SEC investigation.**"

**INSTRUCTOR GUIDANCE:**
- Make regulations CONCRETE with real examples
- Quantify penalties: $5M, 20 years prison, not abstract
- Show WHY each regulation exists (historical context)
- Connect each regulation to specific RAG implementation
- Emphasize: Domain expertise isn't optional, it's REQUIRED
- Reference M9.1 (citations) and M9.2 (risk) throughout
- Preview M9.4: Human-in-the-loop escalation for borderline cases

---

## SECTION 10: DECISION CARD (3-4 minutes, 600-800 words)

**[39:00-42:00] When to Use This Approach**

[SLIDE: Decision matrix with use cases, anti-patterns, and cost tiers]

**NARRATION:**
"Let me give you a clear decision framework for when to implement automated regulatory filtering.

**Use This Approach When:**

✅ **High Query Volume (>1,000 queries/day)**
- Manual review can't scale
- Automated filtering handles 98%, humans review 2%
- Example: Investment research platform, 10,000 analyst queries/day

✅ **Clear Regulatory Framework (Finance, Healthcare, Legal)**
- Well-defined rules (Reg FD, FINRA 2210, HIPAA, attorney-client privilege)
- Patterns are codifiable (not purely judgment-based)
- Example: Financial RAG with SEC/FINRA regulations

✅ **Need for Audit Trail (SEC/SOX/GDPR Compliance)**
- Must prove you had controls in place
- Audit trail required for regulatory reviews
- Example: Public company RAG system (SOX 404 compliance)

✅ **Explicit Liability Risk (Securities violations, insider trading)**
- False negatives = catastrophic (jail time, $5M fines)
- Worth investing in automated controls
- Example: MNPI protection in investment bank RAG

✅ **Budget for Infrastructure (₹5-50K/month)**
- PostgreSQL, Redis, NLP processing
- Real-time SEC EDGAR sync, monitoring
- Cost justified by risk reduction

---

**Don't Use This Approach When:**

❌ **Low Query Volume (<100 queries/day)**
- Manual review is faster and cheaper
- Automation overhead not justified
- Example: Boutique law firm, 20 legal queries/day

❌ **Ambiguous Regulations (No Clear Codifiable Rules)**
- Requires human judgment on every case
- Patterns can't capture nuance
- Example: 'Is this content offensive?' (subjective, context-dependent)

❌ **Real-Time Trading (Millisecond Latency Requirements)**
- Filter adds 300ms (unacceptable for HFT)
- Better to use pre-filtered data sources only
- Example: Algorithmic trading signals

❌ **Adversarial Users (Intentionally Evading Compliance)**
- Determined users will game filter
- Access control > output filtering
- Example: Insider trying to extract MNPI

❌ **Multi-Jurisdictional Without Localization**
- US SEC rules ≠ EU MiFID II ≠ India SEBI
- Need jurisdiction-specific patterns
- Don't deploy US filter globally without legal review

---

**Cost Tiers with Concrete Examples**

Let me show you what deployment looks like at three scales.

**TIER 1: Small Investment Advisor (20 advisors, 100 queries/day, 5K client documents)**

**Infrastructure:**
- PostgreSQL: ₹1,000/month ($12)
- Redis: ₹500/month ($6)
- Database storage: 10 GB
- Queries: 3,000/month (100/day × 30 days)

**Total Monthly Cost:** ₹1,500 ($18)

**Per Advisor:** ₹75/advisor/month ($0.90)

**Metrics:**
- MNPI detection: 98% recall
- Disclaimer coverage: 100%
- Filter latency: +200ms
- False positive rate: 5% (5 queries/day blocked incorrectly)

**Headcount Impact:**
- Without filtering: 1 compliance officer reviewing 100 queries/day (8 hours)
- With filtering: 1 compliance officer reviewing 5 escalated queries/day (1 hour)
- **Labor savings:** ₹1,40,000/month (7 hours/day × ₹600/hour × 30 days)

**ROI:** Spend ₹1,500, save ₹1,40,000 = 9,233% ROI

---

**TIER 2: Mid-Size Investment Bank (100 analysts, 1,000 queries/day, 50K research documents)**

**Infrastructure:**
- PostgreSQL: ₹8,000/month ($95) - larger instance for concurrent queries
- Redis: ₹3,000/month ($35) - cluster for high availability
- Database storage: 100 GB
- SEC EDGAR sync: ₹2,000/month ($24) - real-time RSS polling
- Monitoring (Prometheus, Grafana): ₹2,000/month ($24)

**Total Monthly Cost:** ₹15,000 ($180)

**Per Analyst:** ₹150/analyst/month ($1.80)

**Metrics:**
- MNPI detection: 98% recall
- Queries processed: 30,000/month (1,000/day × 30 days)
- Escalations: 600/month (2% escalation rate)
- Filter latency: +250ms (more database queries)

**Headcount Impact:**
- Without filtering: 20 compliance officers (50 queries/day each)
- With filtering: 3 compliance officers (200 escalations/day shared)
- **Labor savings:** ₹34,00,000/month (17 officers × ₹2,00,000 salary)

**ROI:** Spend ₹15,000, save ₹34,00,000 = 22,567% ROI

---

**TIER 3: Large Hedge Fund (500 traders/analysts, 10,000 queries/day, 200K market research docs)**

**Infrastructure:**
- PostgreSQL: ₹30,000/month ($360) - high-performance cluster, read replicas
- Redis: ₹15,000/month ($180) - multi-region cluster
- Database storage: 1 TB (historical audit trail)
- SEC EDGAR sync: ₹5,000/month ($60) - dedicated service, <1 min latency
- Monitoring & Alerting: ₹10,000/month ($120)
- Bloomberg Compliance integration: ₹2,00,000/month ($2,400) - enterprise license

**Total Monthly Cost:** ₹2,60,000 ($3,120)

**Per User:** ₹520/user/month ($6.24)

**Metrics:**
- MNPI detection: 98% recall
- Queries processed: 3,00,000/month (10,000/day × 30 days)
- Escalations: 6,000/month (2% rate)
- Filter latency: +300ms (global deployment, multiple regions)
- Uptime: 99.9% (required for trading hours)

**Headcount Impact:**
- Without filtering: 200 compliance officers (50 queries/day each)
- With filtering: 15 compliance officers (400 escalations/day shared)
- **Labor savings:** ₹3,70,00,000/month (185 officers × ₹2,00,000 salary)

**ROI:** Spend ₹2,60,000, save ₹3,70,00,000 = 14,123% ROI

**Note:** At this scale, compliance team size is still significant (15 officers), but manageable. Without automation, 200 compliance officers would be operationally impossible.

---

**Decision Tree:**

```
START: Do you need regulatory compliance for LLM outputs?
│
├─ YES → Is liability risk high? (Securities violations, insider trading, malpractice)
│   │
│   ├─ YES → Is query volume >100/day?
│   │   │
│   │   ├─ YES → **Use Automated Filtering + Human Escalation** (this approach)
│   │   │
│   │   └─ NO → Use Manual Review Only (too few queries to justify automation)
│   │
│   └─ NO → Can regulations be codified into patterns? (clear rules vs. judgment)
│       │
│       ├─ YES → **Use Automated Filtering** (lower liability, but still valuable for consistency)
│       │
│       └─ NO → Use Human Review (ambiguous regulations need judgment)
│
└─ NO → Don't implement regulatory filtering (focus on other RAG improvements)
```

**Key Takeaway:**

Automated regulatory filtering makes sense when:
- Liability risk is high (false negatives = catastrophic)
- Query volume is high (>100/day minimum, ideally >1,000/day)
- Regulations are codifiable (Reg FD, FINRA 2210, SOX)
- Budget supports ₹5-50K/month infrastructure

**Don't use when:**
- Low volume (<100/day)
- Low risk (no securities violations)
- Ambiguous regulations (pure judgment calls)
- Adversarial users (access control is better solution)"

**INSTRUCTOR GUIDANCE:**
- Show three concrete cost tiers (small, medium, large)
- Calculate ROI for each tier (spend vs. labor savings)
- Emphasize: Even small firms get massive ROI
- Make decision tree actionable
- Connect to learner's context: What's your query volume?

---

## SECTION 11: PRACTATHON CONNECTION (2-3 minutes, 400-500 words)

**[42:00-44:00] Hands-On Mission**

[SLIDE: PractaThon mission overview]

**NARRATION:**
"Let's connect this to your hands-on PractaThon mission.

**Your Mission:**

Build a compliance-aware financial RAG system that:
1. Detects MNPI in LLM outputs (98%+ recall)
2. Adds required disclaimers (Safe Harbor, Not Investment Advice)
3. Blocks unauthorized access (information barriers)
4. Creates audit trail (compliance logging)

**Starter Dataset (Provided):**

You'll get:
- 100 SEC filings (10-K, 10-Q, 8-K) from public companies (Apple, Microsoft, Tesla, etc.)
- 50 internal documents (marked 'MNPI' for testing): Board minutes, earnings forecasts, merger memos
- 20 analyst queries (mix of safe and MNPI-seeking)
- Pre-loaded PostgreSQL database (public_disclosures table populated)

**Implementation Steps:**

**Step 1: Setup (30 minutes)**
- Install dependencies: `psycopg2`, `spacy`, `redis`
- Load database schema (provided SQL file)
- Configure environment variables

**Step 2: Implement MNPI Detection (2-3 hours)**
- Build `MNPIDetector` class with three-layer detection
- Test with provided MNPI test cases (should catch 98%+ of 50 internal docs)
- Verify false positive rate (<10% of public filings)

**Step 3: Implement Disclaimer Injection (1-2 hours)**
- Build `DisclaimerInjector` class with spaCy linguistic analysis
- Test with forward-looking statements (should detect 100%)
- Test with investment advice queries (should detect and add disclaimer)

**Step 4: Integrate Complete Filter (2-3 hours)**
- Build `RegulatoryOutputFilter` combining MNPI + disclaimers + barriers
- Connect to your M9.1 citation tracker (use citation metadata)
- Connect to your M9.2 risk classifier (use risk scores for escalation)

**Step 5: Testing & Validation (2-3 hours)**
- Run 20 provided test queries
- Expected results:
  - 5 queries blocked as MNPI
  - 10 queries get Safe Harbor disclaimer
  - 3 queries get Not Investment Advice disclaimer
  - 2 queries blocked for unauthorized access (information barrier)
- Generate audit log for all 20 queries

**Step 6: Create Audit Report (1 hour)**
- Export compliance violations table
- Show: What was blocked, why, when, by whom
- Format: CSV or PDF (suitable for SEC audit)

**Success Criteria:**

✅ **MNPI Detection:**
- Recall ≥ 98% (catch 49+ of 50 MNPI documents)
- False positive rate ≤ 10% (block <10 of 100 public filings)

✅ **Disclaimer Coverage:**
- 100% of forward-looking statements get Safe Harbor
- 100% of investment advice queries get Not Investment Advice disclaimer
- Disclaimers use proper templates (FINRA 2210, PSLRA compliant)

✅ **Information Barriers:**
- Unauthorized users blocked from MNPI (100% enforcement)
- Authorized users can access public data (no false blocking)

✅ **Audit Trail:**
- All 20 queries logged (timestamp, user, query, response, violations)
- Log includes: violation type, action taken, flagged patterns
- Retention configured: 7+ years (SOX requirement)

**Bonus Challenges:**

🎯 **Challenge 1: Multilingual Detection**
- Add Hindi translation layer
- Test with Hindi MNPI query: 'अगली तिमाही की कमाई क्या है?'
- Should detect and block

🎯 **Challenge 2: Real-Time SEC EDGAR Sync**
- Implement RSS polling (every 5 minutes)
- Simulate new 8-K filing
- Verify system updates public_disclosures within 5 minutes

🎯 **Challenge 3: LLM Hybrid Classifier**
- Use Claude/GPT-4 for borderline cases (0.7-0.85 confidence)
- Compare LLM classification accuracy vs. rule-based

**Deliverables:**

1. Working code (GitHub repo)
2. Test results showing success criteria met
3. Audit log CSV (all 20 queries with violations)
4. 1-page reflection: What worked, what was challenging, production considerations

**Time Estimate:** 10-15 hours total

**Submission Deadline:** [Your cohort's schedule]

**Resources:**
- Starter code: [GitHub repo link]
- Dataset: [Download link]
- Database schema: [SQL file]
- Documentation: [Setup guide]

**Getting Stuck?**
- Office hours: [Schedule]
- Slack channel: #m9-3-practathon
- FAQs: [Doc link]

Good luck! You're building production-grade compliance controls. This is resume-worthy work."

**INSTRUCTOR GUIDANCE:**
- Make mission feel achievable (10-15 hours is reasonable)
- Provide clear success criteria (98% recall, 100% disclaimer coverage)
- Emphasize: This is portfolio-worthy (show employers)
- Preview M9.4: Next video integrates human-in-the-loop
- Encourage bonus challenges for advanced learners

---

## SECTION 12: SUMMARY & NEXT STEPS (2-3 minutes, 400-500 words)

**[44:00-47:00] What You Built & What's Next**

[SLIDE: Journey summary - M9.1, M9.2, M9.3, M9.4]

**NARRATION:**
"Let's recap what you accomplished today.

**What You Built:**

✅ **MNPI Detection Engine** that:
- Uses three-layer detection (source validation, materiality indicators, temporal check)
- Achieves 98%+ recall on MNPI violations
- Creates defensible audit trail for SEC investigations
- **Prevents insider trading facilitation**

✅ **Disclaimer Injection System** that:
- Detects forward-looking statements (spaCy linguistic analysis)
- Identifies investment advice language
- Systematically adds Safe Harbor and 'Not Investment Advice' disclaimers
- **Ensures FINRA Rule 2210 and PSLRA compliance**

✅ **Complete Regulatory Output Filter** that:
- Combines MNPI detection + disclaimer injection + information barriers
- Integrates with M9.1 (citations) and M9.2 (risk assessment)
- Logs all violations for compliance audit
- **Protects your company from securities violations**

**This Isn't Theoretical:**

You built production-grade compliance controls that:
- Save ₹34-370 Cr/year in manual review costs (depending on scale)
- Reduce liability risk (MNPI, investment advice violations)
- Create SEC-audit-ready documentation
- Enable scalable financial AI systems

**How This Fits in Finance AI Track:**

```
M9.1: Explainability & Citations
  ↓
  Proves: WHERE information came from (source validation)
  ↓
M9.2: Risk Assessment
  ↓
  Proves: WHAT risk level query represents (escalation trigger)
  ↓
M9.3: Regulatory Constraints (TODAY)
  ↓
  Proves: OUTPUT is compliant (MNPI blocked, disclaimers added)
  ↓
M9.4: Human-in-the-Loop (NEXT)
  ↓
  Proves: HIGH-RISK cases reviewed by experts (final safety layer)
```

**Complete Compliance Stack:** Explainable inputs + Risk-assessed retrieval + Regulated outputs + Human oversight = SEC-defensible financial AI

---

**What's Next in M9.4:**

In the next video, we'll implement **Human-in-the-Loop workflows** for:
- Escalating borderline MNPI cases (confidence 0.7-0.85) to compliance officers
- Routing investment advice queries to registered financial advisors
- Creating approval workflows for high-stakes decisions (M&A announcements, earnings releases)
- Building notification systems (Slack, email, ticketing)

**The driving question will be:** *How do you build escalation workflows that get human expertise on critical decisions WITHOUT creating a manual review bottleneck?*

You'll learn:
- Role-based routing (analyst queries → senior analyst, investment advice → RIA)
- Approval mechanisms with time limits (approve/reject within 2 hours)
- Escalation tracking and SLA monitoring
- Integration with compliance tools (Jira, ServiceNow, Slack)

---

**Before Next Video:**

✅ **Complete the PractaThon mission:**
- Build MNPI detector
- Test disclaimer injection
- Create audit report
- Aim for 98% recall, 100% disclaimer coverage

✅ **Experiment:**
- Try multilingual queries (does Hindi bypass detection?)
- Test adversarial queries (can you evade filter?)
- Measure latency (how much overhead does filtering add?)

✅ **Reflect:**
- What edge cases did you find?
- Where did false positives occur?
- How would you improve MNPI detection?

**Resources:**
- Code repository: [GitHub link]
- Dataset: [Download link]
- Starter PostgreSQL schema: [SQL file]
- Further reading: SEC Regulation FD overview, FINRA Rule 2210 guide

**Community:**
- Share your PractaThon results: #m9-3-showcase
- Help peers: #m9-3-questions
- Office hours: [Schedule link]

Great work today. You built compliance controls that protect companies from multi-million dollar liability. This is production-ready, resume-worthy engineering.

See you in M9.4 for human-in-the-loop workflows!"

**INSTRUCTOR GUIDANCE:**
- Celebrate accomplishment (this was complex, high-stakes work)
- Connect to M9.1, M9.2, preview M9.4 (show progression)
- Make next steps actionable (PractaThon, experimentation)
- Emphasize portfolio value (show employers you understand finance compliance)
- End on encouraging note

---

## METADATA FOR PRODUCTION

**Video File Naming:**
`FinanceAI_M9_V9.3_Regulatory_Constraints_LLM_Outputs_Augmented_v1.0.md`

**Duration Target:** 45-50 minutes

**Word Count:** ~9,500 words

**Slide Count:** 35-40 slides

**Code Examples:** 8 substantial code blocks (MNPI detector, disclaimer injector, complete filter, test cases, integration with M9.1/M9.2, failure fixes)

**TVH Framework v2.0 Compliance Checklist:**
- ✅ Reality Check section present (Section 5) - Limitations, false positives, costs
- ✅ 5 Alternative Solutions provided (Section 6) - Human review, LLM classifier, block all, whitelist, universal disclaimers
- ✅ When NOT to Use cases (Section 7) - 5 anti-patterns with clear red flags
- ✅ 5 Common Failures with fixes (Section 8) - False positives, stale database, cache staleness, multilingual evasion, markdown bypass
- ✅ Complete Decision Card (Section 10) - Use cases, cost tiers, decision tree
- ✅ Section 9B filled (Finance AI Domain) - 6 regulations, tools landscape, disclaimers, liability
- ✅ PractaThon connection (Section 11) - 10-15 hour hands-on mission

**Quality Enhancements Applied:**
- ✅ Educational inline comments in all code blocks
- ✅ 3 tiered cost examples in Section 10 (Small ₹1,500/mo, Mid ₹15,000/mo, Large ₹2,60,000/mo)
- ✅ Detailed diagram descriptions for all [SLIDE: ...] annotations (3-5 bullet points each)
- ✅ WHY explained for all regulations (not just WHAT)
- ✅ Quantified consequences (fines, prison, liability)
- ✅ Domain-specific analogies and examples
- ✅ Required disclaimers with templates

**Production Notes:**
- Insert `<!-- SLIDE: [Description] -->` for slide transitions
- Mark code blocks with language: ```python, ```sql, ```bash
- Use **bold** for emphasis on key regulatory terms
- Include timestamps [MM:SS] at section starts
- Highlight instructor guidance separately
- Connect to M9.1 (citations) and M9.2 (risk assessment) throughout
- Preview M9.4 (human-in-the-loop) at appropriate points

---

## END OF SCRIPT

**Track:** Finance AI (Domain-Specific)  
**Module:** M9 - Financial Compliance & Risk  
**Video:** M9.3 - Regulatory Constraints in LLM Outputs  
**Section 9:** Section 9B (Finance AI Domain-Specific)  
**Version:** 1.0  
**Created:** November 16, 2025  
**Status:** Ready for Production Review  
**Next Steps:** Create Concept Script (M9.3 Concept) + Bridge Script (M9.3 to M9.4)

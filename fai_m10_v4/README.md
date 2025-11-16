# L3 M10.4: Disaster Recovery & Business Continuity

## Overview

This module implements production-grade disaster recovery and business continuity capabilities for financial RAG (Retrieval-Augmented Generation) systems. It provides cross-region replication monitoring, automated failover orchestration, and FINRA Rule 4370 compliance reporting to ensure trading-critical systems meet stringent RTO (Recovery Time Objective) and RPO (Recovery Point Objective) requirements.

**Key Capabilities:**
- **Multi-Region DR Replication**: Automated replication from US-EAST-1 (primary) to US-WEST-2 (DR) with continuous lag monitoring
- **15-Minute RTO**: Automated failover orchestration meeting market-hours availability requirements
- **1-Hour RPO**: Data loss minimization through real-time replication monitoring
- **FINRA Compliance**: Quarterly DR test reporting for FINRA Rule 4370 regulatory requirements
- **SOX Section 404**: 7-year backup retention with audit trail documentation

**Regulatory Context:**
This implementation addresses FINRA Rule 4370 (Business Continuity Planning), SOX Section 404 (Internal Controls), and GLBA (data encryption) requirements for broker-dealer trading systems where portfolio managers rely on RAG systems for billion-dollar trading decisions.

---

## What You'll Learn

By working through this module, you will:

1. **Implement Multi-Region DR Replication** - Set up automated replication of Pinecone vector database, PostgreSQL metadata, and financial documents from US-EAST-1 to US-WEST-2, with continuous sync maintaining 1-hour RPO

2. **Build Automated Failover Systems** - Create DNS-based failover with health checks, pre-flight DR verification, and automated traffic redirection meeting 15-minute RTO

3. **Configure SOX-Compliant Backup Strategies** - Implement 7-year backup retention for financial documents (SOX Section 404), with versioning, encryption, and immutable storage

4. **Execute FINRA-Required Quarterly DR Tests** - Build test procedures measuring RTO/RPO performance, validate data consistency, document results for FINRA Rule 4370

5. **Generate Regulatory Compliance Reports** - Create automated DR compliance reports showing test results, RTO/RPO metrics, failover procedures for FINRA auditors and SEC examiners

---

## Concepts Covered

### Concept 1: Recovery Time Objective (RTO)

**RTO is the maximum acceptable downtime for your system.** It answers: "How long can we be down before business impact becomes unacceptable?"

For financial RAG systems during market hours (9:30 AM - 4:00 PM ET), **RTO = 15 minutes** is the industry standard.

**Rationale:**
- Markets move rapidly during trading hours
- Portfolio managers need real-time information for trading decisions
- 15-minute delay is maximum acceptable lag before opportunity cost becomes material
- One hour of downtime during market hours = ₹30K+ in direct losses

### Concept 2: Recovery Point Objective (RPO)

**RPO is the maximum acceptable data loss measured in time.** It answers: "How much recent data can we afford to lose?"

For financial RAG systems, **RPO = 1 hour** is standard.

**Rationale:**
- Financial documents don't change every second (unlike real-time market data)
- Real-time tick data has separate specialized systems
- One-hour replication interval balances cost and risk
- Most document ingestion happens in batch windows (evenings, weekends)

### Concept 3: Disaster Recovery Tiers

**Cold DR (24+ hours RTO):**
- **Cost**: ~10% of production infrastructure costs
- **Use case**: Internal tools, non-critical systems, historical analysis
- **Recovery process**: Provision infrastructure → Restore from backups → Verify → Go live (1-3 days)
- **When appropriate**: Systems not used during market hours, no regulatory RTO requirements

**Warm DR (2-4 hours RTO):**
- **Cost**: ~30-50% of production infrastructure costs
- **Use case**: Business-critical but not trading-critical systems
- **Recovery process**: Scale up instances → Sync recent data → Test → Go live (2-4 hours)
- **When appropriate**: Compliance research, risk analysis, overnight batch processing

**Hot DR (< 15 minutes RTO):**
- **Cost**: ~80-100% of production costs (nearly doubles infrastructure)
- **Use case**: Trading systems, market data feeds, critical financial RAG
- **Recovery process**: Detect failure → Verify DR health → Switch DNS → Live (< 15 min)
- **When appropriate**: Market-hours trading support, FINRA-regulated systems, material trading decisions

**This module implements Hot DR** because financial RAG systems supporting trading operations cannot tolerate 2-4 hour downtimes during market hours.

### Concept 4: Cross-Region Replication

**Cross-region replication** creates real-time copies of data in geographically separated AWS regions to protect against regional disasters (data center outages, natural disasters, network partitions).

**Components replicated:**
- **Pinecone vector database**: Primary index (US-EAST-1) → Replica index (US-WEST-2), ~5 minute lag
- **PostgreSQL metadata**: RDS Multi-AZ primary → Read replica, < 10 second lag typical
- **Redis cache**: Primary → Replica with continuous sync
- **S3 documents**: Cross-region replication with versioning

**Monitoring requirements:**
- Continuous lag measurement (CloudWatch metrics)
- Alerts when lag exceeds 10 minutes (approaching RPO violation)
- Data consistency validation (compare record counts between regions)

### Concept 5: DNS-Based Failover

**DNS failover** uses Route 53 health checks to automatically redirect traffic from failed primary region to healthy DR region.

**How it works:**
1. Route 53 runs health checks against primary region every 30 seconds
2. If 3 consecutive checks fail (~90 seconds), CloudWatch alarm triggers
3. Lambda function verifies DR region health (replication connected, lag acceptable)
4. Route 53 DNS updated to point to DR region IP addresses
5. 60-second TTL ensures clients get new DNS within 1 minute
6. Total failover time: 8-12 minutes (well within 15-minute RTO)

**Critical configuration:**
- TTL = 60 seconds (faster propagation, but higher query costs)
- Health check interval = 30 seconds
- Consecutive failures = 3 (prevents flapping from transient issues)

### Concept 6: FINRA Rule 4370 - Business Continuity Planning

**FINRA Rule 4370** requires broker-dealers to:
- Create and maintain business continuity plans (BCP)
- **Test the BCP at least annually** (industry practice: quarterly)
- Document test results with RTO/RPO measurements
- Demonstrate ability to resume operations "as soon as possible"

**Compliance requirements:**
- Quarterly DR test execution in non-production environment
- Measure actual RTO achieved (must be ≤ 15 minutes for trading systems)
- Measure actual data loss (must be ≤ 1 hour RPO)
- Generate written report with test date, results, pass/fail status
- File report with compliance team for FINRA examiner review

**Consequences of non-compliance:**
- FINRA examination findings
- Regulatory fines
- Requirement to remediate deficiencies within 90 days
- Potential prohibition from operating without adequate BCP

### Concept 7: SOX Section 404 - Internal Controls & 7-Year Retention

**SOX Section 404** requires public companies to maintain internal controls over financial reporting, including:
- **7-year document retention** for financial records
- Audit trail showing which documents informed which decisions
- Prevention of unauthorized modification or deletion
- Ability to recover historical documents for regulatory investigations

**Implementation:**
- S3 + Glacier storage for long-term retention (cost-effective for rarely accessed data)
- Versioning enabled (tracks all changes, prevents accidental deletion)
- Encryption at rest with AWS KMS (GLBA requirement)
- Cross-region replication (protects against regional disasters)
- Immutable storage (prevents tampering)

**Cost structure:**
- S3 Standard: ₹0.60/GB/month (first 30 days, frequently accessed)
- S3 Glacier: ₹0.10/GB/month (7-year retention, rarely accessed)
- Estimated: ₹20K/month for typical financial RAG document corpus

---

## How It Works

### System Architecture

**Primary Region (US-EAST-1):**
```
┌─────────────────────────────────────────────────┐
│ PRIMARY REGION (US-EAST-1)                      │
├─────────────────────────────────────────────────┤
│ • Pinecone Production Index (primary source)    │
│ • RDS PostgreSQL Multi-AZ (writer database)     │
│ • EC2 AutoScaling (2-6 instances, FastAPI)      │
│ • ElastiCache Redis (cache layer)               │
│ • S3 backup storage (30-day retention)          │
│                                                  │
│ Route 53 DNS: rag.yourcompany.com → PRIMARY IP  │
└─────────────────────────────────────────────────┘
          │
          │ Continuous Replication
          │ (PostgreSQL: < 10s lag, Pinecone: < 5min lag)
          ▼
┌─────────────────────────────────────────────────┐
│ DR REGION (US-WEST-2)                           │
├─────────────────────────────────────────────────┤
│ • Pinecone Replica Index (receives updates)     │
│ • RDS Read Replica (asynchronous replication)   │
│ • EC2 AutoScaling (idle, scales during failover)│
│ • Redis Replica (continuously synchronized)     │
│ • S3 with cross-region replication              │
└─────────────────────────────────────────────────┘
```

**Cross-Region Orchestration:**
- **Route 53**: DNS failover with 60-second TTL
- **CloudWatch**: Health checks (90-second failure window = 3 consecutive failures)
- **Lambda**: Automated failover orchestration with pre-flight DR verification
- **PagerDuty**: On-call engineer alerts for manual intervention if needed

**Backup & Compliance:**
- **S3 + S3 Glacier**: 7-year document retention (SOX Section 404)
- **Versioning**: Prevents accidental deletion, tracks all changes
- **Cross-region replication**: Protects backups against regional disasters

### Disaster Scenario Workflow

**Timeline: Hard Drive Failure in Primary Region**

```
09:35 AM - Hard drive fails in US-EAST-1 RDS instance
           (Primary database goes offline)

09:36 AM - CloudWatch health check fails (no response from /health endpoint)

09:37 AM - 3rd consecutive health check failure detected
           CloudWatch alarm triggers, PagerDuty alerts on-call engineer

09:38 AM - Lambda function executes DR verification script
           ✅ Replication lag = 2 minutes (within RPO)
           ✅ Data consistency = 99.8% (acceptable)
           ✅ Replica connected and healthy

09:39 AM - Route 53 DNS updated to point to US-WEST-2 DR region
           60-second TTL propagation begins

09:40 AM - First client requests start hitting DR region

09:43 AM - All traffic redirected to DR (TTL expired on client caches)

TOTAL RTO: 8 minutes ✅ (within 15-minute requirement)
DATA LOSS: 2 minutes of ingested documents ✅ (within 1-hour RPO)
```

**Post-Incident Recovery:**
1. Incident report filed (regulatory requirement for FINRA)
2. Primary region restoration initiated (provision new instance, restore from backup)
3. Once primary recovered and tested (typically 2-4 hours), failback to primary
4. FINRA notification: "Incident 09:35 AM ET, recovered 09:43 AM ET, 8-minute impact"

---

## Prerequisites

### Knowledge Prerequisites

- **Generic CCC M1-M6 completed**: RAG MVP foundations, optimization, deployment
- **Finance AI M10.1 completed**: Security architecture, VPC isolation, encryption
- **Finance AI M10.2 completed**: Monitoring, CloudWatch, PagerDuty integration
- **Finance AI M10.3 completed**: Cost optimization, caching, Redis

### Infrastructure Prerequisites

- **AWS account** with multi-region permissions (EC2, RDS, Route 53, CloudWatch, Lambda)
- **Pinecone Production tier account** (free/starter tiers don't support cross-region replication)
- **PostgreSQL credentials** for primary + DR replica databases
- **Domain with Route 53 hosted zone** (requires domain ownership and nameserver configuration)
- **PagerDuty integration key** (optional, for failover alerts)

### Assumed Resources

- **Primary region (US-EAST-1) RAG system already deployed** from M10.1-M10.3
- If you haven't completed Finance AI M10.1-M10.3, pause here and finish those modules first

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yesvisare/financial_ai_ccc_l2.git
cd financial_ai_ccc_l2/fai_m10_v4
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and configure your credentials
# At minimum, set:
#   AWS_ENABLED=true
#   AWS_ACCESS_KEY_ID=your_key
#   AWS_SECRET_ACCESS_KEY=your_secret
#   POSTGRESQL_ENABLED=true
#   POSTGRES_PRIMARY_HOST=your_primary_db
#   POSTGRES_DR_HOST=your_dr_db
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ENABLED` | Yes | Enable AWS services (`true`/`false`) |
| `AWS_REGION_PRIMARY` | Yes* | Primary AWS region (default: `us-east-1`) |
| `AWS_REGION_DR` | Yes* | DR AWS region (default: `us-west-2`) |
| `AWS_ACCESS_KEY_ID` | Yes* | Your AWS access key (*if enabled) |
| `AWS_SECRET_ACCESS_KEY` | Yes* | Your AWS secret key (*if enabled) |
| `PINECONE_ENABLED` | No | Enable Pinecone vector DB (`true`/`false`) |
| `PINECONE_API_KEY` | Yes* | Your Pinecone API key (*if Pinecone enabled) |
| `PINECONE_ENVIRONMENT` | Yes* | Pinecone environment (e.g., `us-east-1-aws`) |
| `PINECONE_INDEX_PRIMARY` | Yes* | Primary Pinecone index name |
| `PINECONE_INDEX_DR` | Yes* | DR Pinecone replica index name |
| `POSTGRESQL_ENABLED` | Yes | Enable PostgreSQL monitoring (`true`/`false`) |
| `POSTGRES_PRIMARY_HOST` | Yes* | Primary RDS endpoint (*if PostgreSQL enabled) |
| `POSTGRES_PRIMARY_PORT` | No | Primary database port (default: `5432`) |
| `POSTGRES_PRIMARY_DB` | Yes* | Primary database name |
| `POSTGRES_PRIMARY_USER` | Yes* | Primary database username |
| `POSTGRES_PRIMARY_PASSWORD` | Yes* | Primary database password |
| `POSTGRES_DR_HOST` | Yes* | DR RDS endpoint (*if PostgreSQL enabled) |
| `POSTGRES_DR_PORT` | No | DR database port (default: `5432`) |
| `POSTGRES_DR_DB` | Yes* | DR database name |
| `POSTGRES_DR_USER` | Yes* | DR database username |
| `POSTGRES_DR_PASSWORD` | Yes* | DR database password |
| `ROUTE53_HOSTED_ZONE_ID` | Yes* | Route 53 hosted zone ID for DNS failover |
| `ROUTE53_DOMAIN` | Yes* | Domain name for RAG system (e.g., `rag.yourcompany.com`) |
| `PAGERDUTY_ENABLED` | No | Enable PagerDuty alerts (`true`/`false`) |
| `PAGERDUTY_INTEGRATION_KEY` | Yes* | PagerDuty integration key (*if enabled) |

**Note**: Variables marked with * are required only if the corresponding service is enabled.

---

## Usage

### Run API Server

**Windows PowerShell:**
```powershell
.\scripts\run_api.ps1
```

**Manual (Linux/Mac):**
```bash
export PYTHONPATH=$PWD
export AWS_ENABLED=true
export POSTGRESQL_ENABLED=true
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Run Tests

**Windows PowerShell:**
```powershell
.\scripts\run_tests.ps1
```

**Manual:**
```bash
export PYTHONPATH=$PWD
pytest -v tests/
```

### Use Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M10_Financial_RAG_Production.ipynb
```

The notebook provides an interactive walkthrough of all DR concepts, replication monitoring, and failover orchestration.

---

## API Endpoints

### `GET /health`

Health check endpoint showing service availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T14:00:00Z",
  "services": {
    "aws": true,
    "pinecone": false,
    "postgresql": true,
    "dr_monitoring": true
  }
}
```

### `GET /replication/status`

Check current replication lag and status between primary and DR regions.

**Response:**
```json
{
  "lag_seconds": 5.2,
  "is_connected": true,
  "last_sync_time": "2024-12-15T13:59:55Z",
  "data_consistency_ratio": 0.998,
  "meets_rpo": true
}
```

### `GET /dr/readiness`

Verify DR region readiness for failover (pre-flight checks).

**Response:**
```json
{
  "ready": true,
  "issues": [],
  "replication_lag_seconds": 5.2,
  "data_consistency": 0.998,
  "meets_rpo": true,
  "timestamp": "2024-12-15T14:00:00Z"
}
```

### `POST /dr/failover`

**⚠️ CRITICAL OPERATION**: Execute automated failover to DR region.

**Request:**
```json
{
  "reason": "Primary region hard drive failure",
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "rto_minutes": 8.5,
  "data_loss_minutes": 5.0,
  "timestamp": "2024-12-15T09:35:00Z",
  "errors": []
}
```

### `POST /compliance/report`

Generate FINRA Rule 4370 quarterly compliance report.

**Request:**
```json
{
  "test_date": "2024-12-15T14:00:00Z",
  "include_details": true
}
```

**Response:**
```json
{
  "report_type": "FINRA Rule 4370 Quarterly DR Test",
  "test_date": "2024-12-15T14:00:00Z",
  "quarter": "2024-Q4",
  "rto_analysis": {
    "measured_minutes": 8.5,
    "target_minutes": 15,
    "pass": true,
    "status": "✅ PASS"
  },
  "rpo_analysis": {
    "measured_minutes": 5.0,
    "target_minutes": 60,
    "pass": true,
    "status": "✅ PASS"
  },
  "overall_result": {
    "pass": true,
    "status": "✅ TEST PASSED"
  }
}
```

### `GET /metrics/rto`

Get RTO (Recovery Time Objective) target and historical performance.

**Response:**
```json
{
  "rto_target_minutes": 15,
  "description": "Maximum acceptable downtime during market hours",
  "regulatory_basis": "FINRA Rule 4370 - Business Continuity Planning",
  "typical_performance": "8-12 minutes"
}
```

### `GET /metrics/rpo`

Get RPO (Recovery Point Objective) target and current lag.

**Response:**
```json
{
  "rpo_target_minutes": 60,
  "description": "Maximum acceptable data loss measured in time",
  "regulatory_basis": "SOX Section 404 - Document retention",
  "current_lag_seconds": 5.2,
  "meets_rpo": true
}
```

---

## Decision Card

### When to Use Hot DR for Financial RAG

✅ **Required Conditions:**

1. **System serves trading operations during market hours** (9:30 AM - 4:00 PM ET)
2. **Portfolio managers use system for billion-dollar trading decisions**
3. **System is critical to material trading decision rationale**
4. **Regulatory requirement**: FINRA Rule 4370 mandates business continuity capability
5. **Market-hours downtime creates unacceptable financial loss** (₹30K+/hour)

✅ **Cost Justification:**

- Hot DR monthly cost: ₹2.5L (~$3,000 USD)
- One 4-hour downtime cost: ₹1.2Cr+ direct losses + regulatory fines + reputation damage
- **Break-even**: Hot DR pays for itself if prevents ONE major outage every 4 years
- Given typical hardware failure rates (1-2 major incidents per decade), this is highly likely

### When NOT to Use Hot DR

❌ **Acceptable Alternatives (Warm/Cold DR):**

1. **Compliance research** (evening work only, no market-hours requirement)
2. **Historical analysis** (weekend reports only, 2-4 hour recovery acceptable)
3. **Training data preparation** (overnight jobs, no time sensitivity)
4. **Non-trading-hours systems** where business impact of downtime is low
5. **Internal tools** not subject to FINRA examination

❌ **Critical Exception:**

> "If your RAG system is only used outside market hours (9:30 AM - 4:00 PM ET), you might justify Warm DR. But if portfolio managers use your system during market hours - even occasionally - you need Hot DR. No exceptions."

### Regulatory Compliance - Non-Negotiable Driver

**FINRA Rule 4370 Requirements:**

- Create business continuity plans (BCP)
- **Test the BCP at least annually** (industry practice: quarterly)
- Document test results with RTO/RPO measurements
- Demonstrate ability to resume operations "as soon as possible"

> "If your DR plan is 'restore from backups in 4 hours' and your system is critical to trading operations, FINRA will ask: 'Why does restoration take 4 hours when competitors achieve 15 minutes?' You cannot pass FINRA examination with Warm DR for trading-critical systems. Hot DR is table stakes."

### Cost Tiers

**Small Deployment** (10K documents, 100 queries/day):
- Monthly DR cost: ₹80K (~$1,000 USD)
- Primary: t3.small RDS, 1-pod Pinecone, 1 EC2 instance
- DR: Matching infrastructure
- Justification: Even small systems need Hot DR if trading-critical

**Medium Deployment** (100K documents, 1K queries/day):
- Monthly DR cost: ₹2.5L (~$3,000 USD)
- Primary: t3.medium RDS, Production Pinecone, 2-4 EC2 instances
- DR: Matching infrastructure (implementation in this module)
- Justification: Standard for institutional trading desks

**Large Deployment** (1M+ documents, 10K+ queries/day):
- Monthly DR cost: ₹8L (~$10,000 USD)
- Primary: r5.xlarge RDS, Enterprise Pinecone, 10+ EC2 instances
- DR: Matching infrastructure with additional cross-region bandwidth
- Justification: Enterprise broker-dealers with multiple trading desks

---

## Common Failures & Fixes

### Failure 1: Replication Lag Exceeds RPO

**Symptoms:**
- PostgreSQL replication lag > 60 minutes
- Pinecone index sync taking > 2 hours
- CloudWatch metrics show lag spike during heavy document ingestion

**Root Causes:**
- Network congestion between regions during bulk data loads
- Primary database CPU/disk saturation preventing fast writes
- Insufficient bandwidth on replication link
- Large transactions (thousands of documents) blocking replication pipeline

**Fixes:**
1. **Implement backpressure**: Batch document ingestion into smaller chunks (≤500 documents per batch with 5-second delays)
2. **Upgrade RDS instance**: t3.medium → t3.large to handle replication overhead
3. **Create dedicated replication user**: Optimized connection pooling with pgBouncer
4. **Monitor lag continuously**: Set CloudWatch alarm at 5-minute threshold (well before 1-hour RPO violation)
5. **Reduce IOPS-intensive operations**: During bulk ingestion windows in primary region

### Failure 2: DR Database Promotion Takes > 15 Minutes

**Symptoms:**
- During test failover, promoting read replica takes 8+ minutes
- Database schema changes fail during promotion
- Uncontrolled downtime during promotion procedure

**Root Causes:**
- Large number of WAL (write-ahead log) files requiring replay
- Blocking transactions holding locks during promotion
- Manual promotion steps instead of automated scripting
- Insufficient testing of promotion procedure

**Fixes:**
1. **Pre-script entire promotion**: `aws rds promote-read-replica` with all parameters pre-configured
2. **Kill idle connections**: On replica 1 minute before promotion (prevents lock holding)
3. **Test promotion quarterly**: As part of FINRA compliance testing
4. **Document and automate**: Each step in Lambda function
5. **Typical result**: Promotion time 1-2 minutes (meets RTO)

### Failure 3: DNS Failover Doesn't Trigger

**Symptoms:**
- Primary region down, but traffic not redirecting to DR
- Route 53 health checks show primary down, but DNS still points to primary
- Clients continue trying to reach failed region

**Root Causes:**
- Route 53 health checks misconfigured (checking wrong endpoint)
- Health check not testing application health (testing instance availability, not RAG responsiveness)
- DNS TTL too high (clients cache stale DNS for hours)
- Failover policy not configured correctly in Route 53

**Fixes:**
1. **Health check must test actual RAG endpoint**: `GET /health` returning JSON with status
2. **Set CloudWatch alarm**: Trigger Route 53 failover ONLY if health check fails for 90+ seconds (prevents flapping)
3. **Configure Route 53 TTL = 60 seconds**: Ensures rapid DNS propagation to DR
4. **Test failover procedure**: Manually kill primary region application → verify DNS switches within 2 minutes
5. **Document manual runbook**: For manual failover if automated Route 53 fails

### Failure 4: DR Region Data Corruption After Failover

**Symptoms:**
- After failover, DR region serving stale/incorrect document embeddings
- Search results diverging between primary and DR (during normal replication)
- Data consistency check shows > 1% discrepancy

**Root Causes:**
- Replication lag caused some documents to be in primary but not DR at time of failure
- Concurrent writes to primary during replication catch-up period
- Pinecone replica index not fully synchronized before promotion
- Insufficient data validation before switching DNS

**Fixes:**
1. **Pre-failover verification**: Compare record counts between primary and DR (expect < 1% difference)
2. **Don't failover if lag > 10 minutes**: Wait for catch-up or accept data loss
3. **Post-failover validation**: Run sample queries on DR, compare results to pre-failure baseline
4. **Keep failover window log**: Document exactly what data was in-flight during failure (for SOX audit trail)
5. **Plan 30-minute reconciliation window**: Post-failover to catch any inconsistencies

### Failure 5: Cost Blowout from Dual Infrastructure

**Symptoms:**
- Monthly AWS bill doubles from ₹1.2L to ₹2.5L, catching business off guard
- No cost optimization between regions
- Idle DR instances running at full capacity continuously

**Root Causes:**
- Running t3.medium instances in both regions 24/7 (only primary needs full capacity)
- No resource scaling strategy (DR should scale down during non-business hours)
- Pinecone Production tier expensive for DR that's mostly idle

**Fixes:**
1. **Implement auto-scaling**: DR region runs minimum 1 instance, scales to match primary only during failover
2. **Schedule downscaling**: After-hours (8 PM - 6 AM), reduce DR to single t3.small instance
3. **Monitor cross-region data transfer**: Can be $1K+/month
4. **Use Reserved Instances**: For primary region (1-year commitment saves 30%), Spot Instances for DR (temporary surge capacity)
5. **Optimized cost**: ₹1.8L/month (instead of ₹2.5L)

### Failure 6: Quarterly DR Test Doesn't Meet FINRA Requirements

**Symptoms:**
- FINRA examiner asks to see DR test documentation - team has none
- RTO measured at 22 minutes, but requirements say 15 minutes
- No written procedure, just "wing it" during disasters

**Root Causes:**
- No documented test procedure
- Test metrics not being recorded
- Confusion about what FINRA actually requires
- Test never actually executed end-to-end

**Fixes:**
1. **Create formal DR Test Plan document**: Test objectives, expected RTO/RPO, success criteria, rollback procedure
2. **Execute test quarterly**: Trigger failover in staging environment (don't risk production)
3. **Document results**: Timestamp of failure detection, time to failover completion, final RTO measured
4. **Measure RPO**: Compare row count in primary vs. DR at time of failover, calculate data loss
5. **Generate compliance report**: "Q4 2024 DR Test: RTO = 9 minutes (target 15) ✅, RPO = 3 min (target 60) ✅"
6. **File report with compliance team**: For auditor review

---

## Alternative Solutions

### Alternative 1: Warm DR Instead of Hot DR

**How It Works:**
Minimal infrastructure running in DR region; scale up on demand during failure. Backup database snapshots taken hourly, restore from latest snapshot during disaster.

**Pros:**
- **Cost**: Only ~40% of primary infrastructure cost (instead of 100%)
- **Simpler operational burden**: Fewer always-on systems to manage

**Cons:**
- **RTO = 2-4 hours** (unacceptable for trading systems)
- **Requires manual intervention** to promote and scale
- **FINRA will challenge** 2-4 hour RTO as inadequate for trading-critical systems
- **Data loss**: Up to 1 hour (if snapshot taken on hourly schedule)

**When Appropriate:**
Non-trading-hours use cases, compliance research, historical analysis, overnight batch jobs. **NOT for market-hours trading support.**

### Alternative 2: Multi-Cloud DR (AWS Primary, Azure DR)

**How It Works:**
Primary RAG system in AWS US-EAST-1. DR region runs in Microsoft Azure (East US region). Data replicated across cloud providers.

**Pros:**
- **Provider risk mitigation**: AWS outage doesn't impact Azure
- **Different infrastructure**: Reduces systemic risk
- **Regulatory appeal**: "We're protected against AWS regional failure"

**Cons:**
- **Significant complexity**: Different APIs, authentication, monitoring systems
- **Higher cost**: Each cloud has own infrastructure costs, plus inter-cloud data transfer (~$0.02/GB)
- **Operational burden**: Team needs expertise in both AWS and Azure
- **Testing complexity**: DR test requires cross-cloud failover orchestration
- **Latency**: Cross-cloud replication can introduce additional lag

**When Appropriate:**
Only if you require protection against single-cloud provider failure. Most financial institutions accept AWS redundancy (multi-AZ, multi-region within AWS). Multi-cloud adds cost/complexity without proportional risk reduction for most use cases.

### Alternative 3: Active-Active Deployment (No Primary/DR Distinction)

**How It Works:**
Both regions actively serving traffic simultaneously. Users routed to nearest region; both regions can accept writes; replication in both directions.

**Pros:**
- **Zero downtime**: During region failure (other region already serving traffic)
- **No "switchover" required**: No RTO - system never goes down
- **Better load distribution**: Geographic proximity improves latency

**Cons:**
- **Extreme complexity**: Two-way replication with conflict resolution
- **Data consistency challenges**: Writes in both regions simultaneously can conflict
- **Pinecone limitation**: Doesn't support true multi-master replication (only primary → replica)
- **Financial impact**: Running full infrastructure in both regions 24/7 (no cost savings, only higher cost)
- **Regulatory complexity**: Testing becomes harder (have to verify both regions running in parallel)

**When Appropriate:**
**Not recommended for financial RAG.** Pinecone doesn't support write-write replication needed. Complexity/cost not justified vs. Hot DR with fast failover.

---

## Project Structure

```
fai_m10_v4/
├── app.py                              # FastAPI entrypoint (HTTP API)
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # API key template
├── .gitignore                          # Python defaults + notebooks
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample JSON test data
├── example_data.txt                    # Sample text test scenarios
│
├── src/                                # Source code package
│   └── l3_m10_financial_rag_production/
│       └── __init__.py                 # Core DR business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M10_Financial_RAG_Production.ipynb
│
├── tests/                              # Test suite
│   └── test_m10_financial_rag_production.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample DR config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

---

## Contributing

Pull requests welcome! Please:
1. Follow existing code style (type hints, docstrings)
2. Add tests for new functionality
3. Update README with new configuration requirements
4. Ensure all tests pass before submitting

---

## License

MIT License - see LICENSE file for details.

---

## Resources

- **Script**: [Augmented FinanceAI M10.4 - Disaster Recovery & Business Continuity](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_FinanceAI_M10_4_DisasterRecovery_BusinessContinuity.md)
- **FINRA Rule 4370**: [Business Continuity Plans and Emergency Contact Information](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4370)
- **SOX Section 404**: [Internal Control Assessment](https://www.sec.gov/spotlight/sarbanes-oxley.htm)
- **AWS RDS Multi-AZ**: [High Availability Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- **Pinecone Production Tier**: [Cross-Region Replication](https://docs.pinecone.io/)
- **Route 53 DNS Failover**: [Health Checks and Failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)

---

**Module**: L3 M10.4: Disaster Recovery & Business Continuity
**Technology Stack**: AWS (CloudWatch, Route53, RDS), Pinecone, PostgreSQL
**Services Used**: AWS (boto3), Pinecone, PostgreSQL (psycopg2)
**Regulatory Compliance**: FINRA Rule 4370, SOX Section 404, GLBA

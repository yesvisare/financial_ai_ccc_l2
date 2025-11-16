# L3 M10.2: Monitoring Financial RAG Performance

> **Track:** Finance AI (Domain-Specific)
> **Module:** M10 - Financial RAG in Production
> **Video:** M10.2 - Monitoring Financial RAG Performance
> **Script:** [Augmented Script](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M10_2_Monitoring_Performance.md)

## Overview

In financial AI systems, traditional monitoring metrics like "uptime 99.9%" or "average latency 200ms" tell only part of the story. **This module demonstrates the critical gap between technical health and business outcomes** in finance—where monitoring systems can show "all green" while data is 18 hours stale, citations are inaccurate, or Material Non-Public Information (MNPI) is being leaked.

This production-ready monitoring system bridges that gap by tracking **six critical financial metrics** that matter to compliance officers, risk managers, and business stakeholders—not just DevOps teams.

## What You'll Learn

**Learning Objectives:**
- Understand the difference between infrastructure metrics and business-critical financial metrics
- Implement monitoring for **six critical financial RAG metrics** (citation accuracy, data staleness, MNPI detection, query latency, compliance violations, audit trail completeness)
- Build SOX 404 compliant audit trails with 7-year retention
- Design stakeholder-specific dashboards (CFO, CTO, Compliance Officer)
- Implement intelligent alert routing based on violation type
- Apply the "1% real-time sampling" strategy for citation verification
- Balance monitoring cost vs. risk in financial contexts

## Six Critical Financial Metrics

This module monitors **six metrics** that traditional monitoring misses:

### 1. **Citation Accuracy**
- **Definition:** "Of all citations provided, what percentage are actually from the correct document section?"
- **Target:** >95% accuracy
- **Business Impact:** Incorrect citations in financial advice can lead to compliance violations, regulatory penalties, and loss of client trust
- **Implementation:** 1% real-time sampling strategy (balances accuracy monitoring with performance)

### 2. **Data Staleness**
- **Definition:** Hours since last update, with source-specific SLA thresholds
- **SLA Thresholds:**
  - Bloomberg Terminal: <5 minutes
  - SEC EDGAR: <24 hours
  - Internal Financial Models: <1 hour
  - Real-time Market Data: <5 minutes
  - Research Reports: <24 hours
- **Business Impact:** Stale data in trading decisions can result in multi-million dollar losses
- **Alert Routing:** Data engineering on-call

### 3. **MNPI Detection Counts**
- **Definition:** "Material Non-Public Information blocks" tracking for Regulation FD compliance
- **Target:** Zero tolerance for MNPI leaks
- **Business Impact:** SEC violations, criminal charges, firm reputation damage
- **Alert Routing:** Compliance officer (immediate escalation)

### 4. **Query Latency**
- **Definition:** p95 query latency (95th percentile response time)
- **Target:** <2 seconds for analyst workflow
- **Business Impact:** Slow queries disrupt time-sensitive trading decisions
- **Metric Type:** Histogram (buckets: 0.1s - 10s)

### 5. **Compliance Violation Count**
- **Definition:** Count of all compliance violations (MNPI, privilege breaches, export control)
- **Target:** Zero tolerance
- **Business Impact:** Regulatory penalties, legal liability, license revocation
- **Alert Routing:** CFO + CTO + Compliance officer (all three for critical violations)

### 6. **Audit Trail Completeness**
- **Definition:** Percentage of queries with complete audit logs
- **Target:** 100% (SOX 404 requirement)
- **Business Impact:** Failed audits, regulatory non-compliance, potential delisting
- **Retention:** 7 years (S3/Glacier storage)

## How It Works

### Four-Layer Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Compliance & Audit                                │
│  - SOX 404 audit logs (7-year retention)                    │
│  - Compliance report generation                             │
│  - CFO/CTO/Compliance dashboards                            │
└─────────────────────────────────────────────────────────────┘
                           ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Financial Domain Metrics                          │
│  - Citation accuracy (1% sampling)                          │
│  - Data staleness (per-source SLAs)                         │
│  - MNPI detection (keyword + pattern matching)             │
└─────────────────────────────────────────────────────────────┘
                           ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Application Metrics                               │
│  - Query latency (p95 <2s SLA)                             │
│  - Error rates                                              │
│  - LLM token usage                                          │
└─────────────────────────────────────────────────────────────┐
                           ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Infrastructure Metrics                            │
│  - Kubernetes health                                        │
│  - Database connections                                     │
│  - CPU/Memory utilization                                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Tool | Purpose | Cost Estimate |
|-----------|------|---------|---------------|
| Metrics Collection | Prometheus | Time-series metrics storage | $40/month |
| Visualization | Grafana | Stakeholder dashboards | $30/month |
| Alerting | PagerDuty | Intelligent alert routing | $40/month |
| Audit Storage | S3/Glacier | 7-year retention (SOX 404) | $20/month |
| Metadata | PostgreSQL | Query audit metadata | Free (RDS) |

**Total Estimated Cost:** ~$130 USD/month for 50-user investment bank

### Alert Escalation Logic

Different violations require different responses:

| Violation Type | Escalation Path | Response Time |
|----------------|-----------------|---------------|
| Data Staleness SLA Breach | Data Engineering → On-Call | 15 minutes |
| MNPI Detection Spike | Compliance Officer | Immediate |
| Citation Accuracy <95% | Data Science Lead | 1 hour |
| Infrastructure Degradation | SRE On-Call | 5 minutes |
| Critical Compliance Violation | CFO + CTO + Compliance | Immediate (all three) |

## Prerequisites

```bash
pip install -r requirements.txt
```

**Environment Variables (Optional):**

For local development, the system works offline without any external services. To enable cloud integrations:

```bash
cp .env.example .env
# Edit .env and configure (all optional):
PROMETHEUS_ENABLED=true
PAGERDUTY_ENABLED=true
AWS_S3_ENABLED=true
```

## Quick Start

### 1. Run Tests

```powershell
.\scripts\run_tests.ps1
```

### 2. Start API

```powershell
.\scripts\run_api.ps1
```

API will be available at: **http://localhost:8000**

Interactive API docs: **http://localhost:8000/docs**

### 3. Interactive Notebook

```bash
jupyter notebook notebooks/L3_M10_Financial_RAG_In_Production.ipynb
```

## Usage Examples

### Track a RAG Query

```python
from src.l3_m10_financial_rag_in_production import (
    FinancialRAGMonitor,
    DataSource
)

# Initialize monitor
monitor = FinancialRAGMonitor()

# Track a query
result = monitor.track_query(
    query="What is Apple's latest earnings guidance?",
    response="Apple's Q4 2024 guidance indicates revenue of $90-92B...",
    citations=[
        {"source": "SEC_EDGAR_AAPL_10Q_2024Q4", "page": 12, "quote": "Revenue guidance $90-92B"},
        {"source": "Bloomberg_AAPL", "page": 1, "quote": "EPS estimate $1.35"}
    ],
    data_sources=[DataSource.SEC_EDGAR, DataSource.BLOOMBERG]
)

# Result includes:
# - Latency measurement
# - Compliance check (MNPI, privilege, export control)
# - Citation verification (1% sampling)
# - Audit log ID
print(result)
# {'status': 'success', 'latency_seconds': 0.145,
#  'compliance': {'passed': True, 'violations': []},
#  'citations': {'sampled': True, 'accuracy': 100.0},
#  'audit_log_id': 'a3f2e1b9c4d5'}
```

### Check Data Staleness

```python
# Check Bloomberg data freshness
staleness = monitor.check_data_staleness(DataSource.BLOOMBERG)

print(staleness)
# {'source': 'Bloomberg Terminal',
#  'hours_since_update': 0.03,  # ~2 minutes
#  'sla_threshold_hours': 0.083,  # 5 minutes
#  'is_stale': False,
#  'status': 'OK'}
```

### Generate Compliance Report

```python
from datetime import datetime, timedelta

# Generate 30-day SOX 404 compliance report
report = monitor.generate_compliance_report(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)

print(report['sla_compliance'])
# {'citation_accuracy': True,   # >95%
#  'p95_latency': True,          # <2 seconds
#  'zero_violations': True}      # No compliance violations
```

### Get Metrics Summary

```python
# Get current metrics (Prometheus-compatible)
metrics = monitor.metrics_collector.get_metrics_summary()

print(metrics)
# {'successful_queries': 1523,
#  'failed_queries': 7,
#  'mnpi_detections': 0,
#  'compliance_violations': 0,
#  'citation_accuracy_percent': 97.2,
#  'p95_latency_seconds': 1.85,
#  'data_staleness': {...},
#  'audit_log_count': 1530}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health with metrics summary |
| `/track_query` | POST | Track RAG query with full monitoring |
| `/check_staleness` | POST | Check data staleness for specific source |
| `/compliance_report` | POST | Generate SOX 404 compliance report |
| `/metrics` | GET | Get current metrics (Prometheus format) |
| `/audit_logs` | GET | Retrieve audit logs (7-year retention) |
| `/data_sources` | GET | List supported data sources + SLAs |

### Example API Call

```bash
curl -X POST "http://localhost:8000/track_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Tesla Q3 revenue?",
    "response": "Tesla Q3 2024 revenue was $23.4B...",
    "citations": [{"source": "SEC_EDGAR_TSLA_10Q", "page": 8, "quote": "Revenue $23.4B"}],
    "data_sources": ["SEC_EDGAR"]
  }'
```

## Decision Card

### When to Use This Monitoring Approach

| Criterion | This Approach (Financial RAG) | Standard Monitoring | Lightweight Logging |
|-----------|------------------------------|---------------------|---------------------|
| **Compliance Requirements** | SOX 404, Regulation FD, MNPI | GDPR, basic audit | None |
| **Citation Accuracy SLA** | >95% (financial liability) | N/A | N/A |
| **Data Staleness Impact** | Multi-million dollar losses | Moderate | Low |
| **Audit Retention** | 7 years (regulatory) | 1-3 years | Days/weeks |
| **Estimated Monthly Cost** | $130 (50 users) | $50 | $10 |
| **Alert Escalation** | Role-based (CFO/Compliance) | Engineering only | Email alerts |

### Use This Approach When:
- Operating in **regulated financial environments** (investment banks, hedge funds, financial advisors)
- **Regulatory compliance** is non-negotiable (SOX 404, Regulation FD, FINRA rules)
- **Citation accuracy failures** have legal/financial liability
- **Data staleness** can lead to multi-million dollar trading losses
- **Audit trails** must be maintained for 7+ years
- **Stakeholder dashboards** needed for CFO, CTO, Compliance Officer roles

### Do NOT Use This Approach When:
- Building consumer-facing chatbots with no financial liability
- Operating in non-regulated industries
- Budget constraints prevent $130/month monitoring cost
- Team lacks DevOps/SRE expertise for Prometheus/Grafana
- RAG system handles non-sensitive, non-financial queries
- Citation accuracy is "nice to have" not "legally required"

## Common Failures & Solutions

| Failure | Symptom | Root Cause | Solution |
|---------|---------|------------|----------|
| **"All Green" But Stale Data** | Dashboards show 99.9% uptime, but analyst receives 18-hour-old Bloomberg data | Monitoring infrastructure health, not data freshness | Implement Layer 3 monitoring (data staleness gauges per source) |
| **MNPI Leak Detected Post-Factum** | Compliance team discovers MNPI leak during manual quarterly review | No real-time MNPI detection in RAG pipeline | Add `_check_compliance()` with keyword + pattern matching for every query response |
| **Citation Failures Unnoticed** | Clients receive responses with incorrect citations, caught in manual QA | No automated citation verification | Implement 1% real-time sampling with `_verify_citations()` |
| **Alert Fatigue** | Engineers ignore PagerDuty alerts because 90% are false positives | All alerts routed to same on-call rotation | Intelligent alert routing: staleness→data eng, MNPI→compliance, infra→SRE |
| **Audit Trail Gaps** | Failed SOX 404 audit due to missing query logs for 3 days during outage | Audit logs stored in same database that went down | Separate audit storage (S3/Glacier with cross-region replication) |
| **p95 Latency SLA Breach** | Average latency looks fine (0.3s), but 5% of queries take >10 seconds | Monitoring mean instead of p95 | Use Prometheus histograms with percentile queries, not averages |
| **Cost Overruns** | Monitoring costs balloon to $5000/month | Over-provisioned Grafana Cloud, storing all raw queries | Use 1% sampling, store only hashes (not raw queries), leverage S3 Glacier for cold storage |

## Alternative Solutions

### 1. **DataDog APM + Custom Metrics**
- **Trade-offs:** More expensive ($300+/month), but includes full APM, log aggregation, and out-of-box financial integrations
- **When to use:** If already using DataDog for infrastructure monitoring
- **When NOT to use:** Budget-constrained teams, need for on-premise deployment

### 2. **ELK Stack (Elasticsearch, Logstash, Kibana)**
- **Trade-offs:** More flexible querying, higher operational overhead (need to manage Elasticsearch cluster)
- **When to use:** If team already has ELK expertise, need complex log analysis
- **When NOT to use:** Small teams without dedicated DevOps, prefer managed services

### 3. **AWS CloudWatch + Lambda**
- **Trade-offs:** Fully managed (lower operational overhead), but vendor lock-in and higher cost for high-volume metrics
- **When to use:** AWS-native deployments, serverless architectures
- **When NOT to use:** Multi-cloud environments, need for Prometheus compatibility

### 4. **Splunk Enterprise**
- **Trade-offs:** Enterprise-grade features (advanced correlation, AI anomaly detection), very expensive ($$$)
- **When to use:** Large financial institutions with dedicated compliance teams
- **When NOT to use:** Startups, mid-size firms, cost-sensitive projects

### 5. **Custom Logging to PostgreSQL**
- **Trade-offs:** Simplest approach (just INSERT queries), but no built-in dashboards or alerting
- **When to use:** MVP/proof-of-concept, minimal compliance requirements
- **When NOT to use:** Production systems, need for real-time alerting

## Project Structure

```
fai_m10_v2/
├── app.py                              # FastAPI entrypoint
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Python defaults
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample queries
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m10_financial_rag_in_production/
│       └── __init__.py                 # Core business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M10_Financial_RAG_In_Production.ipynb
│
├── tests/                              # Test suite
│   └── test_m10_financial_rag_in_production.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

## Testing

```bash
# Run all tests
pytest tests/test_m10_financial_rag_in_production.py -v

# Run with coverage
pytest --cov=src tests/ --cov-report=html
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Resources

- **Script:** [Augmented Finance AI M10.2 Script](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M10_2_Monitoring_Performance.md)
- **TechVoyageHub Course:** Finance AI Track
- **Prometheus Documentation:** https://prometheus.io/docs/
- **Grafana Dashboards:** https://grafana.com/grafana/dashboards/
- **SOX 404 Compliance:** https://www.sec.gov/spotlight/sarbanes-oxley.htm
- **Regulation FD:** https://www.sec.gov/rules/final/33-7881.htm

## Support

For issues, questions, or feature requests, please open an issue in the GitHub repository.

---

**Built with PractaThon™ standards for production-ready financial AI systems.**

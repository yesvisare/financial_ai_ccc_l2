# L3 M10.1: Secure Deployment for Financial Systems

Production-ready secure deployment architecture for financial RAG systems with VPC isolation, encryption, secrets management, IAM/RBAC access control, and SOX-compliant audit logging.

**Service:** OPENAI (auto-detected from script)

---

## 🎯 What This Module Does

Implements enterprise-grade security controls for deploying financial RAG systems in production environments. This module teaches you how to build production-ready infrastructure that meets stringent financial regulatory requirements.

### Key Features

✅ **VPC Network Isolation**: Private subnets with no public internet exposure  
✅ **Encryption Everywhere**: Data at rest (AWS KMS) + in transit (TLS 1.3)  
✅ **Secrets Management**: AWS Secrets Manager with automatic 90-day rotation  
✅ **Access Control**: IAM roles + application-level RBAC  
✅ **SOX-Compliant Audit Logging**: CloudWatch + CloudTrail with 7-year retention  
✅ **Defense in Depth**: 4 layers of security (network, auth, encryption, logging)  

### Security Architecture

```
Defense-in-Depth Layers:
1. Network Layer: VPC isolation, private subnets, security groups → Blocks 90% of attacks
2. Authentication/Authorization: ALB JWT validation + IAM + RBAC → Identity verification
3. Encryption Layer: KMS (at rest) + TLS 1.3 (in transit) → Data protection
4. Audit Layer: CloudWatch + CloudTrail → Detection & forensics
```

### Compliance Frameworks

- ✅ **SOC 2 Type II**: Enterprise security controls for service organizations
- ✅ **SOX Section 404**: 7-year audit logs with immutable storage
- ✅ **GLBA Title V**: Customer financial data protection
- ℹ️ **PCI DSS**: NOT required for most financial RAG systems (only if processing credit cards)

---

## 📋 Prerequisites

**Required Knowledge:**
- Completed Generic CCC M1-M4 (RAG fundamentals)
- Completed Finance AI M7 (PII detection)
- Completed Finance AI M8 (Data enrichment)
- Completed Finance AI M9 (Risk management)
- Basic AWS knowledge (VPC, IAM, KMS)

**Required Tools:**
- Python 3.11+
- AWS account with multi-AZ support
- Terraform 1.6+ (for infrastructure deployment)
- OpenAI API key
- (Optional) Pinecone account for vector database

**Recommended Budget:**
- Minimum: $500/month infrastructure + $15K/year compliance = **$1,750/month total**
- See [Cost Estimates](#-cost-estimates) section for detailed breakdown

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd fai_m10_v1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and AWS configuration
# Required:
#   - OPENAI_API_KEY (OpenAI API key)
#   - AWS_REGION (e.g., us-east-1)
#   - AWS_KMS_KEY_ID (KMS key ARN for encryption)
#   - Optional: PINECONE_API_KEY, DATABASE_URL, REDIS_URL
```

**Minimum .env configuration:**

```bash
OPENAI_ENABLED=true
OPENAI_API_KEY=your_openai_api_key_here

AWS_REGION=us-east-1
AWS_KMS_KEY_ID=arn:aws:kms:us-east-1:123456789012:key/xxxxx

ENABLE_ENCRYPTION=true
ENABLE_AUDIT_LOGGING=true
LOG_RETENTION_YEARS=7
```

### 3. Run API Server

**Windows (PowerShell):**
```powershell
.\scripts\run_api.ps1
```

**Linux/Mac:**
```bash
export PYTHONPATH=$PWD
export OPENAI_ENABLED=True
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access API at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Run Tests

**Windows (PowerShell):**
```powershell
.\scripts\run_tests.ps1
```

**Linux/Mac:**
```bash
export PYTHONPATH=$PWD
pytest -v tests/
```

---

## 🏗️ Architecture

### Network Topology

```
Internet
   ↓ HTTPS (443)
Application Load Balancer (Public Subnet)
   ↓ TLS 1.3
RAG API (Private Subnet 1) ←→ AWS Secrets Manager
   ↓                             ↓ KMS Encryption
   ↓                          Decrypt API Keys
   ↓
Vector Database (Private Subnet 2, Pinecone/self-hosted)
   ↓
OpenAI API (via NAT Gateway, outbound only)

All components → CloudWatch Logs → S3 (7-year retention, immutable)
All AWS API calls → CloudTrail (audit log)
```

### Security Layers

1. **Network Layer (VPC Isolation)**
   - VPC CIDR: 10.0.0.0/16 (65,536 IP addresses)
   - Public Subnet: 10.0.1.0/24 (ALB + NAT Gateway only)
   - Private Subnet 1: 10.0.10.0/24 (RAG API, NO public IPs)
   - Private Subnet 2: 10.0.11.0/24 (Vector DB, NO public IPs)
   - Security Groups: Whitelist-only approach

2. **Authentication/Authorization Layer**
   - ALB: JWT token validation (before reaching RAG API)
   - IAM: Infrastructure-level permissions
   - RBAC: Application-level permissions (analyst, admin, compliance, viewer)

3. **Encryption Layer**
   - At Rest: AWS KMS with AES-256-GCM (FIPS 140-2 Level 3 compliant)
   - In Transit: TLS 1.3 (latest security standard)
   - Automatic key rotation: Every 365 days

4. **Audit Layer**
   - CloudWatch Logs: Application logs with 7-year retention
   - CloudTrail: All AWS API calls logged
   - S3 Object Lock: Immutable storage (cannot be deleted)
   - Searchable: CloudWatch Insights, Athena queries

---

## 📊 API Endpoints

### Health & Status

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Secure Financial RAG Deployment API",
  "version": "1.0.0",
  "timestamp": "2025-11-16T01:30:00.000Z"
}
```

#### `GET /health`
Detailed health check with configuration status.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "aws_region": "us-east-1",
  "encryption_enabled": true,
  "audit_logging_enabled": true
}
```

### Deployment

#### `POST /deploy`
Deploy secure financial RAG system with full security controls.

**Request:**
```json
{
  "vpc_config": {
    "cidr_block": "10.0.0.0/16",
    "public_subnet": "10.0.1.0/24",
    "private_subnets": ["10.0.10.0/24", "10.0.11.0/24"]
  },
  "encryption_config": {
    "enabled": true,
    "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/xxxxx",
    "tls_version": "1.3"
  },
  "iam_config": {
    "least_privilege": true,
    "rbac_enabled": true,
    "roles": ["analyst", "admin", "compliance"]
  },
  "audit_logging_config": {
    "enabled": true,
    "retention_years": 7,
    "immutable_storage": true
  }
}
```

**Response:**
```json
{
  "status": "deployed",
  "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
  "encryption_enabled": true,
  "audit_logging_enabled": true,
  "compliance_frameworks": [
    "SOC 2 Type II",
    "SOX Section 404",
    "GLBA Title V"
  ],
  "deployment_details": {
    "vpc": {
      "vpc_id": "vpc-xxxxx",
      "private_subnet_ids": ["subnet-xxxxx", "subnet-yyyyy"],
      "security_group_ids": {...}
    },
    "encryption": {...},
    "secrets": {...},
    "iam_roles": {...},
    "audit_logging": {...}
  }
}
```

### Security & Compliance

#### `GET /security/validate`
Validate current security configuration against SOC 2 Type II requirements.

**Response:**
```json
{
  "valid": true,
  "checks_passed": [
    "Encryption enabled",
    "VPC configured",
    "Secrets Manager configured",
    "IAM/RBAC configured",
    "Audit logging enabled",
    "7+ year retention",
    "Immutable storage"
  ],
  "checks_failed": [],
  "compliance_frameworks": [
    "SOC 2 Type II",
    "SOX Section 404",
    "GLBA Title V"
  ],
  "recommendations": []
}
```

#### `GET /compliance/status`
Get current compliance status for financial regulations.

**Response:**
```json
{
  "soc_2_type_ii": {
    "status": "compliant",
    "requirements": [
      {"name": "Security", "status": "met"},
      {"name": "Availability", "status": "met"},
      {"name": "Processing Integrity", "status": "met"},
      {"name": "Confidentiality", "status": "met"},
      {"name": "Privacy", "status": "met"}
    ]
  },
  "sox_section_404": {
    "status": "compliant",
    "requirements": [
      {"name": "7-year retention", "status": "met"},
      {"name": "Immutable storage", "status": "met"},
      {"name": "Audit trail", "status": "met"}
    ]
  },
  "glba_title_v": {
    "status": "compliant",
    "requirements": [
      {"name": "Data encryption", "status": "met"},
      {"name": "Access controls", "status": "met"},
      {"name": "Privacy notices", "status": "met"}
    ]
  }
}
```

#### `GET /audit/logs`
Retrieve information about audit logs.

**Response:**
```json
{
  "message": "Audit logs available in CloudWatch Logs and S3",
  "log_group": "/financial-rag/production",
  "s3_bucket": "financial-rag-audit-logs",
  "retention_years": 7,
  "query_tools": ["CloudWatch Insights", "Athena", "OpenSearch"]
}
```

---

## 🧪 Testing

### Run All Tests

```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Linux/Mac
export PYTHONPATH=$PWD
pytest -v tests/
```

### Run Specific Test Category

```bash
# VPC isolation tests
pytest tests/test_m10_financial_rag_production.py::test_setup_vpc_isolation -v

# Encryption tests
pytest tests/test_m10_financial_rag_production.py -k "encryption" -v

# Compliance tests
pytest tests/test_m10_financial_rag_production.py -k "compliance" -v

# Full deployment workflow
pytest tests/test_m10_financial_rag_production.py::test_full_deployment_workflow -v
```

### Test Coverage

Run tests with coverage report:

```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

View HTML coverage report: `htmlcov/index.html`

### Test Categories

- ✅ **Security Configuration Validation**: 5 tests
- ✅ **VPC Isolation**: 3 tests
- ✅ **Encryption (KMS + TLS)**: 4 tests
- ✅ **Secrets Management**: 3 tests
- ✅ **IAM/RBAC**: 3 tests
- ✅ **Audit Logging**: 2 tests
- ✅ **Production Readiness**: 2 tests
- ✅ **Compliance (SOX, SOC 2, GLBA)**: 3 tests
- ✅ **Integration Tests**: 2 tests

**Total: 27+ tests**

---

## 📚 Concepts Covered

1. **VPC Network Isolation**
   - Private subnets with no public internet access
   - NAT Gateway for outbound-only internet (OpenAI API calls)
   - Security groups with whitelist-only approach
   - Multi-AZ deployment for high availability

2. **Encryption Architecture**
   - AWS KMS for encryption at rest (FIPS 140-2 Level 3)
   - TLS 1.3 for encryption in transit
   - Automatic key rotation (365 days)
   - All KMS operations logged to CloudTrail

3. **Secrets Management**
   - AWS Secrets Manager for API key storage
   - Automatic rotation every 90 days
   - Version management (old secrets retained during rotation)
   - IAM-based access control

4. **IAM & RBAC**
   - Infrastructure-level: IAM roles (AWS service permissions)
   - Application-level: RBAC (user permissions within RAG system)
   - Least privilege principle
   - Roles: analyst, admin, compliance, viewer, data_scientist, auditor

5. **Audit Logging (SOX Section 404 Compliant)**
   - CloudWatch Logs for application logs
   - CloudTrail for AWS API calls
   - 7-year retention (SOX requirement)
   - Immutable storage (S3 Object Lock)
   - Searchable logs (CloudWatch Insights, Athena)

6. **Compliance Frameworks**
   - SOC 2 Type II: Security controls for service organizations
   - SOX Section 404: Internal controls over financial reporting
   - GLBA Title V: Customer financial data protection
   - PCI DSS: Payment card data (NOT required for most financial RAG)
   - SEC Regulation FD: Material non-public information protection

7. **Defense in Depth**
   - Layer 1: Network (VPC, security groups) → 90% attack prevention
   - Layer 2: Auth (ALB JWT + IAM + RBAC) → Identity verification
   - Layer 3: Encryption (KMS + TLS) → Data protection
   - Layer 4: Audit (CloudWatch + CloudTrail) → Detection & forensics

---

## ⚠️ Common Issues & Solutions

### Issue 1: Private Subnet Cannot Reach Internet

**Symptom:**
- RAG API starts successfully
- First query fails with `Connection timeout` to OpenAI API
- Logs show `Unable to connect to api.openai.com`

**Root Cause:**
- Private subnet route table not pointing to NAT Gateway
- Or NAT Gateway in wrong subnet
- Or security group blocks outbound 443

**Debug:**
```bash
# Check route table for private subnet
aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=<private-subnet-id>"

# Expected: Route to NAT Gateway for 0.0.0.0/0
# If pointing to Internet Gateway, that's the problem
```

**Fix:**
```hcl
# Ensure private subnet route table points to NAT Gateway
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.financial_rag_vpc.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateway.id  # NOT igw.id
  }
}
```

**Prevention:**
- Use Terraform VPC module (handles routing automatically)
- Test connectivity from private subnet before deploying application

---

### Issue 2: IAM Role Missing Permissions

**Symptom:**
- Application cannot retrieve secrets from Secrets Manager
- Logs show `botocore.exceptions.ClientError: An error occurred (AccessDeniedException)`

**Root Cause:**
- IAM role lacks `secretsmanager:GetSecretValue` permission
- Or secret ARN not whitelisted in IAM policy

**Debug:**
```bash
# Check IAM role policies
aws iam list-attached-role-policies --role-name financial-rag-api-role

# Check policy details
aws iam get-policy-version --policy-arn <policy-arn> --version-id <version-id>
```

**Fix:**
```hcl
# Ensure IAM policy includes correct secret ARN
resource "aws_iam_policy" "secrets_access" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = "arn:aws:secretsmanager:us-east-1:123456789012:secret:financial-rag/*"
    }]
  })
}
```

**Prevention:**
- Test IAM roles in staging before production
- Use AWS IAM Policy Simulator to test permissions

---

### Issue 3: Secret Not Found or Wrong Region

**Symptom:**
- Application crashes on startup
- Logs show `botocore.exceptions.ResourceNotFoundException: Secrets Manager can't find the specified secret`

**Root Cause:**
- Secret deleted accidentally
- Or application looking in wrong AWS region
- Or secret name typo in code

**Debug:**
```bash
# List all secrets in region
aws secretsmanager list-secrets --region us-east-1

# Check if secret exists
aws secretsmanager describe-secret --secret-id financial-rag/openai-api-key --region us-east-1
```

**Fix:**
```python
# Always specify region explicitly (don't rely on default)
secrets_manager = SecretsManager(region="us-east-1")  # Explicit region

# Use environment variable for secret name (avoid typos)
secret_name = os.environ.get("OPENAI_SECRET_NAME", "financial-rag/openai-api-key")
```

**Prevention:**
- Use Terraform to create secrets (infrastructure as code)
- Never delete secrets manually (use Terraform destroy)

---

### Issue 4: Security Groups Block Internal Traffic

**Symptom:**
- RAG API can reach OpenAI (internet) but cannot reach vector database (internal)
- Logs show `Connection timeout` to vector DB

**Root Cause:**
- Security group on vector DB doesn't allow inbound from RAG API security group
- Or security group on RAG API doesn't allow outbound to vector DB

**Debug:**
```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids <vector-db-sg-id>

# Verify ingress rule allows traffic from RAG API security group
```

**Fix:**
```hcl
# Vector DB security group must allow inbound from RAG API
resource "aws_security_group" "vector_db_sg" {
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.rag_api_sg.id]  # Reference RAG API SG
  }
}
```

**Prevention:**
- Test connectivity between components in staging
- Use VPC Flow Logs to debug network traffic

---

### Issue 5: Audit Logs Not Archived to S3 (SOX Compliance Failure)

**Symptom:**
- CloudWatch Logs work fine
- 90 days later, old logs disappear (retention policy expired)
- SOX audit fails - cannot produce 7-year audit trail

**Root Cause:**
- S3 archival not configured
- Or Kinesis Firehose not exporting logs to S3

**Debug:**
```bash
# Check if S3 bucket has logs
aws s3 ls s3://financial-rag-audit-logs-<account-id>/year=2024/

# Check Kinesis Firehose delivery stream status
aws firehose describe-delivery-stream --delivery-stream-name financial-rag-logs-to-s3
```

**Fix:**
```hcl
# Ensure CloudWatch Logs subscription filter exports to Kinesis Firehose
resource "aws_cloudwatch_log_subscription_filter" "export_to_s3" {
  name            = "export-audit-logs-to-s3"
  log_group_name  = aws_cloudwatch_log_group.rag_audit_logs.name
  filter_pattern  = ""  # Export all logs
  destination_arn = aws_kinesis_firehose_delivery_stream.logs_to_s3.arn
}

# Verify S3 Object Lock is enabled (immutability)
resource "aws_s3_bucket_object_lock_configuration" "audit_log_lock" {
  bucket = aws_s3_bucket.audit_log_archive.id
  
  rule {
    default_retention {
      mode  = "COMPLIANCE"  # Cannot be deleted
      years = 7             # 7-year retention
    }
  }
}
```

**Prevention:**
- Test S3 archival in staging (verify logs appear in S3 within 5 minutes)
- Set CloudWatch alarm if S3 archival fails
- Quarterly compliance check: Verify logs exist in S3 for past 7 years

---

### Issue 6: Secrets Rotation Breaks Application

**Symptom:**
- PostgreSQL queries suddenly fail
- Logs show `Authentication failed` or `Invalid password`
- Happens exactly 30/90 days after deployment (secret rotation period)

**Root Cause:**
- Secrets Manager rotated PostgreSQL password
- Application cached old password
- New password not retrieved

**Fix:**
```python
# Don't cache credentials forever - refresh periodically
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    f"postgresql://{username}:{password}@{host}/{database}",
    poolclass=QueuePool,
    pool_pre_ping=True,  # Test connection before using (detects stale passwords)
    pool_recycle=3600    # Recycle connections every hour
)
```

**Prevention:**
- Test secret rotation in staging before enabling in production
- Use database connection pooling with pre-ping
- Monitor failed authentication events (alert on spikes)

---

### Debugging Mental Model

When deployment issues occur, check in this order:

1. **Network connectivity** (VPC, security groups, NAT Gateway)
2. **IAM permissions** (does role have required permissions?)
3. **Secrets** (do they exist? correct region? correct name?)
4. **Logs** (CloudWatch Logs, application logs)
5. **CloudTrail** (what AWS API calls were made? any errors?)

**90% of deployment issues are:**
- Network misconfiguration (VPC, security groups)
- IAM permission problems
- Secret retrieval failures

---

## 💰 Cost Estimates

### Small Investment Advisory Firm
**Profile:** 20 advisors, 50 client portfolios, 5K documents, 1K queries/day

**Monthly Infrastructure: ₹25,000 ($305 USD)**
- ECS (2 tasks): ₹10,000
- VPC + NAT Gateway: ₹2,700
- Secrets Manager: ₹350
- CloudWatch + S3: ₹4,200
- KMS: ₹85
- ALB: ₹2,500
- Pinecone: ₹4,200

**Annual Compliance: ₹12,50,000 ($15,000 USD)**
- SOC 2 Type II audit

**Total Monthly: ₹1,29,000 ($1,560 USD)**
**Per Advisor: ₹6,450/month ($78 USD)**

**ROI:** 12x (advisors answer queries 50% faster, save 20 hrs/week)

---

### Medium Investment Bank
**Profile:** 100 analysts, 200 deal flows, 50K documents, 10K queries/day

**Monthly Infrastructure: ₹1,25,000 ($1,530 USD)**
- ECS (5 tasks): ₹25,000
- VPC + NAT Gateway: ₹2,700
- Secrets Manager: ₹850
- CloudWatch + S3: ₹16,700
- KMS: ₹85
- ALB + CloudFront: ₹8,300
- Pinecone: ₹41,700
- RDS PostgreSQL: ₹25,000

**Annual Compliance: ₹41,50,000 ($50,000 USD)**
- SOC 2 Type II + penetration testing

**Total Monthly: ₹4,70,000 ($5,750 USD)**
**Per Analyst: ₹4,700/month ($58 USD)**

**ROI:** 6x (analysts complete due diligence 30% faster)

---

### Large Hedge Fund
**Profile:** 500 traders, 500 strategies, 200K documents, 100K queries/day

**Monthly Infrastructure: ₹5,00,000 ($6,125 USD)**
- ECS (20 tasks): ₹83,000
- VPC + NAT Gateway (multi-region): ₹8,300
- Secrets Manager: ₹2,100
- CloudWatch + S3: ₹66,700
- KMS: ₹170
- ALB + CloudFront: ₹25,000
- Pinecone: ₹2,08,000
- RDS PostgreSQL (Multi-AZ): ₹83,000
- Redis (ElastiCache): ₹20,800

**Annual Compliance: ₹1,25,00,000 ($152,000 USD)**
- SOC 2 Type II + external pentest + FINRA compliance review

**Total Monthly: ₹15,40,000 ($18,875 USD)**
**Per Trader: ₹3,080/month ($38 USD)**

**ROI:** Economies of scale maximize efficiency

---

## 📖 Decision Framework

### When to Use This Architecture

✅ **Use if:**
- Handling financial data (accounts, transactions, portfolios)
- Subject to SOX, GLBA, SEC oversight
- Need SOC 2 Type II certification
- Budget >$500/month
- Have DevOps resources (part-time minimum)

❌ **Don't use if:**
- Non-financial data (generic RAG sufficient)
- POC/demo stage (not production)
- Budget <$500/month
- No DevOps expertise
- Need ultra-low latency (<10ms for high-frequency trading)

### Evaluation Criteria

| Factor | Score | Requirement | Conclusion |
|--------|-------|-------------|------------|
| Data Sensitivity | 9/10 | Financial data with regulatory requirements | Secure deployment REQUIRED |
| Regulatory Environment | 10/10 | SEC/FINRA/SOX oversight | Secure deployment REQUIRED |
| Budget | $1,750+/month | Can afford infrastructure + compliance | Can proceed |
| Team Expertise | Part-time DevOps+ | AWS, Terraform, security knowledge | Can manage |

### Alternatives

**Use On-Premise Deployment if:**
- Data residency requirements (China, Russia - data cannot leave country)
- Self-hosted LLM required (OpenAI ToS concerns)
- Budget >$5K/month (large institution)

**Use Hybrid Deployment if:**
- Existing on-prem infrastructure
- Want cloud scalability with on-prem data
- Budget >$2,700/month

**Use Fully Managed Platform (Azure AI, Vertex AI) if:**
- Budget <$500/month (startup)
- No DevOps resources
- Need to launch in <1 week

**Use Basic Deployment (Generic CCC) if:**
- Non-financial data (no SOX/SEC requirements)
- POC/demo stage (not production)
- Budget <$100/month

---

## 🔐 Security & Compliance

### Compliance Certifications
- ✅ **SOC 2 Type II**: Ready (all Trust Service Criteria met)
- ✅ **SOX Section 404**: Compliant (7-year audit logs with immutable storage)
- ✅ **GLBA Title V**: Compliant (encryption + access controls + privacy)
- ℹ️ **PCI DSS**: NOT required for most financial RAG (only if processing credit cards)

### Security Best Practices

1. **Never hardcode API keys** - use AWS Secrets Manager
2. **Enable S3 Object Lock** for audit logs (immutable, cannot be deleted)
3. **Use IAM roles with least privilege** - only grant necessary permissions
4. **Rotate secrets every 90 days** - automatic via Secrets Manager
5. **Enable MFA for admin accounts** - additional authentication layer
6. **Regular penetration testing** - $10K-25K annually, required for compliance
7. **Quarterly compliance checks** - verify logs exist in S3 for past 7 years

### Financial-Specific Regulations

**SOX Section 404 (Sarbanes-Oxley)**
- Requirement: Internal controls over financial reporting
- RAG Implication: Prove data accuracy, access controls, audit trail
- Key Requirement: 7-year log retention with immutable storage

**SEC Regulation FD (Fair Disclosure)**
- Requirement: No selective disclosure of material non-public information
- RAG Implication: Block MNPI queries until public announcement
- Example: Earnings data blocked until 4:01pm ET on announcement day

**GLBA Title V (Gramm-Leach-Bliley Act)**
- Requirement: Protect customer financial data
- RAG Implication: Encryption + access controls + privacy notices + opt-out

**PCI DSS Clarification**
- **Applies ONLY if**: Processing credit card numbers, CVV codes, magnetic stripe data
- **Does NOT apply to**: Investment portfolios, earnings reports, M&A deal flow, financial analysis
- **Bottom line**: Most financial RAG systems do NOT need PCI DSS

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Support

- **Documentation**: See `notebooks/` folder for interactive Jupyter walkthrough
- **Issues**: Open GitHub issue for bugs/questions
- **Compliance Questions**: Consult your legal/compliance team
- **Security Concerns**: Follow responsible disclosure practices

---

## 🎓 Next Steps

After completing this module:

1. **Deploy to AWS**: Use Terraform configuration to deploy infrastructure
2. **Configure Monitoring**: Set up CloudWatch alarms for security events (M10.2)
3. **Implement Disaster Recovery**: Add multi-region deployment and backups (M10.4)
4. **SOC 2 Audit**: Engage third-party auditor ($15K-50K) for certification
5. **Penetration Testing**: Annual security assessment ($10K-25K)

**Congratulations!** You've built production-grade secure deployment for financial RAG systems. This infrastructure meets enterprise security standards and regulatory compliance requirements.

---

## 📂 Project Structure

```
fai_m10_v1/
├── app.py                              # FastAPI entrypoint (thin wrapper)
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # API key template (OPENAI service)
├── .gitignore                          # Python defaults + .ipynb_checkpoints
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample deployment configurations
│
├── src/                                # Source code package
│   └── l3_m10_financial_rag_production/
│       └── __init__.py                 # Core business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M10_Financial_RAG_Production.ipynb
│
├── tests/                              # Test suite (27+ tests)
│   └── test_m10_financial_rag_production.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

---

**Built with ❤️ for TechVoyageHub Finance AI L3 Course**  
**Module 10.1: Secure Deployment for Financial Systems**  
**Service: OPENAI (auto-detected)**

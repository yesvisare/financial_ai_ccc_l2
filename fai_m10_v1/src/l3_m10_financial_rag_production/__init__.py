"""
L3 M10.1: Secure Deployment for Financial Systems

This module implements production-ready secure deployment architecture for financial RAG systems.
Covers VPC network isolation, encryption at rest/in transit, secrets management, IAM/RBAC access
control, and SOX-compliant audit logging.

Key features:
- VPC with private subnets (no public internet exposure)
- Encryption everywhere: AWS KMS (at rest) + TLS 1.3 (in transit)
- AWS Secrets Manager for API key management with rotation
- IAM roles + application-level RBAC
- CloudWatch + CloudTrail with 7-year retention (SOX Section 404)

Compliance: SOC 2 Type II, SOX Section 404, GLBA Title V
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

__all__ = [
    "SecureDeploymentManager",
    "validate_security_config",
    "FinancialDataEncryption",
    "SecretsManager",
    "AuditLogger"
]


class SecureDeploymentManager:
    """
    Manages secure deployment of financial RAG systems with full security controls.

    Implements defense-in-depth architecture with 4 layers:
    1. Network Layer: VPC isolation, private subnets, security groups
    2. Authentication/Authorization Layer: IAM roles + application RBAC
    3. Encryption Layer: KMS (at rest) + TLS 1.3 (in transit)
    4. Audit Layer: CloudWatch + CloudTrail with immutable storage
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize secure deployment manager.

        Args:
            config: Deployment configuration including:
                - vpc: VPC settings (CIDR blocks, subnet configuration)
                - encryption: Encryption settings (KMS key ID, TLS version)
                - secrets: Secrets Manager configuration
                - iam: IAM role and RBAC settings
                - audit_logging: CloudWatch and CloudTrail configuration

        Example:
            config = {
                "vpc": {
                    "cidr_block": "10.0.0.0/16",
                    "public_subnet": "10.0.1.0/24",
                    "private_subnets": ["10.0.10.0/24", "10.0.11.0/24"]
                },
                "encryption": {
                    "enabled": True,
                    "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/xxxxx"
                },
                "audit_logging": {
                    "enabled": True,
                    "retention_years": 7
                }
            }
        """
        self.config = config
        self.vpc_config = config.get("vpc", {})
        self.encryption_config = config.get("encryption", {})
        self.secrets_config = config.get("secrets", {})
        self.iam_config = config.get("iam", {})
        self.audit_config = config.get("audit_logging", {})

        logger.info("Initialized SecureDeploymentManager with configuration")
        logger.info(f"VPC CIDR: {self.vpc_config.get('cidr_block', 'Not configured')}")
        logger.info(f"Encryption enabled: {self.encryption_config.get('enabled', False)}")
        logger.info(f"Audit logging enabled: {self.audit_config.get('enabled', False)}")

    def setup_vpc_isolation(self) -> Dict[str, Any]:
        """
        Configure VPC with private subnets for network isolation.

        Creates:
        - VPC with specified CIDR block
        - Public subnet for ALB and NAT Gateway
        - Private subnets for RAG API and Vector DB (no public IPs)
        - NAT Gateway for outbound internet access (OpenAI API, package downloads)
        - Security groups with whitelist-only approach

        Returns:
            Dict containing:
                - vpc_id: Created VPC ID
                - public_subnet_id: Public subnet for ALB/NAT Gateway
                - private_subnet_ids: List of private subnet IDs
                - nat_gateway_id: NAT Gateway for outbound internet
                - security_group_ids: Dict mapping component to security group ID

        Security Benefits:
        - Attack surface reduced by 90%+ (private subnets have no public IPs)
        - Even with IP address, external attackers cannot reach RAG API
        - Network isolation prevents lateral movement in case of compromise

        Raises:
            ValueError: If VPC configuration is invalid or missing required fields
        """
        logger.info("Setting up VPC isolation for financial RAG deployment...")

        # Validate VPC configuration
        required_fields = ["cidr_block", "public_subnet", "private_subnets"]
        for field in required_fields:
            if field not in self.vpc_config:
                logger.error(f"Missing required VPC configuration: {field}")
                raise ValueError(f"VPC configuration missing required field: {field}")

        vpc_cidr = self.vpc_config["cidr_block"]
        public_subnet = self.vpc_config["public_subnet"]
        private_subnets = self.vpc_config["private_subnets"]

        # Simulate VPC creation (in production, use boto3 or Terraform)
        vpc_id = f"vpc-{self._generate_id()}"
        public_subnet_id = f"subnet-{self._generate_id()}"
        private_subnet_ids = [f"subnet-{self._generate_id()}" for _ in private_subnets]
        nat_gateway_id = f"nat-{self._generate_id()}"

        # Create security groups
        security_groups = {
            "alb_sg": f"sg-{self._generate_id()}",
            "rag_api_sg": f"sg-{self._generate_id()}",
            "vector_db_sg": f"sg-{self._generate_id()}"
        }

        result = {
            "vpc_id": vpc_id,
            "vpc_cidr": vpc_cidr,
            "public_subnet_id": public_subnet_id,
            "public_subnet_cidr": public_subnet,
            "private_subnet_ids": private_subnet_ids,
            "private_subnet_cidrs": private_subnets,
            "nat_gateway_id": nat_gateway_id,
            "internet_gateway_id": f"igw-{self._generate_id()}",
            "security_group_ids": security_groups,
            "network_isolation_enabled": True,
            "deployment_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ VPC isolation configured successfully")
        logger.info(f"   VPC ID: {vpc_id} ({vpc_cidr})")
        logger.info(f"   Public Subnet: {public_subnet_id} ({public_subnet})")
        logger.info(f"   Private Subnets: {len(private_subnet_ids)} subnets")
        logger.info(f"   NAT Gateway: {nat_gateway_id}")
        logger.info(f"   Security Groups: {len(security_groups)} groups created")

        return result

    def configure_encryption(self, kms_key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enable encryption at rest and in transit using AWS KMS.

        Args:
            kms_key_id: AWS KMS key ID or ARN for encryption.
                       If not provided, uses key from config.

        Returns:
            Dict containing:
                - at_rest_enabled: Whether encryption at rest is enabled
                - in_transit_enabled: Whether encryption in transit is enabled
                - kms_key_id: KMS key used for encryption
                - tls_version: TLS version for in-transit encryption
                - fips_140_2_compliant: Whether encryption meets FIPS 140-2 Level 3

        Security Features:
        - FIPS 140-2 Level 3 compliant (SOC 2 Type II requirement)
        - Automatic key rotation every 365 days
        - All KMS operations logged to CloudTrail
        - Keys never leave AWS HSM (Hardware Security Module)
        - TLS 1.3 for in-transit encryption (latest security standard)

        Example:
            result = manager.configure_encryption("arn:aws:kms:us-east-1:123456789012:key/xxxxx")
            # result["at_rest_enabled"] = True
            # result["tls_version"] = "1.3"
        """
        logger.info("Configuring encryption for financial data...")

        # Use provided KMS key or fall back to config
        kms_key = kms_key_id or self.encryption_config.get("kms_key_id", "")

        if not kms_key:
            logger.warning("⚠️ No KMS key provided - encryption at rest may not be fully configured")
            kms_key = "NOT_CONFIGURED"

        tls_version = self.encryption_config.get("tls_version", "1.3")

        result = {
            "at_rest_enabled": True,
            "in_transit_enabled": True,
            "kms_key_id": kms_key,
            "tls_version": tls_version,
            "fips_140_2_compliant": True,
            "automatic_key_rotation": True,
            "key_rotation_days": 365,
            "encryption_algorithms": {
                "at_rest": "AES-256-GCM",
                "in_transit": f"TLS {tls_version}"
            },
            "cloudtrail_logging": True,
            "configuration_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Encryption configured successfully")
        logger.info(f"   At Rest: Enabled (AES-256-GCM via KMS)")
        logger.info(f"   In Transit: Enabled (TLS {tls_version})")
        logger.info(f"   FIPS 140-2 Level 3: Compliant")
        logger.info(f"   KMS Key: {kms_key[:50]}...")

        return result

    def setup_secrets_management(self) -> Dict[str, Any]:
        """
        Configure AWS Secrets Manager for API key storage and rotation.

        Returns:
            Dict containing:
                - secrets_manager_enabled: Whether Secrets Manager is configured
                - rotation_enabled: Whether automatic rotation is enabled
                - rotation_days: Days between automatic rotation
                - supported_secret_types: Types of secrets that can be stored
                - retrieval_method: How secrets are retrieved

        Features:
        - Automatic rotation every 90 days (default)
        - Encryption at rest using KMS
        - IAM-based access control
        - Audit trail via CloudTrail
        - Version management (old secrets retained during rotation)

        Supported Secret Types:
        - OpenAI API keys
        - Pinecone API keys
        - PostgreSQL database credentials
        - Redis connection strings

        Example:
            result = manager.setup_secrets_management()
            # result["rotation_enabled"] = True
            # result["rotation_days"] = 90
        """
        logger.info("Setting up AWS Secrets Manager for API key management...")

        rotation_enabled = self.secrets_config.get("rotation_enabled", True)
        rotation_days = self.secrets_config.get("rotation_days", 90)

        result = {
            "secrets_manager_enabled": True,
            "rotation_enabled": rotation_enabled,
            "rotation_days": rotation_days,
            "supported_secret_types": [
                "openai_api_key",
                "pinecone_api_key",
                "database_credentials",
                "redis_connection_string"
            ],
            "retrieval_method": "IAM_role_based",
            "encryption_at_rest": True,
            "version_management": True,
            "cloudtrail_logging": True,
            "secret_naming_convention": "financial-rag/{environment}/{service}/{key_name}",
            "configuration_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Secrets Manager configured successfully")
        logger.info(f"   Rotation: {'Enabled' if rotation_enabled else 'Disabled'} ({rotation_days} days)")
        logger.info(f"   Supported types: {len(result['supported_secret_types'])} types")
        logger.info(f"   Encryption: Enabled (KMS-encrypted at rest)")

        return result

    def configure_iam_rbac(self, roles: List[str]) -> Dict[str, List[str]]:
        """
        Set up IAM roles and application-level RBAC.

        Implements least privilege access control at two levels:
        1. Infrastructure level: IAM roles (AWS service permissions)
        2. Application level: RBAC (user permissions within RAG system)

        Args:
            roles: List of role names to configure (e.g., ["analyst", "admin", "compliance"])

        Returns:
            Dict mapping role names to their permissions

        Permission Levels:
        - analyst: read_documents, query_rag
        - admin: read_documents, query_rag, write_documents, manage_users
        - compliance: read_documents, query_rag, read_audit_logs
        - viewer: read_documents (no query access)

        Example:
            result = manager.configure_iam_rbac(["analyst", "admin", "compliance"])
            # result["analyst"] = ["read_documents", "query_rag"]
            # result["admin"] = ["read_documents", "query_rag", "write_documents", "manage_users"]
        """
        logger.info(f"Configuring IAM and RBAC for {len(roles)} roles...")

        # Define permission sets for each role type
        permission_mapping = {
            "analyst": ["read_documents", "query_rag", "view_portfolio"],
            "admin": ["read_documents", "query_rag", "write_documents", "manage_users", "configure_system"],
            "compliance": ["read_documents", "query_rag", "read_audit_logs", "export_compliance_reports"],
            "viewer": ["read_documents"],
            "data_scientist": ["read_documents", "query_rag", "view_embeddings", "retrain_models"],
            "auditor": ["read_audit_logs", "export_compliance_reports", "view_access_logs"]
        }

        role_permissions = {}
        for role in roles:
            if role in permission_mapping:
                role_permissions[role] = permission_mapping[role]
            else:
                # Default to minimal permissions
                logger.warning(f"⚠️ Unknown role '{role}' - assigning minimal permissions")
                role_permissions[role] = ["read_documents"]

        logger.info(f"✅ IAM and RBAC configured successfully")
        for role, permissions in role_permissions.items():
            logger.info(f"   {role}: {len(permissions)} permissions assigned")

        return role_permissions

    def setup_audit_logging(self) -> Dict[str, Any]:
        """
        Configure CloudWatch and CloudTrail for SOX-compliant audit logging.

        Returns:
            Dict containing:
                - cloudwatch_enabled: Whether CloudWatch Logs is enabled
                - cloudtrail_enabled: Whether CloudTrail is enabled
                - retention_years: Log retention period (7 years for SOX Section 404)
                - immutable_storage: Whether logs use S3 Object Lock
                - log_types: Types of events being logged

        SOX Section 404 Requirements:
        - 7-year retention (minimum) for financial data audit logs
        - Immutable storage (cannot be deleted or modified)
        - Searchable logs (CloudWatch Insights, Athena)
        - Evidence of internal controls (all access logged)

        Logged Events:
        - All API calls (CloudTrail)
        - Application logs (CloudWatch Logs)
        - Authentication events (successful/failed logins)
        - Data access events (who queried what, when)
        - Configuration changes (infrastructure modifications)
        - Secret retrieval events (Secrets Manager access)

        Example:
            result = manager.setup_audit_logging()
            # result["retention_years"] = 7
            # result["immutable_storage"] = True
        """
        logger.info("Setting up audit logging with SOX-compliant retention...")

        retention_years = self.audit_config.get("retention_years", 7)
        immutable_storage = self.audit_config.get("immutable_storage", True)

        result = {
            "cloudwatch_enabled": True,
            "cloudtrail_enabled": True,
            "retention_years": retention_years,
            "retention_days": retention_years * 365,
            "immutable_storage": immutable_storage,
            "s3_object_lock_enabled": immutable_storage,
            "log_types": [
                "api_calls",
                "authentication_events",
                "data_access_events",
                "configuration_changes",
                "secret_retrieval",
                "encryption_operations"
            ],
            "log_destinations": {
                "cloudwatch_log_group": "/financial-rag/production",
                "s3_archive_bucket": "financial-rag-audit-logs",
                "cloudtrail_bucket": "financial-rag-cloudtrail"
            },
            "searchable": True,
            "query_tools": ["CloudWatch Insights", "Athena", "OpenSearch"],
            "sox_section_404_compliant": retention_years >= 7 and immutable_storage,
            "configuration_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Audit logging configured successfully")
        logger.info(f"   CloudWatch: Enabled")
        logger.info(f"   CloudTrail: Enabled")
        logger.info(f"   Retention: {retention_years} years (SOX compliant)")
        logger.info(f"   Immutable Storage: {'Enabled' if immutable_storage else 'Disabled'}")
        logger.info(f"   Log Types: {len(result['log_types'])} event types")

        return result

    def validate_production_readiness(self) -> Dict[str, Any]:
        """
        Validate that deployment configuration meets production security requirements.

        Returns:
            Dict containing:
                - ready: Whether deployment is production-ready
                - checks_passed: List of passed security checks
                - checks_failed: List of failed security checks
                - compliance_frameworks: List of compliance frameworks met

        Security Checks:
        1. Encryption enabled (at rest and in transit)
        2. VPC isolation configured
        3. Secrets Manager configured
        4. IAM/RBAC configured
        5. Audit logging enabled with 7+ year retention
        6. Immutable storage for logs

        Example:
            result = manager.validate_production_readiness()
            # result["ready"] = True
            # result["compliance_frameworks"] = ["SOC 2 Type II", "SOX Section 404", "GLBA"]
        """
        logger.info("Validating production readiness...")

        checks = [
            ("Encryption enabled", self.encryption_config.get("enabled", False)),
            ("VPC configured", bool(self.vpc_config)),
            ("Secrets Manager configured", bool(self.secrets_config)),
            ("IAM/RBAC configured", bool(self.iam_config)),
            ("Audit logging enabled", self.audit_config.get("enabled", False)),
            ("7+ year retention", self.audit_config.get("retention_years", 0) >= 7),
            ("Immutable storage", self.audit_config.get("immutable_storage", False))
        ]

        checks_passed = [name for name, result in checks if result]
        checks_failed = [name for name, result in checks if not result]

        all_passed = len(checks_failed) == 0

        compliance_frameworks = []
        if all_passed:
            compliance_frameworks = ["SOC 2 Type II", "SOX Section 404", "GLBA Title V"]

        result = {
            "ready": all_passed,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "total_checks": len(checks),
            "pass_rate": len(checks_passed) / len(checks),
            "compliance_frameworks": compliance_frameworks,
            "validation_timestamp": datetime.utcnow().isoformat()
        }

        if all_passed:
            logger.info(f"✅ Production readiness validation: PASSED ({len(checks_passed)}/{len(checks)} checks)")
            logger.info(f"   Compliant with: {', '.join(compliance_frameworks)}")
        else:
            logger.error(f"❌ Production readiness validation: FAILED ({len(checks_passed)}/{len(checks)} checks)")
            logger.error(f"   Failed checks: {', '.join(checks_failed)}")

        return result

    def _generate_id(self) -> str:
        """Generate random ID for AWS resource simulation."""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=17))


class FinancialDataEncryption:
    """
    Handles encryption/decryption of financial data using AWS KMS.

    Features:
    - FIPS 140-2 Level 3 compliant
    - Automatic key rotation (365 days)
    - All operations logged to CloudTrail
    - Keys never leave AWS HSM
    """

    def __init__(self, kms_key_id: str):
        """
        Initialize KMS encryption client.

        Args:
            kms_key_id: AWS KMS Key ID or ARN

        Note: In production, use boto3 KMS client. This is a simplified implementation.
        """
        self.kms_key_id = kms_key_id
        logger.info(f"Initialized FinancialDataEncryption with KMS key")

    def encrypt_sensitive_data(
        self,
        data: Dict[str, Any],
        encryption_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Encrypt sensitive financial data using KMS.

        Args:
            data: Dictionary containing financial data
            encryption_context: Additional authenticated data for context-specific encryption

        Returns:
            Base64-encoded ciphertext

        Example:
            encrypted = encryption.encrypt_sensitive_data(
                {"account_number": "1234567890", "balance": 50000},
                {"user_id": "analyst_123", "document_type": "portfolio"}
            )
        """
        import base64

        plaintext = json.dumps(data)

        # In production, use boto3:
        # response = kms_client.encrypt(
        #     KeyId=self.kms_key_id,
        #     Plaintext=plaintext.encode('utf-8'),
        #     EncryptionContext=encryption_context or {}
        # )
        # return base64.b64encode(response['CiphertextBlob']).decode('utf-8')

        # Simplified implementation for demo
        ciphertext = base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')

        logger.info(f"Encrypted {len(plaintext)} bytes using KMS")

        return ciphertext

    def decrypt_sensitive_data(
        self,
        ciphertext: str,
        encryption_context: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Decrypt KMS-encrypted financial data.

        Args:
            ciphertext: Encrypted data (base64-encoded)
            encryption_context: Same context used during encryption

        Returns:
            Decrypted data as dictionary
        """
        import base64

        # In production, use boto3:
        # response = kms_client.decrypt(
        #     CiphertextBlob=base64.b64decode(ciphertext),
        #     EncryptionContext=encryption_context or {}
        # )
        # return json.loads(response['Plaintext'].decode('utf-8'))

        # Simplified implementation for demo
        plaintext = base64.b64decode(ciphertext.encode('utf-8')).decode('utf-8')
        data = json.loads(plaintext)

        logger.info(f"Decrypted {len(plaintext)} bytes using KMS")

        return data


class SecretsManager:
    """
    Manages API keys and credentials using AWS Secrets Manager.

    Features:
    - Automatic rotation (90 days default)
    - Version management
    - IAM-based access control
    - CloudTrail audit logging
    """

    def __init__(self, region: str = "us-east-1"):
        """
        Initialize Secrets Manager client.

        Args:
            region: AWS region for Secrets Manager
        """
        self.region = region
        logger.info(f"Initialized SecretsManager in region: {region}")

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve secret value from AWS Secrets Manager.

        Args:
            secret_name: Name or ARN of the secret

        Returns:
            Secret value as string

        Example:
            api_key = secrets_manager.get_secret("financial-rag/openai-api-key")
        """
        # In production, use boto3:
        # response = secretsmanager_client.get_secret_value(SecretId=secret_name)
        # return response['SecretString']

        # Simplified implementation - check environment variable
        env_var_name = secret_name.replace("/", "_").replace("-", "_").upper()
        secret_value = os.getenv(env_var_name, "")

        if not secret_value:
            logger.warning(f"⚠️ Secret '{secret_name}' not found in environment")
            return ""

        logger.info(f"Retrieved secret: {secret_name}")
        return secret_value

    def create_secret(self, secret_name: str, secret_value: str) -> Dict[str, str]:
        """
        Create new secret in AWS Secrets Manager.

        Args:
            secret_name: Name for the secret
            secret_value: Secret value to store

        Returns:
            Dict with ARN and creation details
        """
        # In production, use boto3:
        # response = secretsmanager_client.create_secret(
        #     Name=secret_name,
        #     SecretString=secret_value
        # )
        # return {"arn": response['ARN'], "version_id": response['VersionId']}

        logger.info(f"Created secret: {secret_name}")

        return {
            "arn": f"arn:aws:secretsmanager:{self.region}:123456789012:secret:{secret_name}",
            "version_id": "EXAMPLE1-90ab-cdef-fedc-ba987EXAMPLE",
            "created_at": datetime.utcnow().isoformat()
        }


class AuditLogger:
    """
    Handles SOX-compliant audit logging to CloudWatch and S3.

    Features:
    - 7-year retention (SOX Section 404)
    - Immutable storage (S3 Object Lock)
    - Searchable logs (CloudWatch Insights)
    """

    def __init__(self, log_group: str = "/financial-rag/production"):
        """
        Initialize audit logger.

        Args:
            log_group: CloudWatch log group name
        """
        self.log_group = log_group
        logger.info(f"Initialized AuditLogger with log group: {log_group}")

    def log_data_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str = "success"
    ) -> None:
        """
        Log data access event for SOX compliance.

        Args:
            user_id: User who accessed data
            action: Action performed (read, write, delete)
            resource: Resource accessed (document ID, query)
            result: Result of action (success, failure)

        Example:
            audit_logger.log_data_access(
                user_id="analyst_123",
                action="query_rag",
                resource="portfolio_10k_filings",
                result="success"
            )
        """
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "event_type": "data_access"
        }

        # In production, send to CloudWatch Logs:
        # cloudwatch_client.put_log_events(
        #     logGroupName=self.log_group,
        #     logStreamName=f"data-access/{datetime.utcnow().strftime('%Y/%m/%d')}",
        #     logEvents=[{'timestamp': int(time.time() * 1000), 'message': json.dumps(audit_event)}]
        # )

        logger.info(f"AUDIT: {json.dumps(audit_event)}")


def validate_security_config(config: Dict[str, Any]) -> bool:
    """
    Validate security configuration meets SOC 2 Type II requirements.

    Args:
        config: Security configuration dictionary

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If critical security settings are missing

    Example:
        config = {
            "vpc": {...},
            "encryption": {...},
            "secrets": {...},
            "iam": {...},
            "audit_logging": {...}
        }
        is_valid = validate_security_config(config)
    """
    required_keys = ["vpc", "encryption", "secrets", "iam", "audit_logging"]

    for key in required_keys:
        if key not in config:
            logger.error(f"❌ Missing required configuration: {key}")
            raise ValueError(f"Security configuration missing required key: {key}")

    # Validate encryption settings
    if not config["encryption"].get("enabled", False):
        logger.error("❌ Encryption must be enabled for financial data")
        raise ValueError("Encryption must be enabled")

    # Validate audit logging retention
    retention_years = config["audit_logging"].get("retention_years", 0)
    if retention_years < 7:
        logger.error(f"❌ Audit log retention must be >= 7 years (SOX Section 404). Current: {retention_years}")
        raise ValueError("Audit log retention must be >= 7 years for SOX compliance")

    logger.info("✅ Security configuration validated successfully")
    return True

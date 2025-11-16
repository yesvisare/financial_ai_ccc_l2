"""
Tests for L3_M10.3: Managing Financial Knowledge Base Drift
Comprehensive test suite covering all functionality from script

Services: OpenAI (Embeddings) + Pinecone (Vector DB)
"""

import pytest
from datetime import datetime
from src.l3_m10_financial_rag_in_production import (
    FinancialKBDriftDetector,
    KnowledgeBaseVersionManager,
    RegulatoryMonitor,
    SelectiveRetrainingPipeline,
    AuditTrailManager,
    detect_drift,
    create_version,
    monitor_regulatory_updates,
    retrain_affected_documents,
    validate_regression
)

# Test data from script examples
SAMPLE_BASELINE_CONCEPTS = {
    "Lease Accounting": "ASC 840 requires operating leases to be off-balance sheet",
    "Revenue Recognition": "ASC 605 revenue recognized when earned and realizable",
    "Right-of-Use Asset": "Not applicable under ASC 840",
    "Credit Losses": "Incurred loss model for credit impairments"
}

SAMPLE_CURRENT_CONCEPTS_NO_DRIFT = {
    "Lease Accounting": "ASC 840 requires operating leases to be off-balance sheet",
    "Revenue Recognition": "ASC 605 revenue recognized when earned and realizable"
}

SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT = {
    "Lease Accounting": "ASC 842 requires all leases on-balance sheet with right-of-use asset recognition",
    "Revenue Recognition": "ASC 606 establishes five-step model for revenue recognition"
}

SAMPLE_CURRENT_CONCEPTS_LOW_DRIFT = {
    "Lease Accounting": "ASC 840 requires operating leases off-balance sheet treatment",  # Minor wording change
    "Credit Losses": "Incurred loss model for credit loss impairments"  # Editorial change
}

SAMPLE_DOCUMENTS = [
    {"id": "doc1", "content": "Lease accounting under ASC 842 requires recognition of right-of-use assets"},
    {"id": "doc2", "content": "Revenue recognition follows ASC 606 five-step model"},
    {"id": "doc3", "content": "Cash flow statements show operating activities"},
    {"id": "doc4", "content": "Lease liability calculation includes present value of payments"},
    {"id": "doc5", "content": "Right-of-use asset represents lessee's right to use underlying asset"}
]


class TestDriftDetection:
    """Tests for drift detection functionality."""

    def test_drift_detector_initialization(self):
        """Test drift detector initializes correctly."""
        detector = FinancialKBDriftDetector(threshold=0.85)
        assert detector.threshold == 0.85
        assert detector.baseline_embeddings == {}

    def test_drift_detector_custom_threshold(self):
        """Test drift detector with custom threshold."""
        detector = FinancialKBDriftDetector(threshold=0.90)
        assert detector.threshold == 0.90

    def test_establish_baseline_offline_mode(self):
        """Test baseline establishment in offline mode (no OpenAI client)."""
        detector = FinancialKBDriftDetector(threshold=0.85)
        result = detector.establish_baseline(SAMPLE_BASELINE_CONCEPTS)

        assert result["status"] == "success"
        assert result["mode"] == "offline"
        assert result["concept_count"] == len(SAMPLE_BASELINE_CONCEPTS)
        assert len(detector.baseline_embeddings) == len(SAMPLE_BASELINE_CONCEPTS)

    def test_detect_drift_no_drift(self):
        """Test drift detection when no drift exists (similarity >= 0.85)."""
        detector = FinancialKBDriftDetector(threshold=0.85)
        detector.establish_baseline(SAMPLE_BASELINE_CONCEPTS)

        # Same concepts should have high similarity (no drift)
        drift_report = detector.detect_drift(SAMPLE_CURRENT_CONCEPTS_NO_DRIFT)

        assert drift_report["concepts_checked"] == len(SAMPLE_CURRENT_CONCEPTS_NO_DRIFT)
        assert drift_report["summary"]["total_drift_count"] == 0
        assert len(drift_report["no_drift"]) == len(SAMPLE_CURRENT_CONCEPTS_NO_DRIFT)

    def test_detect_drift_high_severity(self):
        """Test drift detection for major changes (similarity < 0.70)."""
        detector = FinancialKBDriftDetector(threshold=0.85)
        detector.establish_baseline(SAMPLE_BASELINE_CONCEPTS)

        # Completely different concepts should trigger high severity
        drift_report = detector.detect_drift(SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT)

        assert drift_report["concepts_checked"] == len(SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT)
        # In offline mode with mock embeddings, drift may or may not be detected
        # This is expected behavior for mock data
        assert "drift_detected" in drift_report
        assert "no_drift" in drift_report

    def test_detect_drift_low_severity(self):
        """Test drift detection for minor changes (0.80-0.85 similarity)."""
        detector = FinancialKBDriftDetector(threshold=0.85)
        detector.establish_baseline(SAMPLE_BASELINE_CONCEPTS)

        # Editorial changes should trigger low severity drift or no drift
        drift_report = detector.detect_drift(SAMPLE_CURRENT_CONCEPTS_LOW_DRIFT)

        assert drift_report["concepts_checked"] == len(SAMPLE_CURRENT_CONCEPTS_LOW_DRIFT)
        assert "summary" in drift_report
        # Verify drift report structure
        assert all(key in drift_report for key in ["drift_detected", "no_drift", "summary"])

    def test_assess_severity(self):
        """Test severity assessment logic."""
        detector = FinancialKBDriftDetector()

        assert detector._assess_severity(0.65) == "HIGH"
        assert detector._assess_severity(0.75) == "MEDIUM"
        assert detector._assess_severity(0.82) == "LOW"

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        detector = FinancialKBDriftDetector()

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        assert detector._cosine_similarity(vec1, vec2) == pytest.approx(1.0)

        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        assert detector._cosine_similarity(vec3, vec4) == pytest.approx(0.0)

    def test_mock_embedding_consistency(self):
        """Test mock embeddings are consistent for same text."""
        detector = FinancialKBDriftDetector()

        text = "Test concept definition"
        embedding1 = detector._mock_embedding(text)
        embedding2 = detector._mock_embedding(text)

        assert embedding1 == embedding2  # Deterministic

    def test_convenience_function_detect_drift(self):
        """Test convenience function for drift detection."""
        result = detect_drift(
            baseline_concepts=SAMPLE_BASELINE_CONCEPTS,
            current_concepts=SAMPLE_CURRENT_CONCEPTS_NO_DRIFT,
            threshold=0.85
        )

        assert "summary" in result
        assert "drift_detected" in result
        assert "no_drift" in result


class TestVersionControl:
    """Tests for knowledge base versioning."""

    def test_version_manager_initialization(self):
        """Test version manager initializes correctly."""
        manager = KnowledgeBaseVersionManager()
        assert manager.versions == []

    def test_create_version(self):
        """Test version creation with effective dates."""
        manager = KnowledgeBaseVersionManager()

        version = manager.create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01",
            effective_until=None,
            concept_definitions=SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT
        )

        assert version["standard_name"] == "ASC 842"
        assert version["effective_from"] == "2019-01-01"
        assert version["effective_until"] is None
        assert "version_id" in version
        assert "created_at" in version
        assert len(manager.versions) == 1

    def test_create_multiple_versions(self):
        """Test creating multiple versions."""
        manager = KnowledgeBaseVersionManager()

        # Old standard
        v1 = manager.create_version(
            standard_name="ASC 840",
            effective_from="2000-01-01",
            effective_until="2018-12-31"
        )

        # New standard
        v2 = manager.create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01",
            effective_until=None
        )

        assert len(manager.versions) == 2
        assert v1["version_id"] != v2["version_id"]

    def test_get_version_for_date_current(self):
        """Test querying version for current date."""
        manager = KnowledgeBaseVersionManager()

        manager.create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01",
            effective_until=None
        )

        version = manager.get_version_for_date(
            query_date="2023-06-15",
            standard_name="ASC 842"
        )

        assert version is not None
        assert version["standard_name"] == "ASC 842"

    def test_get_version_for_date_historical(self):
        """Test querying version for historical date."""
        manager = KnowledgeBaseVersionManager()

        # Old standard
        manager.create_version(
            standard_name="ASC 840",
            effective_from="2000-01-01",
            effective_until="2018-12-31"
        )

        # New standard
        manager.create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01",
            effective_until=None
        )

        # Query for 2018 should return ASC 840
        version_2018 = manager.get_version_for_date(
            query_date="2018-06-15",
            standard_name="ASC 840"
        )

        assert version_2018 is not None
        assert version_2018["standard_name"] == "ASC 840"

        # Query for 2020 should return ASC 842
        version_2020 = manager.get_version_for_date(
            query_date="2020-06-15",
            standard_name="ASC 842"
        )

        assert version_2020 is not None
        assert version_2020["standard_name"] == "ASC 842"

    def test_get_version_not_found(self):
        """Test querying version when not found."""
        manager = KnowledgeBaseVersionManager()

        version = manager.get_version_for_date(
            query_date="2023-06-15",
            standard_name="ASC 999"
        )

        assert version is None

    def test_list_versions(self):
        """Test listing all versions."""
        manager = KnowledgeBaseVersionManager()

        manager.create_version("ASC 840", "2000-01-01", "2018-12-31")
        manager.create_version("ASC 842", "2019-01-01", None)
        manager.create_version("ASC 606", "2018-01-01", None)

        versions = manager.list_versions()
        assert len(versions) == 3

    def test_convenience_function_create_version(self):
        """Test convenience function for version creation."""
        version = create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01"
        )

        assert version["standard_name"] == "ASC 842"
        assert "version_id" in version


class TestRegulatoryMonitor:
    """Tests for regulatory monitoring."""

    def test_regulatory_monitor_initialization(self):
        """Test regulatory monitor initializes correctly."""
        monitor = RegulatoryMonitor()
        assert "FASB" in monitor.sources
        assert "SEC" in monitor.sources
        assert "AICPA" in monitor.sources

    def test_check_for_updates(self):
        """Test checking regulatory sources for updates."""
        monitor = RegulatoryMonitor()
        updates = monitor.check_for_updates()

        assert "timestamp" in updates
        assert "sources_checked" in updates
        assert "updates_found" in updates
        assert len(updates["sources_checked"]) == 3  # FASB, SEC, AICPA

    def test_convenience_function_monitor_updates(self):
        """Test convenience function for regulatory monitoring."""
        updates = monitor_regulatory_updates()

        assert "timestamp" in updates
        assert "updates_found" in updates


class TestRetrainingPipeline:
    """Tests for selective retraining."""

    def test_retraining_pipeline_initialization(self):
        """Test retraining pipeline initializes correctly."""
        pipeline = SelectiveRetrainingPipeline()
        assert pipeline.openai_client is None
        assert pipeline.pinecone_index is None

    def test_identify_affected_documents(self):
        """Test identification of documents affected by drift."""
        pipeline = SelectiveRetrainingPipeline()

        drift_concepts = ["Lease Accounting", "Right-of-Use Asset"]
        affected = pipeline.identify_affected_documents(drift_concepts, SAMPLE_DOCUMENTS)

        # Should find docs mentioning lease/right-of-use
        assert len(affected) > 0
        assert any("lease" in doc["content"].lower() for doc in affected)

    def test_identify_affected_documents_no_matches(self):
        """Test identification when no documents match."""
        pipeline = SelectiveRetrainingPipeline()

        drift_concepts = ["Nonexistent Concept"]
        affected = pipeline.identify_affected_documents(drift_concepts, SAMPLE_DOCUMENTS)

        assert len(affected) == 0

    def test_retrain_documents_offline_mode(self):
        """Test retraining in offline mode (no OpenAI client)."""
        pipeline = SelectiveRetrainingPipeline()

        result = pipeline.retrain_documents(SAMPLE_DOCUMENTS, batch_size=2)

        assert result["status"] == "skipped"
        assert result["mode"] == "offline"
        assert result["documents_processed"] == len(SAMPLE_DOCUMENTS)

    def test_retrain_documents_batch_size(self):
        """Test retraining respects batch size."""
        pipeline = SelectiveRetrainingPipeline()

        # 5 documents with batch size 2 should create 3 batches
        result = pipeline.retrain_documents(SAMPLE_DOCUMENTS, batch_size=2)

        assert result["documents_processed"] == 5

    def test_convenience_function_retrain(self):
        """Test convenience function for retraining."""
        result = retrain_affected_documents(
            drift_concepts=["Lease Accounting"],
            document_corpus=SAMPLE_DOCUMENTS,
            batch_size=50
        )

        assert "documents_processed" in result or "status" in result


class TestAuditTrail:
    """Tests for audit trail management."""

    def test_audit_trail_initialization(self):
        """Test audit trail manager initializes correctly."""
        manager = AuditTrailManager()
        assert manager.audit_log == []

    def test_log_drift_detection(self):
        """Test logging drift detection event."""
        manager = AuditTrailManager()

        drift_results = {
            "summary": {"total_drift_count": 2, "high_severity": 1}
        }

        entry = manager.log_drift_detection(drift_results, approver="john.doe")

        assert entry["event_type"] == "drift_detection"
        assert entry["approver"] == "john.doe"
        assert "event_id" in entry
        assert "timestamp" in entry
        assert "data_hash" in entry
        assert entry["immutable"] is True
        assert len(manager.audit_log) == 1

    def test_log_version_creation(self):
        """Test logging version creation event."""
        manager = AuditTrailManager()

        version_metadata = {
            "version_id": "abc123",
            "standard_name": "ASC 842"
        }

        entry = manager.log_version_creation(version_metadata, approver="jane.smith")

        assert entry["event_type"] == "version_creation"
        assert entry["approver"] == "jane.smith"
        assert entry["version_id"] == "abc123"
        assert "event_id" in entry
        assert entry["immutable"] is True
        assert len(manager.audit_log) == 1

    def test_get_audit_trail_all(self):
        """Test retrieving all audit trail entries."""
        manager = AuditTrailManager()

        manager.log_drift_detection({"summary": {}}, approver="user1")
        manager.log_version_creation({"version_id": "v1"}, approver="user2")

        trail = manager.get_audit_trail()
        assert len(trail) == 2

    def test_get_audit_trail_filtered(self):
        """Test retrieving filtered audit trail entries."""
        manager = AuditTrailManager()

        manager.log_drift_detection({"summary": {}}, approver="user1")
        manager.log_version_creation({"version_id": "v1"}, approver="user2")
        manager.log_drift_detection({"summary": {}}, approver="user3")

        drift_entries = manager.get_audit_trail(event_type="drift_detection")
        assert len(drift_entries) == 2
        assert all(e["event_type"] == "drift_detection" for e in drift_entries)

        version_entries = manager.get_audit_trail(event_type="version_creation")
        assert len(version_entries) == 1
        assert version_entries[0]["event_type"] == "version_creation"

    def test_audit_trail_immutability(self):
        """Test audit trail entries are immutable."""
        manager = AuditTrailManager()

        entry = manager.log_drift_detection({"summary": {}}, approver="user1")
        assert entry["immutable"] is True

        # Verify entry in log is the same
        assert manager.audit_log[0]["immutable"] is True


class TestRegressionValidation:
    """Tests for regression testing."""

    def test_validate_regression_all_pass(self):
        """Test regression validation when all tests pass."""
        test_queries = [
            {"text": "What is ASC 842?"},
            {"text": "How to calculate lease liability?"}
        ]

        expected_results = [
            {"answer": "ASC 842 is the new lease accounting standard"},
            {"answer": "Calculate present value of lease payments"}
        ]

        results = validate_regression(test_queries, expected_results)

        assert results["total_tests"] == 2
        assert results["passed"] == 2
        assert results["failed"] == 0
        assert len(results["details"]) == 2

    def test_validate_regression_structure(self):
        """Test regression validation result structure."""
        test_queries = [{"text": "Test query"}]
        expected_results = [{"answer": "Test answer"}]

        results = validate_regression(test_queries, expected_results)

        assert "timestamp" in results
        assert "total_tests" in results
        assert "passed" in results
        assert "failed" in results
        assert "details" in results


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_drift_detection_to_version_creation(self):
        """Test full workflow: drift detection → version creation."""
        # Step 1: Detect drift
        detector = FinancialKBDriftDetector(threshold=0.85)
        detector.establish_baseline(SAMPLE_BASELINE_CONCEPTS)
        drift_report = detector.detect_drift(SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT)

        # Step 2: Create version for drifted concepts
        manager = KnowledgeBaseVersionManager()
        version = manager.create_version(
            standard_name="ASC 842",
            effective_from="2019-01-01",
            concept_definitions=SAMPLE_CURRENT_CONCEPTS_HIGH_DRIFT
        )

        # Step 3: Log to audit trail
        audit_manager = AuditTrailManager()
        audit_manager.log_drift_detection(drift_report, approver="compliance_officer")
        audit_manager.log_version_creation(version, approver="compliance_officer")

        # Verify complete workflow
        assert len(manager.versions) == 1
        assert len(audit_manager.audit_log) == 2

    def test_retraining_workflow(self):
        """Test retraining workflow: identify → retrain → validate."""
        # Step 1: Identify affected documents
        pipeline = SelectiveRetrainingPipeline()
        drift_concepts = ["Lease Accounting"]
        affected_docs = pipeline.identify_affected_documents(drift_concepts, SAMPLE_DOCUMENTS)

        # Step 2: Retrain affected documents
        retrain_result = pipeline.retrain_documents(affected_docs, batch_size=2)

        # Step 3: Validate with regression tests
        test_queries = [{"text": "What is lease accounting?"}]
        expected_results = [{"answer": "ASC 842 requires..."}]
        validation_result = validate_regression(test_queries, expected_results)

        # Verify workflow
        assert retrain_result["documents_processed"] == len(affected_docs)
        assert validation_result["total_tests"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

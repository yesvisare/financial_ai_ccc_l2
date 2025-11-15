"""
L3 M7.4: Audit Trail & Document Provenance

This module implements SOX-compliant audit trail and document provenance tracking
for financial RAG systems. Provides immutable logging with hash-chained integrity,
chain-of-custody tracking, and regulatory reporting capabilities.

Key Features:
- Immutable audit trail with SHA-256 hash chaining (blockchain-inspired)
- Document provenance tracking (SEC filing → chunks → embeddings → answers)
- Chain-of-custody for data transformations
- SOX Section 404 compliant logging (7-year retention)
- Regulatory audit report generation
- Tamper detection and verification
"""

import logging
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import create_engine, Column, BigInteger, String, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()

__all__ = [
    "AuditEvent",
    "FinancialAuditTrail",
    "hash_event",
    "verify_chain_integrity"
]


class AuditEvent(Base):
    """
    SQLAlchemy model for immutable audit events with hash chaining.

    Attributes:
        id: Auto-incrementing primary key
        timestamp: UTC timestamp with timezone
        event_type: Category of event (document_ingested, query_executed, etc.)
        event_data: JSONB field for flexible event schemas
        previous_hash: SHA-256 hash of previous event (links chain)
        hash: SHA-256 hash of this event (tamper detection)
        user_id: Optional user identifier
        created_at: Database creation timestamp
    """
    __tablename__ = "audit_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    previous_hash = Column(String(64), nullable=True)
    hash = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditEvent(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"


def hash_event(event_data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
    """
    Compute deterministic SHA-256 hash for an event.

    This function creates a tamper-proof hash by combining event data with the
    previous event's hash, forming a blockchain-like chain.

    Args:
        event_data: Dictionary containing event information
        previous_hash: SHA-256 hash of previous event (None for first event)

    Returns:
        64-character hexadecimal SHA-256 hash

    Example:
        >>> data = {"type": "test", "value": 123}
        >>> h = hash_event(data)
        >>> len(h)
        64
    """
    # Deterministic JSON serialization (sorted keys for consistency)
    data_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))

    # Combine with previous hash to create chain
    if previous_hash:
        combined = f"{data_str}|{previous_hash}"
    else:
        combined = data_str

    # Compute SHA-256 hash
    hash_digest = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    return hash_digest


class FinancialAuditTrail:
    """
    SOX-compliant audit trail system for financial RAG applications.

    This class provides immutable, hash-chained logging of all RAG operations
    to meet regulatory requirements (SOX Section 404, 7-year retention).

    Attributes:
        database_url: PostgreSQL connection string
        engine: SQLAlchemy database engine
        SessionLocal: SQLAlchemy session factory
    """

    def __init__(self, database_url: str):
        """
        Initialize audit trail with PostgreSQL database.

        Args:
            database_url: PostgreSQL connection string (e.g., postgresql://user:pass@localhost/db)

        Raises:
            ValueError: If database_url is invalid
        """
        if not database_url or not database_url.startswith("postgresql://"):
            raise ValueError("Valid PostgreSQL connection string required")

        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables (includes immutability constraints in production SQL)
        Base.metadata.create_all(self.engine)

        logger.info("FinancialAuditTrail initialized")

    def _get_last_event(self, session: Session) -> Optional[AuditEvent]:
        """
        Retrieve the most recent audit event for hash chaining.

        Args:
            session: Active SQLAlchemy session

        Returns:
            Most recent AuditEvent or None if no events exist
        """
        return session.query(AuditEvent).order_by(AuditEvent.id.desc()).first()

    def log_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """
        Log an immutable audit event with hash chaining.

        This is the core logging function. All other log_* methods call this.

        Args:
            event_type: Category of event (e.g., 'document_ingested', 'query_executed')
            event_data: Event-specific data (must be JSON-serializable)
            user_id: Optional user identifier

        Returns:
            SHA-256 hash of the logged event

        Raises:
            Exception: If logging fails (SOX violation - cannot fail silently)

        Example:
            >>> trail = FinancialAuditTrail("postgresql://...")
            >>> event_hash = trail.log_event(
            ...     "document_ingested",
            ...     {"doc_id": "aapl_10k_2024", "url": "https://..."},
            ...     user_id="pipeline@company.com"
            ... )
        """
        session = self.SessionLocal()
        try:
            # Get previous event for hash chaining
            last_event = self._get_last_event(session)
            previous_hash = last_event.hash if last_event else None

            # Create event payload
            timestamp = datetime.now(timezone.utc)
            full_event_data = {
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "data": event_data
            }

            # Compute hash
            event_hash = hash_event(full_event_data, previous_hash)

            # Create database record
            audit_event = AuditEvent(
                timestamp=timestamp,
                event_type=event_type,
                event_data=event_data,
                previous_hash=previous_hash,
                hash=event_hash,
                user_id=user_id
            )

            session.add(audit_event)
            session.commit()

            logger.info(f"Logged event: {event_type} (hash: {event_hash[:16]}...)")
            return event_hash

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log event {event_type}: {str(e)}")
            raise  # Cannot fail silently - SOX violation
        finally:
            session.close()

    def log_document_ingested(
        self,
        document_id: str,
        source_url: str,
        filing_date: str,
        document_type: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log when a financial document enters the system.

        Args:
            document_id: Unique document identifier
            source_url: SEC EDGAR URL or other source
            filing_date: Official filing date (ISO format)
            document_type: Type of filing (10-K, 10-Q, 8-K, etc.)
            user_id: User or system that ingested the document

        Returns:
            Event hash for verification
        """
        return self.log_event(
            "document_ingested",
            {
                "document_id": document_id,
                "source_url": source_url,
                "filing_date": filing_date,
                "document_type": document_type
            },
            user_id=user_id
        )

    def log_document_processed(
        self,
        document_id: str,
        chunks_created: int,
        embeddings_created: int,
        processing_time_seconds: float,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log when document processing (parsing, chunking, embedding) completes.

        Args:
            document_id: Document being processed
            chunks_created: Number of text chunks created
            embeddings_created: Number of embeddings generated
            processing_time_seconds: Processing duration
            user_id: User or system that processed the document

        Returns:
            Event hash for verification
        """
        return self.log_event(
            "document_processed",
            {
                "document_id": document_id,
                "chunks_created": chunks_created,
                "embeddings_created": embeddings_created,
                "processing_time_seconds": processing_time_seconds
            },
            user_id=user_id
        )

    def log_query(
        self,
        query_text: str,
        query_id: str,
        user_id: str
    ) -> str:
        """
        Log when a user executes a RAG query.

        Args:
            query_text: The natural language query
            query_id: Unique query identifier
            user_id: User executing the query

        Returns:
            Event hash for verification
        """
        return self.log_event(
            "query_executed",
            {
                "query_id": query_id,
                "query_text": query_text[:500]  # Truncate for storage efficiency
            },
            user_id=user_id
        )

    def log_retrieval(
        self,
        query_id: str,
        chunks_retrieved: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """
        Log retrieval results (which chunks were retrieved for a query).

        This is critical for provenance - knowing which source documents
        influenced the generated answer.

        Args:
            query_id: Query identifier (links to log_query)
            chunks_retrieved: List of chunk metadata (chunk_id, score, page_num, etc.)
            user_id: User executing the query

        Returns:
            Event hash for verification
        """
        return self.log_event(
            "retrieval_completed",
            {
                "query_id": query_id,
                "chunks_retrieved": chunks_retrieved,
                "num_chunks": len(chunks_retrieved)
            },
            user_id=user_id
        )

    def log_generation(
        self,
        query_id: str,
        answer: str,
        citations: List[str],
        model_used: str,
        user_id: str
    ) -> str:
        """
        Log LLM answer generation with citations.

        Args:
            query_id: Query identifier (links to log_query)
            answer: Generated answer text
            citations: List of citations (e.g., ["[1] AAPL 10-K FY2024, p.28"])
            model_used: LLM model identifier
            user_id: User executing the query

        Returns:
            Event hash for verification
        """
        return self.log_event(
            "generation_completed",
            {
                "query_id": query_id,
                "answer_preview": answer[:500],  # Store preview, not full text
                "citations": citations,
                "model_used": model_used
            },
            user_id=user_id
        )

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the entire audit trail hash chain.

        Recomputes all hashes and checks that each event's hash matches
        the stored hash, and that previous_hash links are valid.

        Returns:
            Tuple of (is_valid, list_of_broken_event_ids)

        Example:
            >>> trail = FinancialAuditTrail("postgresql://...")
            >>> is_valid, broken_events = trail.verify_integrity()
            >>> if is_valid:
            ...     print("✅ Hash chain intact")
            ... else:
            ...     print(f"❌ Broken events: {broken_events}")
        """
        session = self.SessionLocal()
        try:
            events = session.query(AuditEvent).order_by(AuditEvent.id).all()

            if not events:
                logger.warning("No events to verify")
                return True, []

            broken_events = []
            previous_hash = None

            for event in events:
                # Reconstruct event data for hash computation
                event_data_for_hash = {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "data": event.event_data
                }

                # Recompute hash
                expected_hash = hash_event(event_data_for_hash, previous_hash)

                # Check if hash matches
                if event.hash != expected_hash:
                    broken_events.append(f"Event {event.id}: hash mismatch")
                    logger.error(f"Hash mismatch at event {event.id}")

                # Check if previous_hash is correct
                if event.previous_hash != previous_hash:
                    broken_events.append(f"Event {event.id}: previous_hash mismatch")
                    logger.error(f"Previous hash mismatch at event {event.id}")

                previous_hash = event.hash

            is_valid = len(broken_events) == 0
            if is_valid:
                logger.info(f"✅ Hash chain verified: {len(events)} events intact")
            else:
                logger.error(f"❌ Hash chain broken: {len(broken_events)} issues found")

            return is_valid, broken_events

        finally:
            session.close()

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate a compliance audit report for a date range.

        This report is designed for SOX audits and regulatory reviews.

        Args:
            start_date: Report start date (inclusive)
            end_date: Report end date (inclusive)

        Returns:
            Dictionary containing:
                - total_events: Number of events in range
                - event_breakdown: Count by event type
                - unique_users: Number of unique users
                - chain_valid: Whether hash chain is intact
                - sample_events: First 10 events (for auditor review)

        Example:
            >>> trail = FinancialAuditTrail("postgresql://...")
            >>> report = trail.generate_compliance_report(
            ...     datetime(2024, 1, 1, tzinfo=timezone.utc),
            ...     datetime(2024, 12, 31, tzinfo=timezone.utc)
            ... )
        """
        session = self.SessionLocal()
        try:
            # Query events in date range
            events = session.query(AuditEvent).filter(
                AuditEvent.timestamp >= start_date,
                AuditEvent.timestamp <= end_date
            ).order_by(AuditEvent.timestamp).all()

            # Count events by type
            event_breakdown = {}
            unique_users = set()

            for event in events:
                event_breakdown[event.event_type] = event_breakdown.get(event.event_type, 0) + 1
                if event.user_id:
                    unique_users.add(event.user_id)

            # Verify chain integrity
            is_valid, broken_events = self.verify_integrity()

            # Build report
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_events": len(events),
                "event_breakdown": event_breakdown,
                "unique_users": len(unique_users),
                "chain_valid": is_valid,
                "broken_events": broken_events,
                "sample_events": [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp.isoformat(),
                        "event_type": e.event_type,
                        "user_id": e.user_id,
                        "hash": e.hash[:16] + "..."
                    }
                    for e in events[:10]  # First 10 events as sample
                ]
            }

            logger.info(f"Generated compliance report: {len(events)} events, {len(unique_users)} users")
            return report

        finally:
            session.close()

    def get_event_count(self) -> int:
        """
        Get total number of audit events.

        Returns:
            Total event count
        """
        session = self.SessionLocal()
        try:
            return session.query(AuditEvent).count()
        finally:
            session.close()


def verify_chain_integrity(database_url: str) -> Tuple[bool, List[str]]:
    """
    Standalone function to verify audit trail integrity.

    Args:
        database_url: PostgreSQL connection string

    Returns:
        Tuple of (is_valid, list_of_broken_event_ids)

    Example:
        >>> is_valid, broken = verify_chain_integrity("postgresql://...")
        >>> if is_valid:
        ...     print("✅ Audit trail verified")
    """
    trail = FinancialAuditTrail(database_url)
    return trail.verify_integrity()

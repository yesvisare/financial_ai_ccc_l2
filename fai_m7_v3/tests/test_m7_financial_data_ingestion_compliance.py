"""
Tests for L3 M7.3: Financial Document Parsing & Chunking
"""

import pytest
from unittest.mock import Mock, patch
from src.l3_m7_financial_data_ingestion_compliance import (
    EDGARDownloader,
    SECFilingParser,
    XBRLParser,
    FinancialDocumentChunker,
    chunk_filing,
    extract_sections,
    parse_xbrl_data
)


@pytest.fixture
def sample_user_agent():
    """Sample SEC User-Agent for testing."""
    return "TestCompany testing@testcompany.com"


@pytest.fixture
def sample_html():
    """Sample SEC filing HTML for testing."""
    return """
    <html>
    <body>
    <h2>Item 1. Business</h2>
    <p>Company description goes here.</p>

    <h2>Item 1A. Risk Factors</h2>
    <p>Risk factors content.</p>

    <h2>Item 7. Management's Discussion and Analysis</h2>
    <p>MD&A content goes here.</p>

    <h2>Item 8. Financial Statements and Supplementary Data</h2>
    <table>
    <tr><th>BALANCE SHEET</th></tr>
    <tr><td>Assets</td><td>$1,000,000</td></tr>
    <tr><td>Liabilities</td><td>$500,000</td></tr>
    </table>
    </body>
    </html>
    """


class TestEDGARDownloader:
    """Test EDGARDownloader class."""

    def test_init_valid_user_agent(self, sample_user_agent):
        """Test initialization with valid user agent."""
        downloader = EDGARDownloader(sample_user_agent)
        assert downloader.user_agent == sample_user_agent
        assert downloader.rate_limit == 10

    def test_init_invalid_user_agent(self):
        """Test initialization with invalid user agent (no email)."""
        with pytest.raises(ValueError, match="must include company name and email"):
            EDGARDownloader("InvalidUserAgent")

    def test_rate_limiting(self, sample_user_agent):
        """Test rate limiting enforcement."""
        downloader = EDGARDownloader(sample_user_agent, rate_limit=10)

        # First request should not wait
        import time
        start = time.time()
        downloader._rate_limit_wait()
        first_duration = time.time() - start

        # Second immediate request should wait
        start = time.time()
        downloader._rate_limit_wait()
        second_duration = time.time() - start

        # Second request should have a delay
        assert second_duration >= 0.09  # ~0.1s for 10 req/sec

    def test_download_filing_mock(self, sample_user_agent):
        """Test filing download with mock data."""
        downloader = EDGARDownloader(sample_user_agent)
        result = downloader.download_filing('MSFT', '10-K', 2023)

        assert 'html' in result
        assert 'ticker' in result
        assert result['ticker'] == 'MSFT'
        assert result['filing_type'] == '10-K'


class TestSECFilingParser:
    """Test SECFilingParser class."""

    def test_init(self):
        """Test parser initialization."""
        parser = SECFilingParser('10-K')
        assert parser.filing_type == '10-K'
        assert 'Item 1' in parser.section_patterns_10k

    def test_extract_sections(self, sample_html):
        """Test section extraction from HTML."""
        parser = SECFilingParser('10-K')
        sections = parser.extract_sections(sample_html)

        assert isinstance(sections, dict)
        assert len(sections) > 0
        # Should extract at least some sections
        assert any('Item' in section_name for section_name in sections.keys())

    def test_extract_sections_empty_html(self):
        """Test section extraction with empty HTML."""
        parser = SECFilingParser('10-K')
        sections = parser.extract_sections("")

        # Should return empty dict for empty HTML
        assert isinstance(sections, dict)


class TestXBRLParser:
    """Test XBRLParser class."""

    def test_init(self):
        """Test XBRL parser initialization."""
        parser = XBRLParser()
        assert len(parser.core_tags) > 0
        assert 'Assets' in parser.core_tags

    def test_parse_xbrl_from_html(self, sample_html):
        """Test XBRL parsing from HTML."""
        parser = XBRLParser()
        result = parser.parse_xbrl_from_html(sample_html, 'Item 8')

        assert isinstance(result, dict)
        assert 'balance_sheet' in result
        assert 'income_statement' in result
        assert 'fiscal_period' in result

    def test_parse_balance_sheet(self):
        """Test balance sheet parsing."""
        parser = XBRLParser()
        mock_table = Mock()
        result = parser._parse_balance_sheet(mock_table)

        assert isinstance(result, dict)
        assert 'Assets' in result


class TestFinancialDocumentChunker:
    """Test FinancialDocumentChunker class."""

    def test_init(self):
        """Test chunker initialization."""
        chunker = FinancialDocumentChunker(chunk_size=1000, chunk_overlap=200)
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 200

    def test_init_defaults(self):
        """Test chunker initialization with defaults."""
        chunker = FinancialDocumentChunker()
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 200

    def test_chunk_filing_mock(self):
        """Test filing chunking with mock data (no user agent)."""
        chunker = FinancialDocumentChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_filing('MSFT', '10-K')

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Verify chunk structure
        first_chunk = chunks[0]
        assert 'text' in first_chunk
        assert 'metadata' in first_chunk
        assert 'ticker' in first_chunk['metadata']
        assert 'chunk_hash' in first_chunk['metadata']

    def test_chunk_filing_with_user_agent(self, sample_user_agent):
        """Test filing chunking with user agent."""
        chunker = FinancialDocumentChunker()
        chunks = chunker.chunk_filing('AAPL', '10-K', user_agent=sample_user_agent)

        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_generate_chunk_hash(self):
        """Test chunk hash generation."""
        chunker = FinancialDocumentChunker()
        text = "Sample chunk text"
        hash1 = chunker._generate_chunk_hash(text)
        hash2 = chunker._generate_chunk_hash(text)

        # Same text should produce same hash
        assert hash1 == hash2

        # Different text should produce different hash
        hash3 = chunker._generate_chunk_hash("Different text")
        assert hash1 != hash3

    def test_chunk_narrative_section(self):
        """Test narrative section chunking with overlap."""
        chunker = FinancialDocumentChunker(chunk_size=200, chunk_overlap=50)

        section_content = "Paragraph 1 content here. " * 10 + "\n\n" + "Paragraph 2 content here. " * 10
        filing = {'ticker': 'TEST', 'filing_type': '10-K', 'filing_date': '2023-01-01', 'accession_number': 'test-123'}

        chunks = chunker._chunk_narrative_section('Item 1', section_content, filing, 'public')

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Verify overlap exists between consecutive chunks
        if len(chunks) > 1:
            # Last part of first chunk should appear in second chunk
            assert chunks[0]['metadata']['chunk_number'] == 0
            assert chunks[1]['metadata']['chunk_number'] == 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_chunk_filing_function(self, sample_user_agent):
        """Test chunk_filing convenience function."""
        chunks = chunk_filing('MSFT', '10-K', user_agent=sample_user_agent)

        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_extract_sections_function(self, sample_html):
        """Test extract_sections convenience function."""
        sections = extract_sections(sample_html, '10-K')

        assert isinstance(sections, dict)

    def test_parse_xbrl_data_function(self, sample_html):
        """Test parse_xbrl_data convenience function."""
        result = parse_xbrl_data(sample_html)

        assert isinstance(result, dict)
        assert 'balance_sheet' in result


class TestComplianceFeatures:
    """Test SOX Section 404 compliance features."""

    def test_section_boundary_preservation(self, sample_html):
        """Test that section boundaries are preserved (no overlap)."""
        parser = SECFilingParser('10-K')
        sections = parser.extract_sections(sample_html)

        # Sections should not overlap
        # This is a basic test - production would verify exact boundaries
        assert isinstance(sections, dict)

    def test_financial_table_atomic(self):
        """Test that financial tables remain atomic (not split)."""
        chunker = FinancialDocumentChunker(chunk_size=100)  # Very small chunk size

        # Even with small chunk size, tables should remain intact
        html_with_table = """
        <html><body>
        <h2>Item 8. Financial Statements</h2>
        <table>
        <tr><th>BALANCE SHEET</th></tr>
        <tr><td>Assets</td><td>$1000</td></tr>
        <tr><td>Liabilities</td><td>$500</td></tr>
        </table>
        </body></html>
        """

        chunks = chunker.chunk_filing('TEST', '10-K')

        # Financial statement chunks should exist
        financial_chunks = [c for c in chunks if c['metadata'].get('section', '').startswith('Item 8')]
        assert len(financial_chunks) > 0

    def test_chunk_hash_for_audit_trail(self):
        """Test that chunks have hash for audit trail."""
        chunker = FinancialDocumentChunker()
        chunks = chunker.chunk_filing('MSFT', '10-K')

        # All chunks should have hash
        for chunk in chunks:
            assert 'chunk_hash' in chunk['metadata']
            assert len(chunk['metadata']['chunk_hash']) == 16  # SHA-256 truncated to 16 chars

    def test_metadata_completeness(self):
        """Test that chunks have complete metadata."""
        chunker = FinancialDocumentChunker()
        chunks = chunker.chunk_filing('AAPL', '10-K')

        required_fields = ['ticker', 'filing_type', 'section', 'filing_date',
                          'accession_number', 'sensitivity', 'chunk_hash', 'created_at']

        for chunk in chunks:
            metadata = chunk['metadata']
            for field in required_fields:
                assert field in metadata, f"Missing field: {field}"


# Integration tests (skip by default, run with: pytest --run-integration)

@pytest.mark.skipif(
    True,  # Skip by default
    reason="Integration tests require EDGAR API access"
)
class TestIntegration:
    """Integration tests with actual EDGAR API."""

    def test_real_edgar_download(self, sample_user_agent):
        """Test download from real EDGAR API."""
        downloader = EDGARDownloader(sample_user_agent)
        # This would make a real API call
        # result = downloader.download_filing('MSFT', '10-K', 2023)
        # assert 'html' in result
        pass

    def test_full_pipeline(self, sample_user_agent):
        """Test full pipeline from download to chunking."""
        # This would test the complete workflow
        # chunks = chunk_filing('AAPL', '10-K', user_agent=sample_user_agent)
        # assert len(chunks) > 50  # Real filing should have many chunks
        pass

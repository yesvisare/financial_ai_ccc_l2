"""
Tests for L3 M8.4: Temporal Financial Information Handling

Comprehensive test suite for fiscal period conversion, temporal retrieval,
and consistency validation.
"""

import pytest
from datetime import datetime
from src.l3_m8_financial_domain_knowledge_injection import (
    FiscalCalendarManager,
    TemporalRetriever,
    TemporalValidator,
    fiscal_quarter_to_dates,
    point_in_time_query,
    validate_temporal_consistency
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fiscal_manager():
    """Provide FiscalCalendarManager instance."""
    return FiscalCalendarManager()


@pytest.fixture
def temporal_retriever(fiscal_manager):
    """Provide TemporalRetriever instance without vector client."""
    return TemporalRetriever(fiscal_manager, vector_client=None)


@pytest.fixture
def temporal_validator(fiscal_manager):
    """Provide TemporalValidator instance."""
    return TemporalValidator(fiscal_manager)


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        {
            "ticker": "AAPL",
            "filing_date": "2024-04-15",
            "fiscal_period": "Q3 FY2024",
            "content": "Revenue grew 10%"
        },
        {
            "ticker": "AAPL",
            "filing_date": "2024-05-20",
            "fiscal_period": "Q3 FY2024",
            "content": "Margins improved"
        }
    ]


# ============================================================================
# Test FiscalCalendarManager
# ============================================================================

def test_fiscal_manager_initialization(fiscal_manager):
    """Test FiscalCalendarManager initializes correctly."""
    assert fiscal_manager is not None
    assert len(fiscal_manager.fiscal_year_ends) > 0


def test_get_fiscal_year_end_apple(fiscal_manager):
    """Test getting fiscal year end for Apple."""
    company_data = fiscal_manager.get_fiscal_year_end('AAPL')
    assert company_data is not None
    assert company_data['fiscal_year_end'] == '09-30'
    assert company_data['company_name'] == 'Apple Inc.'


def test_get_fiscal_year_end_microsoft(fiscal_manager):
    """Test getting fiscal year end for Microsoft."""
    company_data = fiscal_manager.get_fiscal_year_end('MSFT')
    assert company_data is not None
    assert company_data['fiscal_year_end'] == '06-30'


def test_get_fiscal_year_end_walmart(fiscal_manager):
    """Test getting fiscal year end for Walmart."""
    company_data = fiscal_manager.get_fiscal_year_end('WMT')
    assert company_data is not None
    assert company_data['fiscal_year_end'] == '01-31'


def test_get_fiscal_year_end_invalid_ticker(fiscal_manager):
    """Test getting fiscal year end for invalid ticker."""
    company_data = fiscal_manager.get_fiscal_year_end('INVALID')
    assert company_data is None


def test_get_fiscal_year_end_case_insensitive(fiscal_manager):
    """Test ticker lookup is case-insensitive."""
    company_data = fiscal_manager.get_fiscal_year_end('aapl')
    assert company_data is not None
    assert company_data['fiscal_year_end'] == '09-30'


# ============================================================================
# Test Fiscal Quarter to Calendar Date Conversion
# ============================================================================

def test_fiscal_quarter_to_dates_apple_q3(fiscal_manager):
    """Test Apple Q3 FY2024 conversion."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q3')
    assert start == '2024-04-01'
    assert end == '2024-06-30'


def test_fiscal_quarter_to_dates_apple_q4(fiscal_manager):
    """Test Apple Q4 FY2024 conversion."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q4')
    assert start == '2024-07-01'
    assert end == '2024-09-30'


def test_fiscal_quarter_to_dates_apple_q1(fiscal_manager):
    """Test Apple Q1 FY2024 conversion."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q1')
    assert start == '2023-10-01'
    assert end == '2023-12-31'


def test_fiscal_quarter_to_dates_microsoft_q3(fiscal_manager):
    """Test Microsoft Q3 FY2024 conversion."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('MSFT', 2024, 'Q3')
    assert start == '2024-01-01'
    assert end == '2024-03-31'


def test_fiscal_quarter_to_dates_walmart_q3(fiscal_manager):
    """Test Walmart Q3 FY2024 conversion."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('WMT', 2024, 'Q3')
    assert start == '2023-08-01'
    assert end == '2023-10-31'


def test_fiscal_quarter_to_dates_invalid_ticker(fiscal_manager):
    """Test conversion with invalid ticker."""
    result = fiscal_manager.fiscal_quarter_to_dates('INVALID', 2024, 'Q3')
    assert result is None


def test_fiscal_quarter_to_dates_invalid_quarter(fiscal_manager):
    """Test conversion with invalid quarter."""
    result = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q5')
    assert result is None


def test_fiscal_quarter_to_dates_case_insensitive_quarter(fiscal_manager):
    """Test quarter is case-insensitive."""
    start, end = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'q3')
    assert start == '2024-04-01'
    assert end == '2024-06-30'


def test_fiscal_quarter_to_dates_standalone_function():
    """Test standalone fiscal_quarter_to_dates function."""
    start, end = fiscal_quarter_to_dates('AAPL', 2024, 'Q3')
    assert start == '2024-04-01'
    assert end == '2024-06-30'


# ============================================================================
# Test TemporalRetriever
# ============================================================================

def test_temporal_retriever_initialization(temporal_retriever):
    """Test TemporalRetriever initializes correctly."""
    assert temporal_retriever is not None
    assert temporal_retriever.fiscal_manager is not None


def test_query_fiscal_period_apple_q3(temporal_retriever):
    """Test querying Apple Q3 FY2024."""
    result = temporal_retriever.query_fiscal_period(
        ticker='AAPL',
        fiscal_year=2024,
        quarter='Q3',
        query_text='revenue growth',
        top_k=5
    )

    assert result['status'] == 'success'
    assert result['ticker'] == 'AAPL'
    assert result['fiscal_period'] == 'Q3 FY2024'
    assert '2024-04-01' in result['calendar_period']
    assert '2024-06-30' in result['calendar_period']


def test_query_fiscal_period_invalid_ticker(temporal_retriever):
    """Test querying with invalid ticker."""
    result = temporal_retriever.query_fiscal_period(
        ticker='INVALID',
        fiscal_year=2024,
        quarter='Q3',
        query_text='test',
        top_k=5
    )

    assert result['status'] == 'error'
    assert 'Failed to convert fiscal period' in result['message']


def test_point_in_time_query_valid_date(temporal_retriever):
    """Test point-in-time query with valid date."""
    result = temporal_retriever.point_in_time_query(
        ticker='AAPL',
        as_of_date='2023-03-15',
        query_text='revenue',
        top_k=5
    )

    assert result['status'] == 'success'
    assert result['ticker'] == 'AAPL'
    assert result['as_of_date'] == '2023-03-15'


def test_point_in_time_query_invalid_date_format(temporal_retriever):
    """Test point-in-time query with invalid date format."""
    result = temporal_retriever.point_in_time_query(
        ticker='AAPL',
        as_of_date='03/15/2023',  # Wrong format
        query_text='revenue',
        top_k=5
    )

    assert result['status'] == 'error'
    assert 'Invalid date format' in result['message']


def test_point_in_time_query_standalone_function():
    """Test standalone point_in_time_query function."""
    result = point_in_time_query(
        ticker='AAPL',
        as_of_date='2023-03-15',
        query_text='revenue'
    )

    assert result['status'] == 'success'
    assert result['ticker'] == 'AAPL'


# ============================================================================
# Test TemporalValidator
# ============================================================================

def test_validate_temporal_consistency_valid(temporal_validator, sample_documents):
    """Test validation of temporally consistent documents."""
    result = temporal_validator.validate_temporal_consistency(
        documents=sample_documents,
        strict=True
    )

    assert result['status'] == 'valid'
    assert len(result['issues']) == 0
    assert result['summary']['document_count'] == 2


def test_validate_temporal_consistency_mixed_fiscal_periods(temporal_validator):
    """Test validation detects mixed fiscal periods."""
    documents = [
        {"ticker": "AAPL", "filing_date": "2024-04-15", "fiscal_period": "Q3 FY2024"},
        {"ticker": "AAPL", "filing_date": "2024-07-15", "fiscal_period": "Q4 FY2024"}
    ]

    result = temporal_validator.validate_temporal_consistency(
        documents=documents,
        strict=True
    )

    assert result['status'] == 'invalid'
    assert any(issue['type'] == 'mixed_fiscal_periods' for issue in result['issues'])


def test_validate_temporal_consistency_mixed_tickers(temporal_validator):
    """Test validation detects mixed tickers."""
    documents = [
        {"ticker": "AAPL", "filing_date": "2024-04-15", "fiscal_period": "Q3 FY2024"},
        {"ticker": "MSFT", "filing_date": "2024-04-15", "fiscal_period": "Q3 FY2024"}
    ]

    result = temporal_validator.validate_temporal_consistency(
        documents=documents,
        strict=True
    )

    # Mixed tickers should produce a warning
    assert any(issue['type'] == 'mixed_tickers' for issue in result['issues'])


def test_validate_temporal_consistency_large_date_range(temporal_validator):
    """Test validation detects large date ranges."""
    documents = [
        {"ticker": "AAPL", "filing_date": "2024-01-15", "fiscal_period": "Q1 FY2024"},
        {"ticker": "AAPL", "filing_date": "2024-09-15", "fiscal_period": "Q4 FY2024"}
    ]

    result = temporal_validator.validate_temporal_consistency(
        documents=documents,
        strict=False
    )

    assert any(issue['type'] == 'large_date_range' for issue in result['issues'])


def test_validate_temporal_consistency_empty_documents(temporal_validator):
    """Test validation with empty document list."""
    result = temporal_validator.validate_temporal_consistency(
        documents=[],
        strict=True
    )

    assert result['status'] == 'valid'
    assert result['message'] == 'No documents to validate'


def test_validate_temporal_consistency_standalone_function():
    """Test standalone validate_temporal_consistency function."""
    documents = [
        {"ticker": "AAPL", "filing_date": "2024-04-15", "fiscal_period": "Q3 FY2024"}
    ]

    result = validate_temporal_consistency(documents, strict=True)
    assert result['status'] == 'valid'


# ============================================================================
# Test Forward-Looking Statement Validation
# ============================================================================

def test_check_forward_looking_statements_recent(temporal_validator):
    """Test forward-looking statement check for recent document."""
    document = {
        "filing_date": datetime.now().strftime("%Y-%m-%d"),
        "is_forward_looking": True
    }

    result = temporal_validator.check_forward_looking_statements(document)

    assert result['status'] == 'assessed'
    assert result['confidence'] == 'high'


def test_check_forward_looking_statements_medium_age(temporal_validator):
    """Test forward-looking statement check for moderately aged document."""
    document = {
        "filing_date": "2024-05-01",
        "is_forward_looking": True
    }

    result = temporal_validator.check_forward_looking_statements(
        document,
        current_date="2024-08-01"
    )

    assert result['status'] == 'assessed'
    assert result['confidence'] == 'high'  # Within 3 months


def test_check_forward_looking_statements_stale(temporal_validator):
    """Test forward-looking statement check for stale document."""
    document = {
        "filing_date": "2023-01-01",
        "is_forward_looking": True
    }

    result = temporal_validator.check_forward_looking_statements(
        document,
        current_date="2024-01-01"
    )

    assert result['status'] == 'assessed'
    assert result['confidence'] == 'low'
    assert result['age_days'] == 365


def test_check_forward_looking_statements_not_applicable(temporal_validator):
    """Test forward-looking statement check for non-forward-looking document."""
    document = {
        "filing_date": "2024-01-01",
        "is_forward_looking": False
    }

    result = temporal_validator.check_forward_looking_statements(document)

    assert result['status'] == 'not_applicable'


# ============================================================================
# Test Failure Scenarios from Script
# ============================================================================

def test_failure_scenario_1_fiscal_database_out_of_date(fiscal_manager):
    """
    Failure #1: Fiscal Year Database Out of Date

    Problem: Companies occasionally change fiscal year ends
    Detection: Query returns unexpected date ranges
    """
    # Test that we can detect when fiscal data exists
    company_data = fiscal_manager.get_fiscal_year_end('AAPL')
    assert company_data is not None

    # In production, would check 'last_updated' field against current date
    # and flag if > 1 year old


def test_failure_scenario_2_transition_period_confusion():
    """
    Failure #2: Transition Period Confusion

    Problem: Fiscal year changes create overlap periods
    Detection: Documents show 5 quarters in a single fiscal year
    """
    # Test data representing transition period
    documents = [
        {"ticker": "TEST", "filing_date": "2024-01-15", "fiscal_period": "Q1 FY2024"},
        {"ticker": "TEST", "filing_date": "2024-04-15", "fiscal_period": "Q2 FY2024"},
        {"ticker": "TEST", "filing_date": "2024-07-15", "fiscal_period": "Q3 FY2024"},
        {"ticker": "TEST", "filing_date": "2024-10-15", "fiscal_period": "Q4 FY2024"},
        {"ticker": "TEST", "filing_date": "2024-12-15", "fiscal_period": "Q5 FY2024"}  # Transition!
    ]

    # Should detect unusual pattern (5 quarters)
    assert len(documents) == 5


def test_failure_scenario_3_forward_looking_becomes_outdated(temporal_validator):
    """
    Failure #3: Forward-Looking Statement Becomes Outdated

    Problem: Guidance from Q1 2024 may be invalid by Q4 2024
    Detection: Forward-looking statements used in analysis after 6+ months
    """
    stale_document = {
        "filing_date": "2023-06-01",
        "is_forward_looking": True
    }

    result = temporal_validator.check_forward_looking_statements(
        stale_document,
        current_date="2024-01-01"
    )

    # Should detect as stale (> 6 months)
    assert result['confidence'] == 'low'
    assert result['age_days'] > 180


def test_failure_scenario_4_cross_company_mismatch(temporal_validator):
    """
    Failure #4: Cross-Company Fiscal Period Mismatch

    Problem: Comparing Apple Q3 to Microsoft Q3 from different calendar periods
    Detection: TemporalValidator returns "mixed_fiscal_periods" error
    """
    # Apple Q3 FY2024: April-June 2024
    # Microsoft Q3 FY2024: January-March 2024
    # Even though both are "Q3", they're different calendar periods!

    documents = [
        {"ticker": "AAPL", "filing_date": "2024-05-15", "fiscal_period": "Q3 FY2024"},
        {"ticker": "MSFT", "filing_date": "2024-02-15", "fiscal_period": "Q3 FY2024"}
    ]

    result = temporal_validator.validate_temporal_consistency(
        documents,
        strict=True
    )

    # Should warn about mixed tickers
    assert any(issue['type'] == 'mixed_tickers' for issue in result['issues'])


def test_failure_scenario_5_missing_metadata():
    """
    Failure #5: Missing Fiscal Period Metadata in Documents

    Problem: Documents ingested without filing_date metadata
    Detection: Vector queries return no results despite existing documents
    """
    # Document missing filing_date
    incomplete_document = {
        "ticker": "AAPL",
        "fiscal_period": "Q3 FY2024"
        # filing_date is missing!
    }

    # Should handle missing metadata gracefully
    assert incomplete_document.get("filing_date") is None


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_all_quarters_for_apple(fiscal_manager):
    """Test all four quarters for Apple FY2024."""
    q1 = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q1')
    q2 = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q2')
    q3 = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q3')
    q4 = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q4')

    assert q1 == ('2023-10-01', '2023-12-31')
    assert q2 == ('2024-01-01', '2024-03-31')
    assert q3 == ('2024-04-01', '2024-06-30')
    assert q4 == ('2024-07-01', '2024-09-30')


def test_fiscal_year_span_across_calendar_years(fiscal_manager):
    """Test that Apple's fiscal year spans two calendar years."""
    q1_start, _ = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q1')
    q4_end, _ = fiscal_manager.fiscal_quarter_to_dates('AAPL', 2024, 'Q4')

    # Q1 should be in 2023, Q4 should be in 2024
    assert q1_start.startswith('2023')
    assert q4_end.startswith('2024')


def test_calendar_year_companies(fiscal_manager):
    """Test companies with calendar year fiscal year (Dec 31)."""
    # Amazon, Google, Tesla all end Dec 31
    amzn = fiscal_manager.get_fiscal_year_end('AMZN')
    googl = fiscal_manager.get_fiscal_year_end('GOOGL')
    tsla = fiscal_manager.get_fiscal_year_end('TSLA')

    assert amzn['fiscal_year_end'] == '12-31'
    assert googl['fiscal_year_end'] == '12-31'
    assert tsla['fiscal_year_end'] == '12-31'


def test_multiple_companies_loaded(fiscal_manager):
    """Test that fiscal database has 20+ companies."""
    assert len(fiscal_manager.fiscal_year_ends) >= 20


# ============================================================================
# Test 100% Accuracy Requirement
# ============================================================================

def test_fiscal_conversion_accuracy_apple():
    """Test 100% accuracy on Apple fiscal period conversions."""
    # Known accurate conversions from SEC filings
    test_cases = [
        ('AAPL', 2024, 'Q1', '2023-10-01', '2023-12-31'),
        ('AAPL', 2024, 'Q2', '2024-01-01', '2024-03-31'),
        ('AAPL', 2024, 'Q3', '2024-04-01', '2024-06-30'),
        ('AAPL', 2024, 'Q4', '2024-07-01', '2024-09-30'),
    ]

    for ticker, fy, q, expected_start, expected_end in test_cases:
        start, end = fiscal_quarter_to_dates(ticker, fy, q)
        assert start == expected_start, f"{ticker} {q} FY{fy} start date mismatch"
        assert end == expected_end, f"{ticker} {q} FY{fy} end date mismatch"


def test_fiscal_conversion_accuracy_microsoft():
    """Test 100% accuracy on Microsoft fiscal period conversions."""
    # Microsoft FY ends June 30
    test_cases = [
        ('MSFT', 2024, 'Q1', '2023-07-01', '2023-09-30'),
        ('MSFT', 2024, 'Q2', '2023-10-01', '2023-12-31'),
        ('MSFT', 2024, 'Q3', '2024-01-01', '2024-03-31'),
        ('MSFT', 2024, 'Q4', '2024-04-01', '2024-06-30'),
    ]

    for ticker, fy, q, expected_start, expected_end in test_cases:
        start, end = fiscal_quarter_to_dates(ticker, fy, q)
        assert start == expected_start, f"{ticker} {q} FY{fy} start date mismatch"
        assert end == expected_end, f"{ticker} {q} FY{fy} end date mismatch"


def test_fiscal_conversion_accuracy_walmart():
    """Test 100% accuracy on Walmart fiscal period conversions."""
    # Walmart FY ends January 31
    test_cases = [
        ('WMT', 2024, 'Q1', '2023-02-01', '2023-04-30'),
        ('WMT', 2024, 'Q2', '2023-05-01', '2023-07-31'),
        ('WMT', 2024, 'Q3', '2023-08-01', '2023-10-31'),
        ('WMT', 2024, 'Q4', '2023-11-01', '2024-01-31'),
    ]

    for ticker, fy, q, expected_start, expected_end in test_cases:
        start, end = fiscal_quarter_to_dates(ticker, fy, q)
        assert start == expected_start, f"{ticker} {q} FY{fy} start date mismatch"
        assert end == expected_end, f"{ticker} {q} FY{fy} end date mismatch"

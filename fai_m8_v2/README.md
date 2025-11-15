# L3 M8.2: Real-Time Financial Data Enrichment

## Overview

**From:** FinanceAI M8.2 - Real-Time Financial Data Enrichment
**Script:** [Augmented_Finance_AI_M8_2_RealTime_Financial_Data_Enrichment (1).md](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M8_2_RealTime_Financial_Data_Enrichment%20(1).md)

This module implements **real-time financial data enrichment** for RAG (Retrieval-Augmented Generation) systems in production financial applications. It integrates live market data APIs with intelligent caching strategies to balance cost, latency, and data freshness.

### The Problem

Imagine you're an investment analyst at 9:45 AM on earnings day. You query your RAG system: *"What's Apple's current stock price and how does it compare to analyst expectations?"*

Your system retrieves a document from yesterday that says Apple is trading at $185. But the market opened 15 minutes ago, and Apple is actually at $192—up 3.8% on better-than-expected earnings announced this morning.

**Your RAG system just gave you stale data.** In financial services, 15-minute-old information can cost millions in missed opportunities or lead to trading violations.

### The Solution

This module provides a **production-ready financial data enrichment layer** that:

- **Integrates live market data** from yfinance (free) with 15-minute delay or Bloomberg ($24K/year) for real-time data
- **Implements intelligent caching** with Redis using differentiated TTLs (1 min for prices, 24 hours for company info)
- **Handles market hours correctly** to prevent showing stale after-hours data as current
- **Degrades gracefully** when APIs fail, maintaining RAG system availability

## What You'll Learn

1. **Integrate live market data APIs** into your RAG system using yfinance (free) and understand when Bloomberg Terminal ($24K/year) is justified

2. **Implement intelligent caching strategies** with Redis, using differentiated TTLs for different data types (1 min for prices, 24 hours for company info)

3. **Handle market hours and data availability constraints** so you never show 4 PM Friday data on Monday morning as 'current'

4. **Build fallback mechanisms for API failures** that gracefully degrade service rather than crash your entire RAG system

## Key Concepts Covered

1. **Financial Data Enrichment** - Augmenting historical documents with current market data before generating RAG responses

2. **Data Freshness Hierarchy** - Understanding that different financial data types have different freshness requirements:
   - Tier 1: High-frequency trading (1-second refresh, Bloomberg $24K/year)
   - Tier 2: Analyst/advisory data (1-5 minute refresh, free APIs acceptable)
   - Tier 3: Fundamental company data (24-hour refresh, free SEC EDGAR)

3. **Intelligent Caching with Differentiated TTL** - Using Redis with different Time-To-Live values:
   - Stock prices: 60 seconds (real-time trading needs)
   - Company information: 86,400 seconds (fundamentals change slowly)
   - Market status: 300 seconds (open/closed status)

4. **Market Hours Awareness** - Detecting when markets are open/closed/pre-market/after-hours to prevent showing stale data as current

5. **Graceful Degradation** - Handling API failures without crashing the RAG system

6. **API Cost Optimization** - Achieving 60%+ cache hit rates to reduce API costs by 60%

7. **Cache-First Strategy** - Always check Redis (10ms latency) before calling external APIs (200ms latency)

## Architecture

```
┌─────────────────┐
│   User Query    │
│ "How is AAPL    │
│ performing?"    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     RAG Retrieval Engine            │
│  (Retrieves historical documents)   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Ticker Extraction                │
│  (AAPL, MSFT, GOOGL...)            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  FinancialDataEnricher              │
│                                     │
│  ┌──────────────┐  ┌─────────────┐│
│  │ Redis Cache  │  │ Market Hours││
│  │ (1-min TTL)  │  │  Detector   ││
│  └──────┬───────┘  └─────────────┘│
│         │ Cache Miss               │
│         ▼                          │
│  ┌──────────────┐  ┌─────────────┐│
│  │  yfinance    │  │  Fallback   ││
│  │   API        │  │  Handler    ││
│  └──────────────┘  └─────────────┘│
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Enriched Context                  │
│   (Historical + Current Data)       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│        LLM Generation               │
│  (Combines historical + current)    │
└─────────────────────────────────────┘
```

## How It Works

### Component 1: FinancialDataEnricher

The core enrichment engine that orchestrates caching, API calls, and data injection.

**Key Features:**
- **Cache-first strategy**: Checks Redis before calling APIs (10ms vs 200ms)
- **Differentiated TTL**: Stock prices (1 min), company info (24 hours), market status (5 min)
- **Graceful degradation**: API failures return fallback data instead of crashing

**Design Philosophy:**
```python
# Cache-first approach
cached = redis.get(f"market:{ticker}")
if cached:
    return cached  # Fast path: 10ms
else:
    data = yfinance.fetch(ticker)  # Slow path: 200ms
    redis.setex(f"market:{ticker}", 60, data)
    return data
```

### Component 2: Market Hours Detector

Prevents showing stale after-hours data as current.

**Why This Matters:**
- Showing Friday 4 PM data on Monday 10 AM as "current price" is misleading
- After-hours prices are less reliable (lower volume)
- Different exchanges have different hours (NYSE vs TSE vs LSE)

**Implementation:**
```python
# US market hours: 9:30 AM - 4:00 PM ET
if weekday >= 5:  # Weekend
    return "CLOSED"
elif (hour == 9 and minute >= 30) or (9 < hour < 16):
    return "OPEN"
elif 4 <= hour < 9 or (hour == 9 and minute < 30):
    return "PRE_MARKET"
elif 16 <= hour < 20:
    return "AFTER_HOURS"
else:
    return "CLOSED"
```

### Component 3: API Fallback Handler

Handles API failures and rate limits gracefully.

**Failure Handling:**
```python
try:
    stock_data = yfinance.fetch(ticker)
    return stock_data
except Exception as e:
    # Don't crash - return fallback data
    return {
        "ticker": ticker,
        "current_price": None,
        "error": "Market data temporarily unavailable",
        "fallback": True
    }
```

### Component 4: RAG Integration Layer

Combines historical documents with real-time market data.

**Workflow:**
1. User query arrives: "How is Apple performing?"
2. RAG retrieves historical documents about Apple
3. Extract ticker symbols (Apple → AAPL)
4. Enrich with real-time data from FinancialDataEnricher
5. Combine historical context + current data
6. Generate LLM response with both perspectives

## Installation

### Prerequisites

- Python 3.11+
- Redis (optional, for caching - 60% cost savings)
- OpenAI API key (optional, for full RAG features)
- Pinecone account (optional, for vector storage)

### Setup

```bash
# Clone repository
git clone <repo-url>
cd fai_m8_v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (all services are optional)
```

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REDIS_ENABLED` | No | Enable/disable Redis caching | `true` or `false` |
| `REDIS_HOST` | Conditional | Redis server hostname (if enabled) | `localhost` |
| `REDIS_PORT` | Conditional | Redis server port (if enabled) | `6379` |
| `REDIS_PASSWORD` | No | Redis password (if required) | `your_password` |
| `REDIS_DB` | No | Redis database number | `0` |
| `REDIS_URL` | No | Full Redis connection string (overrides above) | `redis://:pass@host:port/db` |
| `OPENAI_ENABLED` | No | Enable/disable OpenAI integration | `true` or `false` |
| `OPENAI_API_KEY` | Conditional | OpenAI API key (required if enabled) | `sk-...` |
| `PINECONE_ENABLED` | No | Enable/disable Pinecone vector DB | `true` or `false` |
| `PINECONE_API_KEY` | Conditional | Pinecone API key (required if enabled) | `your_api_key` |
| `PINECONE_ENVIRONMENT` | Conditional | Pinecone environment (required if enabled) | `us-west1-gcp` |
| `PINECONE_INDEX_NAME` | No | Pinecone index name | `financial-rag` |
| `LOG_LEVEL` | No | Logging level | `INFO`, `DEBUG`, `ERROR` |

### Service Configurations

**Minimal Setup (No External Services):**
```bash
# All services disabled - system works in "offline mode"
REDIS_ENABLED=false
OPENAI_ENABLED=false
PINECONE_ENABLED=false
```

**Recommended Setup (Redis Only):**
```bash
# 60% cost savings with Redis caching
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
OPENAI_ENABLED=false
PINECONE_ENABLED=false
```

**Full RAG Setup (All Services):**
```bash
# Complete RAG system with caching and vector storage
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

OPENAI_ENABLED=true
OPENAI_API_KEY=sk-your-key-here

PINECONE_ENABLED=true
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=financial-rag
```

## Usage

### As a Library

```python
from src.l3_m8_financial_domain_knowledge_injection import FinancialDataEnricher
import redis

# Initialize Redis client (optional)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create enricher
enricher = FinancialDataEnricher(redis_client)

# Enrich document with market data
result = enricher.enrich_with_market_data(
    text="Apple reported strong Q1 2024 earnings...",
    tickers=["AAPL"]
)

print(result)
# Output:
# {
#     'original_text': 'Apple reported strong Q1 2024 earnings...',
#     'enriched_data': {
#         'AAPL': {
#             'current_price': 192.45,
#             'change_percent': 3.2,
#             'market_cap': '2.97T',
#             'pe_ratio': 29.8,
#             'market_status': 'OPEN'
#         }
#     },
#     'cache_hit_rate': 65.5
# }
```

### As an API

#### Start the API Server

```bash
# Method 1: Using uvicorn directly
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using PowerShell script (Windows)
.\scripts\run_api.ps1

# Method 3: Direct Python execution
python app.py
```

#### API Endpoints

##### 1. POST /enrich - Enrich Document with Market Data

Enrich document text with real-time market data for specified tickers.

```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple reported strong Q1 2024 earnings with revenue of $94.9B",
    "tickers": ["AAPL"]
  }'
```

**Response:**
```json
{
  "original_text": "Apple reported strong Q1 2024 earnings...",
  "enriched_data": {
    "AAPL": {
      "ticker": "AAPL",
      "current_price": 192.45,
      "previous_close": 186.12,
      "change_percent": 3.4,
      "change_dollars": 6.33,
      "market_cap": "2.97T",
      "volume": 52847362,
      "pe_ratio": 29.8,
      "52_week_high": 199.62,
      "52_week_low": 164.08,
      "market_status": "OPEN",
      "data_source": "yfinance (15-min delay)"
    }
  },
  "enrichment_timestamp": "2024-11-15T10:30:00Z",
  "cache_hit_rate": 65.5
}
```

##### 2. POST /query - RAG Query with Auto-Enrichment

Execute RAG query with automatic ticker extraction and enrichment.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How is Apple performing today?",
    "context": "Apple Inc. is a technology company..."
  }'
```

##### 3. POST /extract-tickers - Extract Ticker Symbols

Extract stock ticker symbols from text.

```bash
curl -X POST http://localhost:8000/extract-tickers \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AAPL and MSFT are performing well in the tech sector"
  }'
```

**Response:**
```json
{
  "text": "AAPL and MSFT are performing well in the tech sector",
  "tickers": ["AAPL", "MSFT"]
}
```

##### 4. GET /market-status - Get Market Status

Get current US stock market status.

```bash
curl http://localhost:8000/market-status
```

**Response:**
```json
{
  "is_open": true,
  "status": "OPEN",
  "timestamp": "2024-11-15T14:30:00Z"
}
```

##### 5. GET /metrics - Get Service Metrics

Get enrichment service metrics for monitoring.

```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "cache_hit_rate": 65.5,
  "total_api_calls": 1247,
  "api_failure_rate": 2.3,
  "cache_hits": 817,
  "cache_misses": 430
}
```

##### 6. GET /ticker/{ticker} - Get Ticker Data

Get real-time data for a specific ticker.

```bash
curl http://localhost:8000/ticker/AAPL
```

##### 7. GET /health - Health Check

Health check endpoint for load balancers.

```bash
curl http://localhost:8000/health
```

## Testing

### Run All Tests

```bash
# Using pytest
pytest tests/ -v

# Using PowerShell script (Windows)
.\scripts\run_tests.ps1

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Tests

```bash
# Test enrichment functionality
pytest tests/test_m8_financial_domain_knowledge_injection.py::test_enrich_with_market_data

# Test caching
pytest tests/test_m8_financial_domain_knowledge_injection.py::test_cache_hit_rate

# Test market hours detection
pytest tests/test_m8_financial_domain_knowledge_injection.py::test_market_hours_detection
```

## Common Failure Cases

### Failure 1: Cache Hit Rate Suddenly Drops from 60% to 10%

**Symptom:**
- Yesterday: 60% cache hit rate, ₹500/day API costs
- Today: 10% cache hit rate, ₹3,000/day API costs
- No code changes

**Root Cause Analysis:**
```python
# Step 1: Check cache connectivity
>>> redis_client.ping()
PONG  # Redis is up, not a connection issue

# Step 2: Check cache keys
>>> redis_client.keys("market:*")
[]  # PROBLEM: No cached keys!

# Step 3: Check TTL configuration
>>> print(enricher.ttl_config["stock_price"])
0  # PROBLEM: TTL set to 0 (instant expiration)
```

**What Happened:**
Someone changed TTL config to 0 seconds during debugging and forgot to revert. Every cache write immediately expires.

**The Fix:**
```python
# Verify TTL is reasonable
TTL_CONFIG = {
    "stock_price": 60,  # Must be > 0
    "company_info": 86400
}

# Add validation in __init__
def __init__(self, redis_client, ttl_config):
    for key, ttl in ttl_config.items():
        if ttl <= 0:
            raise ValueError(f"TTL for {key} must be > 0, got {ttl}")
    self.ttl_config = ttl_config
```

**Debug Checklist:**
1. ✅ Redis connectivity (PING)
2. ✅ Cache keys present (KEYS pattern)
3. ✅ TTL values reasonable (> 0)
4. ✅ Cache writes succeeding (check logs)

---

### Failure 2: API Returns None for Valid Tickers

**Symptom:**
```python
>>> enricher.enrich_with_market_data("text", ["AAPL"])
{'AAPL': {'fallback': True, 'error': 'Market data temporarily unavailable'}}
```

Even though AAPL is a valid ticker and yfinance is working.

**Root Cause Analysis:**
```python
# Step 1: Test yfinance directly
>>> import yfinance as yf
>>> stock = yf.Ticker("AAPL")
>>> info = stock.info
>>> info.get('currentPrice')
None  # PROBLEM: Key is 'regularMarketPrice', not 'currentPrice'

# Step 2: Inspect available keys
>>> list(info.keys())
['regularMarketPrice', 'regularMarketOpen', 'marketCap', ...]
```

**What Happened:**
Yahoo Finance changed their API response keys. 'currentPrice' no longer exists—it's now 'regularMarketPrice'.

**The Fix:**
```python
# Robust key extraction with fallbacks
def _get_current_price(self, info: Dict) -> Optional[float]:
    # Try multiple keys (API schema changes over time)
    price_keys = ['currentPrice', 'regularMarketPrice', 'price']

    for key in price_keys:
        price = info.get(key)
        if price and price > 0:
            return price

    # No valid price found
    return None
```

**Debug Checklist:**
1. ✅ Test API directly (outside your code)
2. ✅ Inspect actual response keys
3. ✅ Check for API schema changes
4. ✅ Add fallback key names

---

### Failure 3: Enrichment Latency Spikes from 50ms to 2 seconds

**Symptom:**
- P95 latency yesterday: 50ms
- P95 latency today: 2,000ms
- Cache hit rate: 65% (normal)

**Root Cause Analysis:**
```python
# Step 1: Check where time is spent
import time

def enrich_with_market_data(self, text, tickers):
    for ticker in tickers:
        t1 = time.time()
        cached = self._get_from_cache(f"market:{ticker}")
        print(f"Cache GET {ticker}: {(time.time() - t1) * 1000:.2f}ms")

        if not cached:
            t2 = time.time()
            stock_data = self._fetch_stock_data(ticker)
            print(f"API call {ticker}: {(time.time() - t2) * 1000:.2f}ms")

# Output:
# Cache GET AAPL: 2.1ms
# Cache GET MSFT: 1.9ms
# Cache GET GOOGL: 1800ms  <- PROBLEM!
# API call GOOGL: 250ms
```

**What Happened:**
Redis cache GET for GOOGL took 1.8 seconds. Root cause: Redis instance was out of memory and swapping to disk.

**The Fix:**
```python
# Monitor Redis memory usage
>>> redis_client.info('memory')
{
    'used_memory_human': '4.95G',
    'maxmemory_human': '5.00G',  # PROBLEM: At max memory
    'mem_fragmentation_ratio': 1.2,
    'eviction_policy': 'allkeys-lru'
}

# Solution 1: Increase Redis memory (scale up)
# Solution 2: Reduce cache size (shorter TTLs)
# Solution 3: Use LRU eviction (already set, but not enough)
```

**Debug Checklist:**
1. ✅ Profile each operation (time.time() around calls)
2. ✅ Check Redis memory usage
3. ✅ Monitor Redis latency (INFO stats)
4. ✅ Check network latency to Redis

---

### Failure 4: Rate Limited by yfinance at Peak Hours

**Symptom:**
- System works fine 8 AM - 10 AM
- 10 AM - 12 PM: Frequent API failures
- Error: `HTTP 429: Too Many Requests`

**Root Cause Analysis:**
```python
# Check API call volume over time
>>> import collections
>>> call_times = enricher.api_call_log
>>> hourly_counts = collections.Counter([t.hour for t in call_times])
>>> print(hourly_counts)
{8: 500, 9: 1200, 10: 2500, 11: 2800}  # PROBLEM: 2500+ calls/hour

# yfinance limit: ~2000 calls/hour
```

**What Happened:**
Market opens at 9:30 AM. All analysts query the system simultaneously. API calls spike from 500/hour to 2,800/hour.

**The Fix:**
```python
# Solution 1: Pre-fetch popular stocks at 9:25 AM (before market open)
def pre_fetch_popular_stocks(self):
    popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]

    for ticker in popular_tickers:
        self._fetch_stock_data(ticker)  # Warm the cache

    logger.info("Pre-fetched 6 popular stocks before market open")

# Solution 2: Upgrade to paid API (Alpha Vantage Premium: $50/month)
# Supports 75 calls/minute = 4,500 calls/hour

# Solution 3: Increase cache TTL during peak hours
if 9 <= hour <= 12:  # Peak hours
    self.ttl_config["stock_price"] = 120  # 2 minutes
else:
    self.ttl_config["stock_price"] = 60  # 1 minute
```

**Debug Checklist:**
1. ✅ Track API call volume by hour
2. ✅ Identify rate limit thresholds
3. ✅ Pre-fetch popular stocks before peak
4. ✅ Consider paid API tiers

## Decision Card

### When to Use Real-Time Enrichment

#### Use Case 1: Investment Research & Analysis
- **User asks:** "How is Microsoft performing this quarter?"
- **Need:** Combine historical earnings with current stock price
- **Freshness requirement:** 5-15 minute delay acceptable
- **API choice:** yfinance (free, 15-min delay) ✅

#### Use Case 2: Portfolio Performance Tracking
- **User asks:** "What's the current value of my portfolio?"
- **Need:** Real-time prices for 10-50 stocks
- **Freshness requirement:** <5 minutes
- **API choice:** Polygon.io ($29/month for real-time) or yfinance with 1-min cache

#### Use Case 3: Financial News Analysis
- **User asks:** "How did the market react to Apple's earnings?"
- **Need:** Combine news articles with stock price movements
- **Freshness requirement:** 15-minute delay acceptable
- **API choice:** yfinance + Alpha Vantage (free)

---

### When NOT to Use Real-Time Enrichment

#### Scenario 1: Historical Analysis
- **User asks:** "How did Apple perform in 2020?"
- **No need for current prices**—historical data is sufficient
- **Don't enrich:** Unnecessary API calls

#### Scenario 2: Company Research (Non-Price Questions)
- **User asks:** "Who is Apple's CEO?"
- **Static information** doesn't change daily
- **Don't enrich:** Use cached company info (24-hour TTL)

#### Scenario 3: Regulatory Document Analysis
- **User asks:** "What does the 10-K say about risk factors?"
- **Document analysis**, not market data
- **Don't enrich:** Wastes API calls

---

### Decision Framework

```
START
    ↓
Does the query mention current/today/now?
    YES → Enrich with real-time data
    NO ↓

Does the query ask about price/performance/stock?
    YES → Check if historical or current context
        CURRENT → Enrich
        HISTORICAL → Don't enrich
    NO ↓

Is the query time-sensitive (portfolio value, trading)?
    YES → Enrich with real-time data
    NO → Don't enrich
```

---

### Cost Estimation - Concrete Examples

#### Small Investment Advisory Firm (20 users, 50 stocks tracked, 5K docs)

**Usage:**
- 20 analysts × 10 queries/day = 200 queries/day
- Average 3 tickers per query = 600 ticker lookups/day
- Cache hit rate: 60% → 240 API calls/day = 7,200 calls/month

**Infrastructure:**
- Pinecone: ₹850/month (Serverless, 100K vectors)
- Redis: ₹500/month (Railway, 1GB cache)
- OpenAI API: ₹2,500/month (GPT-4, 200K tokens/day)
- yfinance: ₹0 (free)
- **Total: ₹3,850/month** (≈$48 USD)

**Per User Cost:** ₹192/month per analyst

---

#### Medium Hedge Fund (100 users, 200 stocks tracked, 50K docs)

**Usage:**
- 100 analysts × 15 queries/day = 1,500 queries/day
- Average 4 tickers per query = 6,000 ticker lookups/day
- Cache hit rate: 65% → 2,100 API calls/day = 63,000 calls/month

**Infrastructure:**
- Pinecone: ₹4,200/month (Standard, 1M vectors)
- Redis: ₹2,000/month (AWS ElastiCache, 5GB cache)
- OpenAI API: ₹12,000/month (GPT-4, 1M tokens/day)
- Alpha Vantage: ₹4,200/month (Premium, 75 calls/min)
- **Total: ₹22,400/month** (≈$270 USD)

**Per User Cost:** ₹224/month per analyst

**Upgrade Trigger:** When yfinance rate limits become problematic (>2K calls/hour). At this scale, paid API justifies cost.

---

#### Large Investment Bank (500 users, 500 stocks tracked, 200K docs)

**Usage:**
- 500 analysts × 20 queries/day = 10,000 queries/day
- Average 5 tickers per query = 50,000 ticker lookups/day
- Cache hit rate: 70% → 15,000 API calls/day = 450,000 calls/month

**Infrastructure:**
- Pinecone: ₹16,800/month (Enterprise, 5M vectors)
- Redis: ₹8,400/month (AWS ElastiCache Cluster, 25GB)
- OpenAI API: ₹42,000/month (GPT-4, 5M tokens/day)
- Bloomberg API: ₹1,00,000/month ($24K/year ÷ 12 + API fees)
- **Total: ₹1,67,200/month** (≈$2,000 USD)

**Per User Cost:** ₹334/month per analyst (economies of scale)

**Upgrade Justification:** At this scale, Bloomberg's real-time data, institutional coverage, and reliability justify the $24K/year cost. 15-minute delay is unacceptable for 500-person trading desk.

---

### ROI Calculation

**Medium Hedge Fund Example:**

**Cost with enrichment:** ₹22,400/month

**Value delivered:**
- Analysts save 30 min/day not manually checking stock prices
  - 100 analysts × 30 min × ₹2,000/hour = ₹1,00,000/month saved
- Faster decision-making (5 min vs 30 min per analysis)
  - Value: Capture 10% more trading opportunities = ₹5L-10L/month additional returns

**ROI:** (₹1,00,000 + ₹5,00,000) / ₹22,400 = **27X return**

Even conservative estimates (₹50,000 value) give 2X ROI—easily justifiable.

## Production Considerations

### Performance

- **Target cache hit rate:** 60%+ (achieves 60% API cost reduction)
- **Target latency:** P95 < 100ms for cached requests, P95 < 300ms for uncached
- **API rate limits:** yfinance ~2,000 calls/hour, plan pre-fetching for peak hours
- **Redis memory:** Monitor usage, scale before hitting 80% capacity

### Security

- **API keys:** Store in environment variables, never commit to Git
- **Redis authentication:** Use passwords in production
- **HTTPS only:** Enforce TLS for API endpoints
- **Rate limiting:** Implement per-user rate limits to prevent abuse

### Compliance

- **Data freshness disclaimers:** Clearly indicate 15-minute delay for free APIs
- **Audit trails:** Log all enrichment requests for compliance
- **SEC regulations:** Material event disclosure within 4 business days
- **Privacy:** Don't cache PII, implement data retention policies

## Examples

### Example 1: Basic Enrichment

```python
from src.l3_m8_financial_domain_knowledge_injection import FinancialDataEnricher

# No Redis - minimal setup
enricher = FinancialDataEnricher(redis_client=None)

# Enrich document
result = enricher.enrich_with_market_data(
    text="Apple reported $94.9B revenue in Q1 2024",
    tickers=["AAPL"]
)

print(f"Current price: ${result['enriched_data']['AAPL']['current_price']}")
print(f"Change: {result['enriched_data']['AAPL']['change_percent']}%")
```

### Example 2: With Redis Caching

```python
import redis
from src.l3_m8_financial_domain_knowledge_injection import FinancialDataEnricher

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create enricher with caching
enricher = FinancialDataEnricher(redis_client)

# First call - cache miss (200ms)
result1 = enricher.enrich_with_market_data("text", ["AAPL"])

# Second call within 60 seconds - cache hit (10ms)
result2 = enricher.enrich_with_market_data("text", ["AAPL"])

# Check metrics
metrics = enricher.get_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1f}%")
```

### Example 3: RAG Integration

```python
from src.l3_m8_financial_domain_knowledge_injection import FinancialRAGWithEnrichment

# Initialize RAG system
rag = FinancialRAGWithEnrichment(redis_client=None)

# Execute query with auto-enrichment
result = rag.query(
    user_query="How is Apple performing today?",
    context="Apple Inc. reported strong Q1 2024 earnings..."
)

print(f"Tickers found: {result['tickers_found']}")
print(f"Enrichment: {result['enrichment']}")
```

### Example 4: Market Hours Check

```python
from src.l3_m8_financial_domain_knowledge_injection import is_market_open

# Check if market is currently open
if is_market_open():
    print("✅ Market is OPEN - real-time data is current")
else:
    print("⚠️ Market is CLOSED - showing last close prices")
```

## Resources

- **Script:** [Augmented_Finance_AI_M8_2_RealTime_Financial_Data_Enrichment (1).md](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M8_2_RealTime_Financial_Data_Enrichment%20(1).md)
- **yfinance Documentation:** https://pypi.org/project/yfinance/
- **Redis Documentation:** https://redis.io/docs/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **OpenAI API:** https://platform.openai.com/docs/
- **Pinecone Documentation:** https://docs.pinecone.io/

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

This is an educational module from TechVoyageHub's Finance AI curriculum. For questions or suggestions, please open an issue in the repository.

---

**Production-Ready Features:**
- ✅ Graceful degradation for API failures
- ✅ Intelligent caching with differentiated TTLs
- ✅ Market hours awareness
- ✅ Comprehensive error handling
- ✅ Prometheus-compatible metrics
- ✅ Full test coverage
- ✅ API documentation (Swagger/ReDoc)
- ✅ Environment-based configuration
- ✅ Docker-ready (add Dockerfile)

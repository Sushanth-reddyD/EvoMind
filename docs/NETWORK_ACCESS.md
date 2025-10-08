# EvoMind Network Access Guide

## 🔒 Security Model

EvoMind uses a **secure-by-default** sandbox model that blocks network access to prevent:
- Unauthorized data exfiltration
- Malicious API calls
- System compromise via network attacks

## ❌ Tasks That Require Network (Currently Blocked)

These tasks will fail validation:

1. **Web Scraping**
   - Fetching HTML from websites
   - Parsing web pages
   - Screen scraping

2. **API Calls**
   - REST API requests
   - HTTP GET/POST operations
   - Web service integrations

3. **Network Operations**
   - Socket connections
   - URL parsing with urllib/requests
   - DNS lookups

## ✅ Alternative: Non-Network Tasks

Try these instead:

### Data Processing
```
Create a function that takes a list of dictionaries representing users (name, age, salary) and returns:
1. Average salary by age group (18-30, 31-50, 51+)
2. Top 5 earners
3. Statistical summary (mean, median, std deviation)
```

### Text Analysis
```
Build a text analyzer that:
1. Counts word frequency
2. Finds the longest word
3. Calculates average word length
4. Identifies unique words
5. Returns results as a structured dictionary
```

### Mathematical Computation
```
Create a statistical calculator that accepts a list of numbers and returns:
1. Mean, median, mode
2. Standard deviation and variance
3. Min, max, range
4. Quartiles (Q1, Q2, Q3)
5. Outliers using IQR method
```

### Data Transformation
```
Build a data transformer that:
1. Accepts JSON array of records
2. Filters records based on conditions
3. Transforms field values (uppercase, formatting)
4. Sorts by multiple fields
5. Exports as formatted JSON
```

### Algorithm Implementation
```
Create a sorting algorithm visualizer that:
1. Implements bubble sort, quick sort, merge sort
2. Tracks number of comparisons and swaps
3. Returns step-by-step execution trace
4. Compares performance metrics
```

## 🔓 Enabling Network Access (Advanced)

### For Development/Testing Only

If you need to test network-based tools, you can enable network access:

#### Option 1: Modify Security Policy

```python
from evomind.sandbox.policies import SecurityPolicy

# Create permissive policy
security_policy = SecurityPolicy(
    network_enabled=True,
    allowed_hosts={"api.example.com", "jsonplaceholder.typicode.com"}
)
```

#### Option 2: Use Allow-List Approach

```python
# In evomind/codegen/validators.py
validator = StaticValidator(allow_network=True)
```

#### Option 3: Disable Validator for Testing

```python
# For testing only - DANGEROUS!
generator = CodeGenerator(use_llm=True, allow_network=True)
```

### ⚠️ Security Warnings

Enabling network access:
- ✅ Allows URL/HTTP operations
- ⚠️ Can leak sensitive data
- ⚠️ May access malicious sites
- ⚠️ Bypasses sandbox protection

**Only use in controlled environments!**

## 🎯 Recommended Workflow

### 1. Start with Non-Network Tasks
Test the system with safe, local computation tasks

### 2. Use Mock Data
Instead of fetching from APIs, use sample JSON data:

```python
# Instead of: requests.get('https://api.example.com/users')
# Use mock data:
mock_users = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25}
]
```

### 3. Separate Data Fetch from Processing
1. Manually fetch data outside EvoMind
2. Process with EvoMind tools
3. Keeps sandbox secure

### 4. Use Template Mode for Network Tasks
Template mode is safer for network operations as code is human-written

## 📊 Example: Safe Data Analysis Task

Instead of:
```
❌ Create a web scraper that fetches and analyzes product prices from Amazon
```

Try:
```
✅ Create a price analyzer that:
- Accepts a list of product dictionaries (name, price, category, rating)
- Calculates average price per category
- Finds best-rated products under $50
- Identifies price outliers
- Returns insights as structured JSON
```

Then manually provide the data:
```python
products = [
    {"name": "Widget A", "price": 29.99, "category": "Tools", "rating": 4.5},
    {"name": "Gadget B", "price": 49.99, "category": "Electronics", "rating": 4.8},
    # ... more products
]
```

## 🚀 Quick Success Tips

1. **Focus on computation, not I/O**
   - ✅ Transform data
   - ✅ Calculate statistics
   - ✅ Implement algorithms
   - ❌ Fetch from web
   - ❌ Save to disk

2. **Use built-in modules only**
   - ✅ json, re, math, datetime
   - ✅ collections, itertools
   - ❌ requests, urllib
   - ❌ os, subprocess

3. **Test incrementally**
   - Start with simple tasks
   - Add complexity gradually
   - Verify each step

4. **Read error messages**
   - "Forbidden import" → Use allowed modules
   - "Network operation detected" → Remove network code
   - "Syntax error" → Check generated code

## 📝 Sample Success Tasks

Copy and paste these into the UI:

```
Task 1: JSON Processor
Create a function that validates and processes JSON data with schema validation, type checking, and error reporting.

Task 2: Statistical Analyzer
Build a comprehensive statistical analysis tool that calculates descriptive statistics, detects outliers, and generates summary reports.

Task 3: Data Filter
Create a flexible data filtering system that supports multiple conditions, field transformations, and result aggregation.

Task 4: Text Parser
Build a text parsing tool that extracts patterns, counts occurrences, and analyzes text structure.

Task 5: Algorithm Comparator
Implement multiple sorting algorithms and compare their performance characteristics with detailed metrics.
```

Each of these will work perfectly without network access!

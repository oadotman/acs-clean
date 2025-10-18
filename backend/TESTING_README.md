# Platform-Specific Ad Generation Testing Framework

This comprehensive testing framework validates all aspects of the platform-specific ad generation system across 6 platforms: Facebook, Instagram, Google Ads, LinkedIn, Twitter/X, and TikTok.

## 📋 Test Suite Overview

### 1. **Test Data** (`test_data_comprehensive.py`)
- **3-5 sample ads per platform** covering various scenarios:
  - Short ads (single sentence)
  - Long ads (multiple sentences)  
  - Ads with no clear CTA
  - Ads with multiple CTAs
  - Ads with poor grammar
  - Already well-written ads
  - Platform-specific edge cases

### 2. **Platform Validation Tests** (`test_platform_validation.py`)
- Parser field extraction accuracy
- Character limit compliance  
- Template phrase detection
- Grammar validation
- Confidence score accuracy
- Retry logic functionality
- Output quality standards

### 3. **Output Quality Tests** (`test_output_quality.py`)
- Content structure validation
- Character limit enforcement
- Language quality assessment
- Platform-specific requirements
- Confidence score accuracy
- Template phrase avoidance

### 4. **Frontend Integration Tests** (`test_frontend_integration.py`)
- API response format validation
- Frontend component compatibility
- Platform-specific field display
- Character counter accuracy
- Copy-to-clipboard functionality
- Platform badge display
- Error handling verification

### 5. **Performance & Edge Case Tests** (`test_performance_edge_cases.py`)
- Performance benchmarks across platforms
- Memory usage monitoring
- Concurrent request handling
- Extreme input validation
- Error recovery mechanisms
- Timeout handling
- Resource cleanup

## 🚀 Quick Start

### Run All Tests (Recommended)
```bash
# With OpenAI API key for complete testing
python run_all_tests.py --api-key YOUR_OPENAI_API_KEY

# Without API key (limited testing)
python run_all_tests.py

# Custom API URL and output file
python run_all_tests.py --api-key YOUR_KEY --api-url http://localhost:3000 --output my_report.txt

# Save detailed JSON results
python run_all_tests.py --api-key YOUR_KEY --json-output detailed_results.json
```

### Run Individual Test Suites

#### Basic Validation (No API key needed)
```bash
python test_platform_validation.py
```

#### Platform Validation (Requires API key)
```bash
python test_platform_validation.py YOUR_OPENAI_API_KEY
```

#### Output Quality Tests (Requires API key)
```bash
python test_output_quality.py YOUR_OPENAI_API_KEY
```

#### Frontend Integration Tests
```bash
python test_frontend_integration.py
# Or with custom API URL:
python test_frontend_integration.py http://localhost:3000
```

#### Performance Tests
```bash
python test_performance_edge_cases.py YOUR_OPENAI_API_KEY
# Or API-only testing:
python test_performance_edge_cases.py "" http://localhost:8000
```

## 📊 Understanding Test Results

### Success Criteria
- **Basic Validation**: All test data structures valid
- **Platform Tests**: >80% success rate per platform
- **Quality Tests**: >70% average quality score + >80% test success
- **Integration Tests**: >80% API compatibility success
- **Performance Tests**: >80% success rate + reasonable resource usage

### Report Files Generated
- `master_test_report.txt` - Comprehensive summary
- `platform_validation_report.txt` - Platform-specific details
- `output_quality_report.txt` - Quality metrics
- `frontend_integration_report.txt` - API compatibility
- `performance_edge_case_report.txt` - Performance analysis

## 🎯 Test Coverage

### Platform Coverage
- ✅ **Facebook**: Headlines, body text, CTAs
- ✅ **Instagram**: Body text, hashtags, emojis
- ✅ **Google Ads**: Multiple headlines, descriptions
- ✅ **LinkedIn**: Professional tone, business value
- ✅ **Twitter/X**: Character limits, engagement
- ✅ **TikTok**: Trendy language, hooks

### Validation Coverage
- **Parser Accuracy**: Field extraction per platform
- **Character Limits**: Platform-specific enforcement
- **Content Quality**: Grammar, originality, engagement
- **API Compatibility**: Request/response formats
- **Performance**: Speed, memory, concurrency
- **Error Handling**: Graceful failure recovery

## 🔧 Configuration

### Environment Setup
1. **Backend Server**: Ensure API server running on configured port
2. **OpenAI API Key**: Set in environment or pass as parameter
3. **Dependencies**: Install required packages (requests, psutil, asyncio)

### Customization Options
```python
# Modify test_data_comprehensive.py to add custom test cases
PLATFORM_TEST_DATA['your_platform'] = {
    'short_ads': ['Your test ads here'],
    # ... more categories
}

# Adjust quality thresholds in test files
QUALITY_CRITERIA = {
    'minimum_confidence_score': 60,  # Adjust as needed
    'forbidden_templates': [...],    # Add your templates
}
```

## 📈 Interpreting Results

### Overall Status Indicators
- 🟢 **EXCELLENT** (95%+): Production ready
- 🟡 **GOOD** (85-94%): Minor issues to address  
- 🟠 **NEEDS WORK** (70-84%): Some significant issues
- 🔴 **CRITICAL** (<70%): Major problems require immediate attention

### Platform-Specific Analysis
Each platform gets individual scoring:
- **Parser Tests**: Field extraction accuracy
- **Validation Tests**: Content compliance  
- **Quality Tests**: Generated content standards
- **Performance Tests**: Response time benchmarks

## 🚨 Common Issues & Solutions

### Import Errors
```bash
# Ensure all service modules are available
ModuleNotFoundError: No module named 'app.services'
```
**Solution**: Run tests from backend directory with proper Python path

### API Connection Failures
```bash
# Connection refused errors
ConnectionError: Cannot connect to API
```
**Solution**: Ensure backend server is running on correct port

### OpenAI API Issues
```bash
# Authentication or quota errors  
OpenAI API Error: Insufficient quota
```
**Solution**: Check API key validity and account limits

### Memory/Performance Warnings
```bash
# High memory usage detected
Memory growth: 150MB
```
**Solution**: Review generation logic for memory leaks

## 📝 Test Development

### Adding New Platforms
1. Add platform data to `test_data_comprehensive.py`
2. Update expected parsing results
3. Add platform-specific validation logic
4. Include in frontend integration tests

### Adding New Test Categories  
1. Create test data for new scenarios
2. Implement validation logic in appropriate test file
3. Update master test runner to include new tests
4. Add to reporting and analysis

### Custom Quality Metrics
```python
# Add to test_output_quality.py
def _assess_custom_metric(self, result: Dict, platform_id: str):
    # Your custom quality assessment logic
    pass
```

## 🎬 Example Test Run
```bash
$ python run_all_tests.py --api-key sk-...

🚀 Starting comprehensive platform-specific ad generation tests...
================================================================================

🔍 PHASE 1: Basic Validation Tests
--------------------------------------------------
✅ Basic validation: 36/36 tests passed

🎯 PHASE 2: Platform Validation Tests
--------------------------------------------------
🚀 Starting comprehensive platform validation tests...
📊 Testing platform: facebook
📊 Testing platform: instagram
📊 Testing platform: google_ads
📊 Testing platform: linkedin  
📊 Testing platform: twitter_x
📊 Testing platform: tiktok
✅ Completed all tests in 45.2s
📈 Results: 156/180 tests passed

[... continued for all test phases ...]

🎯 EXECUTIVE SUMMARY:
   Overall Success Rate: 89.2% (445/499 tests)
   Test Suites Passed: 4/5
   Total Execution Time: 127.8s
   Status: 🟡 GOOD - Minor Issues

✅ Tests completed successfully!
```

This comprehensive testing framework ensures your platform-specific ad generation system meets all quality, performance, and compatibility requirements across all supported platforms.
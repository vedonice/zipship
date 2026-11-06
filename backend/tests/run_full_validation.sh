#!/bin/bash
# Full test suite validation script with coverage reporting

set -e

echo "════════════════════════════════════════════════════════"
echo "  ZipShip - Full Test Suite Validation"
echo "════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize counters
TESTS_PASSED=0
TESTS_FAILED=0
COVERAGE_THRESHOLD=85

echo "📋 Step 1: Running Unit Tests..."
echo "─────────────────────────────────"
if python -m pytest tests/unit/ -v --tb=short; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo "📋 Step 2: Running Contract Tests..."
echo "────────────────────────────────────"
if python -m pytest tests/contract/ -v --tb=short; then
    echo -e "${GREEN}✓ Contract tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Contract tests failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo "📋 Step 3: Running Integration Tests..."
echo "───────────────────────────────────────"
if python -m pytest tests/integration/ -v --tb=short; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo "📋 Step 4: Running Full Test Suite with Coverage..."
echo "──────────────────────────────────────────────────"
if python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v; then
    echo -e "${GREEN}✓ Full test suite passed${NC}"
    ((TESTS_PASSED++))

    # Extract coverage percentage
    COVERAGE=$(python -m pytest tests/ --cov=src --cov-report=term | grep "TOTAL" | awk '{print $(NF-2)}' | tr -d '%')
    echo ""
    echo "Coverage Report: ${COVERAGE}%"

    if (( $(echo "$COVERAGE >= $COVERAGE_THRESHOLD" | bc -l) )); then
        echo -e "${GREEN}✓ Coverage meets target (>=${COVERAGE_THRESHOLD}%)${NC}"
    else
        echo -e "${YELLOW}⚠ Coverage below target (${COVERAGE}% < ${COVERAGE_THRESHOLD}%)${NC}"
    fi
else
    echo -e "${RED}✗ Full test suite failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo "════════════════════════════════════════════════════════"
echo "  📊 Test Summary"
echo "════════════════════════════════════════════════════════"
echo "Tests Passed: ${TESTS_PASSED}"
echo "Tests Failed: ${TESTS_FAILED}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation checks passed!${NC}"
    echo ""
    echo "📈 Coverage Report: htmlcov/index.html"
    echo "   Run: open htmlcov/index.html"
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed${NC}"
    exit 1
fi

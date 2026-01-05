#!/bin/bash

echo "🧪 TodoList Test Runner"
echo "========================"
echo ""

if [ "$1" == "1" ]; then
    echo "🔬 Running Unit Tests (Business Logic)"
    DEBUG=1 pytest -v --tb=short
elif [ "$1" == "2" ]; then
    echo "🔌 Running Integration Tests (API)"
    DEBUG=2 pytest -v --tb=short
elif [ "$1" == "3" ]; then
    echo "🌐 Running E2E Tests (Full Stack)"
    DEBUG=3 pytest -v --tb=short
elif [ "$1" == "all" ]; then
    echo "🚀 Running ALL Tests"
    DEBUG=all pytest -v --tb=short --cov=. --cov-report=html
elif [ "$1" == "coverage" ]; then
    echo "📊 Running Tests with Coverage"
    pytest -v --cov=. --cov-report=html --cov-report=term
else
    echo "Usage: ./run_tests.sh [1|2|3|all|coverage]"
    echo ""
    echo "  1        - Unit tests (business logic)"
    echo "  2        - Integration tests (API endpoints)"
    echo "  3        - E2E tests (full stack)"
    echo "  all      - All tests"
    echo "  coverage - All tests with coverage report"
fi

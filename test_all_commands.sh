#!/usr/bin/env bash
# Complete test suite for EnergyLens commands

echo "================================================"
echo "ENERGYLENS AI - COMPLETE COMMAND TESTS"
echo "================================================"
echo ""

tests_passed=0
tests_failed=0

# Test 1: Help
echo "[1/8] Testing: energylens --help"
if energylens --help > /dev/null 2>&1; then
    echo "[PASS] Help command"
    ((tests_passed++))
else
    echo "[FAIL] Help command"
    ((tests_failed++))
fi
echo ""

# Test 2: Analyze bad_code
echo "[2/8] Testing: energylens analyze examples/bad_code.py"
if energylens analyze examples/bad_code.py > /dev/null 2>&1; then
    echo "[PASS] Analyze bad_code"
    ((tests_passed++))
else
    echo "[FAIL] Analyze bad_code"
    ((tests_failed++))
fi
echo ""

# Test 3: Analyze good_code
echo "[3/8] Testing: energylens analyze examples/good_code.py"
if energylens analyze examples/good_code.py > /dev/null 2>&1; then
    echo "[PASS] Analyze good_code"
    ((tests_passed++))
else
    echo "[FAIL] Analyze good_code"
    ((tests_failed++))
fi
echo ""

# Test 4: Refactor bad_code
echo "[4/8] Testing: energylens refactor examples/bad_code.py"
if energylens refactor examples/bad_code.py > /dev/null 2>&1; then
    echo "[PASS] Refactor bad_code"
    ((tests_passed++))
else
    echo "[FAIL] Refactor bad_code"
    ((tests_failed++))
fi
echo ""

# Test 5: Refactor with output
echo "[5/8] Testing: energylens refactor examples/bad_code.py -o test_output.py"
if energylens refactor examples/bad_code.py -o test_output.py > /dev/null 2>&1; then
    echo "[PASS] Refactor with output"
    ((tests_passed++))
else
    echo "[FAIL] Refactor with output"
    ((tests_failed++))
fi
echo ""

# Test 6: Compare
echo "[6/8] Testing: energylens compare examples/bad_code.py examples/good_code.py"
if energylens compare examples/bad_code.py examples/good_code.py > /dev/null 2>&1; then
    echo "[PASS] Compare"
    ((tests_passed++))
else
    echo "[FAIL] Compare"
    ((tests_failed++))
fi
echo ""

# Test 7: Benchmark
echo "[7/8] Testing: energylens benchmark examples/good_code.py --iterations 3"
if energylens benchmark examples/good_code.py --iterations 3 > /dev/null 2>&1; then
    echo "[PASS] Benchmark"
    ((tests_passed++))
else
    echo "[FAIL] Benchmark"
    ((tests_failed++))
fi
echo ""

# Test 8: Info
echo "[8/8] Testing: energylens info"
if energylens info > /dev/null 2>&1; then
    echo "[PASS] Info"
    ((tests_passed++))
else
    echo "[FAIL] Info"
    ((tests_failed++))
fi
echo ""

echo "================================================"
echo "SUMMARY"
echo "================================================"
echo "Passed: $tests_passed/8"
echo "Failed: $tests_failed/8"
echo ""

if [ $tests_failed -eq 0 ]; then
    echo "[SUCCESS] ALL TESTS PASSED!"
    exit 0
else
    echo "[SUMMARY] $tests_failed tests failed"
    exit 1
fi

#!/usr/bin/env python
"""
Complete CLI Testing - All Commands (No emoji)
"""

import subprocess
import sys

print('='*70)
print('ENERGYLENS AI - COMPLETE CLI TESTING')
print('='*70)
print()

commands = [
    ('help', ['energylens', '--help']),
    ('analyze bad_code', ['energylens', 'analyze', 'examples/bad_code.py']),
    ('analyze good_code', ['energylens', 'analyze', 'examples/good_code.py']),
    ('refactor bad_code', ['energylens', 'refactor', 'examples/bad_code.py', '-o', 'test_refactored.py']),
    ('refactor good_code', ['energylens', 'refactor', 'examples/good_code.py']),
    ('compare', ['energylens', 'compare', 'examples/bad_code.py', 'examples/good_code.py']),
    ('benchmark', ['energylens', 'benchmark', 'examples/good_code.py', '--iterations', '5']),
    ('info', ['energylens', 'info']),
]

passed = 0
failed = 0

for name, cmd in commands:
    print(f'[TEST] {name}')
    print('-'*70)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f'[PASS] Command succeeded')
            passed += 1
        else:
            print(f'[FAIL] Command failed (exit code {result.returncode})')
            if result.stderr:
                err_msg = result.stderr[:100].replace('\n', ' ')
                print(f'Error: {err_msg}')
            failed += 1
    except subprocess.TimeoutExpired:
        print(f'[TIMEOUT] Command took too long')
        failed += 1
    except Exception as e:
        print(f'[ERROR] {str(e)[:50]}')
        failed += 1
    
    print()

print('='*70)
print('SUMMARY')
print('='*70)
print(f'Passed: {passed}/{len(commands)}')
print(f'Failed: {failed}/{len(commands)}')
print()

if failed == 0:
    print('[SUCCESS] ALL TESTS PASSED!')
    sys.exit(0)
else:
    print(f'[SUMMARY] {failed} tests failed')
    sys.exit(1)

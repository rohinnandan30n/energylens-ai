#!/usr/bin/env python
"""
Test ALL EnergyLens CLI Commands
"""

import subprocess
import os

def run_energylens_cmd(args):
    """Run energylens command and return output"""
    cmd = f'energylens {args}'
    print(f'\n>>> {cmd}')
    print('-' * 70)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.stdout:
            print(result.stdout[:1000])  # First 1000 chars
        if result.stderr and 'emoji' not in result.stderr.lower():
            print('STDERR:', result.stderr[:500])
        print('Status: OK' if result.returncode == 0 else f'Status: Exit code {result.returncode}')
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print('TIMEOUT')
        return False
    except Exception as e:
        print(f'ERROR: {e}')
        return False

print('='*70)
print('ENERGYLENS CLI - COMMAND TEST SUITE')
print('='*70)

tests = [
    ('Help', '--help'),
    ('Info', 'info'),
    ('Analyze (good_code)', 'analyze examples/good_code.py'),
    ('Analyze (bad_code)', 'analyze examples/bad_code.py'),
    ('Analyze with details', 'analyze examples/good_code.py --detailed'),
    ('Compare codes', 'compare examples/bad_code.py examples/good_code.py'),
    ('Benchmark', 'benchmark examples/good_code.py --iterations 3'),
    ('Train (small)', 'train --samples 10'),
]

results = []
for test_name, cmd in tests:
    print(f'\n{"="*70}')
    print(f'TEST: {test_name}')
    print(f'{"="*70}')
    success = run_energylens_cmd(cmd)
    results.append((test_name, success))

print(f'\n\n{"="*70}')
print('TEST SUMMARY')
print(f'{"="*70}')

passed = sum(1 for _, success in results if success)
for test_name, success in results:
    status = '✓ PASS' if success else '✗ FAIL'
    print(f'{status:8} {test_name}')

print(f'\nTotal: {passed}/{len(results)} commands executed')
print('='*70)

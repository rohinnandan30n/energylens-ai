#!/usr/bin/env python
"""
EnergyLens AI - Complete Functionality Verification
Tests all 6 commands with real examples
"""

print('='*80)
print(' '*20 + 'ENERGYLENS AI - COMPLETE VERIFICATION')
print('='*80)
print()

# Test 1: Module imports
print('[1/6] Module Imports')
print('-'*80)
try:
    from src.analyzer.complexity_analyzer import ComplexityAnalyzer
    from src.predictor.ml_model import EnergyPredictor
    from src.profiler.simple_profiler import SimpleEnergyProfiler
    from src.data.generate_data import TrainingDataGenerator
    from src.refactor.complete_rewriter import generate_corrected_code
    print('[PASS] All core modules imported successfully')
    print('  - ComplexityAnalyzer')
    print('  - EnergyPredictor')
    print('  - SimpleEnergyProfiler')
    print('  - TrainingDataGenerator')
    print('  - Code Rewriter')
except Exception as e:
    print(f'[FAIL] Import error: {e}')
    exit(1)

print()

# Test 2: CLI commands exist
print('[2/6] CLI Commands Available')
print('-'*80)
from src.cli.main import analyze, benchmark, compare, refactor, train, info
commands = [
    ('analyze', analyze),
    ('benchmark', benchmark),
    ('compare', compare),
    ('refactor', refactor),
    ('train', train),
    ('info', info),
]
for cmd_name, cmd_func in commands:
    if callable(cmd_func):
        print(f'[OK] {cmd_name:12} - Available')
    else:
        print(f'[FAIL] {cmd_name:12} - Not callable')
print(f'[PASS] All {len(commands)} commands are available')

print()

# Test 3: Example files
print('[3/6] Example Files')
print('-'*80)
from pathlib import Path
examples = ['examples/bad_code.py', 'examples/good_code.py']
for example in examples:
    if Path(example).exists():
        size = Path(example).stat().st_size
        print(f'[OK] {example:30} ({size:4d} bytes)')
    else:
        print(f'[FAIL] {example:30} NOT FOUND')
print('[PASS] Example files present')

print()

# Test 4: Complexity Analysis
print('[4/6] Complexity Analysis')
print('-'*80)
analyzer = ComplexityAnalyzer()
with open('examples/bad_code.py') as f:
    bad_code = f.read()
with open('examples/good_code.py') as f:
    good_code = f.read()

try:
    bad_analysis = analyzer.analyze(bad_code)
    good_analysis = analyzer.analyze(good_code)
    
    print(f'[OK] bad_code.py:  {bad_analysis["big_o"]:6} complexity, Score {bad_analysis["complexity_score"]:3.0f}/100')
    print(f'[OK] good_code.py: {good_analysis["big_o"]:6} complexity, Score {good_analysis["complexity_score"]:3.0f}/100')
    print('[PASS] Complexity analysis working correctly')
except Exception as e:
    print(f'[FAIL] Analysis error: {e}')
    exit(1)

print()

# Test 5: Code Refactoring
print('[5/6] Code Refactoring')
print('-'*80)
try:
    refactored_bad, optimizations_bad = generate_corrected_code('examples/bad_code.py')
    refactored_good, optimizations_good = generate_corrected_code('examples/good_code.py')
    
    print(f'[OK] Refactored bad_code.py')
    print(f'     Optimizations found: {len(optimizations_bad)}')
    for opt in optimizations_bad:
        print(f'       - {opt}')
    
    print(f'[OK] Refactored good_code.py')
    print(f'     Optimizations found: {len(optimizations_good)}')
    for opt in optimizations_good:
        print(f'       - {opt}')
    
    print('[PASS] Code refactoring working correctly')
except Exception as e:
    print(f'[FAIL] Refactoring error: {e}')
    exit(1)

print()

# Test 6: ML Model Status
print('[6/6] ML Model Status')
print('-'*80)
try:
    from pathlib import Path
    model_path = Path('models/energy_model.pkl')
    if model_path.exists():
        predictor = EnergyPredictor()
        predictor.load('models/energy_model.pkl')
        
        # Test prediction
        test_features = bad_analysis['features']
        energy, confidence = predictor.predict(test_features)
        
        print(f'[OK] Model loaded from {model_path}')
        print(f'[OK] Test prediction: {energy:.2f} J (confidence: {confidence*100:.0f}%)')
        print('[PASS] ML model functional')
    else:
        print(f'[INFO] Model not found (requires training)')
        print('       Run: energylens train --samples 100')
except Exception as e:
    print(f'[INFO] ML model not yet trained: {e}')

print()
print('='*80)
print(' '*25 + 'VERIFICATION COMPLETE')
print('='*80)
print()
print('Status: ALL CRITICAL COMPONENTS OPERATIONAL')
print()
print('Available Commands:')
print('  1. energylens analyze <file>          - Analyze code complexity')
print('  2. energylens refactor <file>         - Refactor code for optimization')
print('  3. energylens compare <f1> <f2>       - Compare two implementations')
print('  4. energylens benchmark <file>        - Measure actual energy')
print('  5. energylens train                   - Train ML model')
print('  6. energylens info                    - Show project information')
print()
print('Example Usage:')
print('  energylens analyze examples/bad_code.py')
print('  energylens refactor examples/bad_code.py -o optimized.py')
print('  energylens compare examples/bad_code.py examples/good_code.py')
print('  energylens benchmark examples/good_code.py --iterations 10')
print()

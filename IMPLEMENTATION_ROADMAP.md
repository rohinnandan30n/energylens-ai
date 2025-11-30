# EnergyLens AI - Quick Implementation Roadmap

## Phase 1: Essential CLI Improvements (1-2 days)

### 1. Global `--json` Output Support
Add to all commands for CI/CD integration and automation.

**Files to modify**: `src/cli/main.py`

```python
# Add helper function at top
def output_as_json(data):
    import json
    console.print_json(data=data)

# Update each command signature
@cli.option('--json', is_flag=True, help='Output as JSON')
def analyze(file, detailed, json):
    # At end of function:
    if json:
        output_as_json({
            'complexity': analysis['big_o'],
            'score': analysis['complexity_score'],
            'energy': energy,
            'confidence': confidence,
            'file_size_kb': file_size_kb,
            'total_lines': total_lines,
        })
    else:
        # existing console output
```

**Benefits**: 
- CI/CD pipeline integration
- Scripting automation
- Tool integration

---

### 2. Global `--quiet` / `-q` Flag
Suppress non-essential output for scripts.

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
def analyze(file, detailed, quiet):
    # Instead of console.print() for info messages:
    if not quiet:
        console.print("[green][OK] Model loaded[/green]")
    
    # Always show results
    console.print(table)
```

**Benefits**:
- Cleaner script output
- Focus on results only

---

### 3. Global `--output` / `-o` Flag
Save results to file (unify with refactor).

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--output', '-o', type=click.Path(), help='Save output to file')
def analyze(file, detailed, output, json):
    # Generate results
    result_text = generate_result_string(...)
    
    if output:
        with open(output, 'w') as f:
            f.write(result_text)
        console.print(f"[green][SAVE] Results saved to {output}[/green]")
    else:
        console.print(result_text)
```

**Benefits**:
- Consistent interface
- Report generation
- Result archiving

---

### 4. Global `--color` Option
Support `auto|always|never` for different environments.

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--color', type=click.Choice(['auto', 'always', 'never']), 
            default='auto', help='Color output')
def analyze(file, color):
    if color == 'never':
        console = Console(force_terminal=True, legacy_windows=False, no_color=True)
    elif color == 'always':
        console = Console(force_terminal=True, legacy_windows=False)
    # else: auto-detect
```

**Benefits**:
- Log file compatibility
- Terminal-agnostic
- Accessibility

---

### 5. Global `--debug` Flag
Show step-by-step execution details.

**Files to modify**: `src/cli/main.py`

```python
import logging

@cli.option('--debug', is_flag=True, help='Show debug information')
def analyze(file, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        console.print("[dim]DEBUG MODE ENABLED[/dim]")
    
    # Throughout function:
    console.print(f"[dim][DEBUG] Reading file: {file}[/dim]", soft_wrap=True)
    console.print(f"[dim][DEBUG] File size: {file_size_kb} KB[/dim]", soft_wrap=True)
```

**Benefits**:
- Easier troubleshooting
- Performance profiling
- Understanding behavior

---

## Phase 2: Command-Specific Features (2-3 days)

### 6. Analyze: `--export` for Multiple Formats

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--export', type=click.Choice(['json', 'csv', 'html', 'markdown']),
            help='Export format')
@cli.option('--output', '-o', type=click.Path(), help='Output file')
def analyze(file, export, output):
    # Generate analysis
    
    if export == 'json':
        export_json(analysis, energy, output)
    elif export == 'csv':
        export_csv(analysis, energy, output)
    elif export == 'html':
        export_html(analysis, energy, output)
    elif export == 'markdown':
        export_markdown(analysis, energy, output)
```

**Create new file**: `src/cli/exporters.py`

```python
def export_json(analysis, energy, filepath):
    import json
    data = {
        'complexity': analysis['big_o'],
        'score': analysis['complexity_score'],
        'energy': energy,
        # ... more fields
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def export_html(analysis, energy, filepath):
    html = """
    <html>
    <head><title>EnergyLens Analysis Report</title></head>
    <body>
    <h1>Code Analysis Report</h1>
    <table>
    ...
    </table>
    </body>
    </html>
    """
    with open(filepath, 'w') as f:
        f.write(html)

# Similar for CSV, Markdown...
```

**Benefits**:
- Report generation
- Data analysis workflow
- Team communication

---

### 7. Benchmark: `--warmup` Runs

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--warmup', default=0, help='Warmup iterations before measurement')
def benchmark(file, iterations, warmup):
    profiler = SimpleEnergyProfiler()
    
    if warmup > 0:
        console.print(f"[yellow]Warming up with {warmup} runs...[/yellow]")
        for _ in track(range(warmup), description="Warmup..."):
            profiler.profile_code(code, iterations=1)
    
    console.print(f"[yellow]Running {iterations} measurement iterations...[/yellow]")
    result = profiler.profile_code(code, iterations=iterations)
```

**Benefits**:
- More accurate measurements
- JIT compilation, cache effects
- Consistent results

---

### 8. Analyze: `--pattern-detail` Flag

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--pattern-detail', is_flag=True, help='Show detailed pattern analysis')
def analyze(file, pattern_detail):
    # ... existing analysis ...
    
    if pattern_detail:
        console.print("\n[bold cyan][CHART] Detailed Pattern Analysis:[/bold cyan]\n")
        
        patterns = {
            'String Patterns': [
                f"String concatenation in loops: {feats.get('string_concat_in_loop', 0)} instances",
                f"Regular expressions: {count_regex_patterns(code)} patterns",
            ],
            'Loop Patterns': [
                f"Nested loops: {feats.get('nested_loops', 0)} instances",
                f"Recursive calls: {feats.get('has_recursion', 0)} instances",
            ],
            'Function Patterns': [
                f"Total functions: {feats.get('num_functions', 0)}",
                f"Lambda functions: {count_lambda(code)}",
            ]
        }
        
        for category, items in patterns.items():
            console.print(f"\n{category}:")
            for item in items:
                console.print(f"  • {item}")
```

**Benefits**:
- Educational insight
- Pattern awareness
- Learning tool

---

### 9. Refactor: `--intensity` Levels

**Files to modify**: `src/cli/main.py`, `src/refactor/complete_rewriter.py`

```python
@cli.option('--intensity', type=click.Choice(['light', 'moderate', 'aggressive']),
            default='moderate', help='Optimization intensity')
def refactor(file, intensity, output):
    from src.refactor.complete_rewriter import generate_corrected_code
    
    refactored_code, optimizations = generate_corrected_code(
        file, 
        intensity=intensity
    )
```

**Modify**: `src/refactor/complete_rewriter.py`

```python
def generate_corrected_code(file_path, intensity='moderate'):
    patterns_to_use = {
        'light': [
            'string_concat',  # Safe optimizations
            'regex_precompile',
        ],
        'moderate': [
            'string_concat',
            'list_lookup',
            'regex_precompile',
            'multiple_passes',
        ],
        'aggressive': [
            'string_concat',
            'list_lookup',
            'nested_duplicates',
            'manual_counting',
            'regex_precompile',
            'bubble_sort',
            'multiple_passes',
        ]
    }
    
    active_patterns = patterns_to_use[intensity]
    # Only apply selected patterns...
```

**Benefits**:
- Risk management
- Safe vs aggressive optimization
- Code safety

---

### 10. Compare: `--three-way-compare`

**Files to modify**: `src/cli/main.py`

```python
@click.argument('files', nargs=3, type=click.Path(exists=True))
def compare(files):
    """Compare energy consumption of multiple implementations"""
    
    results = []
    for filepath in files:
        # Analyze each file
        analysis = analyzer.analyze(code)
        energy, confidence = predictor.predict(analysis['features'])
        results.append({...})
    
    # Create wider table
    table = Table(title="[CHART] Three-Way Comparison")
    table.add_column("Metric", width=24)
    for result in results:
        table.add_column(result['file'], width=18)
    
    # Add all rows...
    # Add improvements row
    # Add ranking row...
```

**Benefits**:
- Comprehensive comparison
- Best-of-three selection
- Clear ranking

---

## Phase 3: Advanced Features (3-5 days)

### 11. Analyze: `--check` Mode for CI/CD

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--check', is_flag=True, help='Exit with error if thresholds exceeded')
@cli.option('--max-score', type=int, help='Max acceptable complexity score')
@cli.option('--max-energy', type=float, help='Max acceptable energy (Joules)')
@click.pass_context
def analyze(ctx, file, check, max_score, max_energy):
    # ... existing analysis ...
    
    if check:
        errors = []
        if max_score and analysis['complexity_score'] > max_score:
            errors.append(f"Complexity score {analysis['complexity_score']} > max {max_score}")
        if max_energy and energy and energy > max_energy:
            errors.append(f"Energy {energy}J > max {max_energy}J")
        
        if errors:
            for error in errors:
                console.print(f"[red][NO] {error}[/red]")
            ctx.exit(1)
        else:
            console.print("[green][YES] All checks passed![/green]")
            ctx.exit(0)
```

**Benefits**:
- CI/CD pipeline gates
- Automated quality checks
- Build blocking

---

### 12. Train: `--model-type` Selection

**Files to modify**: `src/cli/main.py`, `src/predictor/ml_model.py`

```python
@cli.option('--model-type', 
            type=click.Choice(['random-forest', 'xgboost', 'gradient-boost']),
            default='random-forest', help='ML model algorithm')
def train(samples, model_type):
    # ... setup ...
    
    predictor = EnergyPredictor(model_type=model_type)
    X, y = predictor.prepare_data(dataset)
    predictor.train(X, y)
    predictor.save()
    
    console.print(f"[green]Trained {model_type} model[/green]")
```

**Modify**: `src/predictor/ml_model.py`

```python
class EnergyPredictor:
    def __init__(self, model_type='random-forest'):
        self.model_type = model_type
        if model_type == 'random-forest':
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(n_estimators=100)
        elif model_type == 'xgboost':
            import xgboost
            self.model = xgboost.XGBRegressor()
        elif model_type == 'gradient-boost':
            from sklearn.ensemble import GradientBoostingRegressor
            self.model = GradientBoostingRegressor()
```

**Benefits**:
- Better predictions
- Flexibility
- Performance optimization

---

### 13. Benchmark: `--profile-memory`

**Files to modify**: `src/cli/main.py`, `src/profiler/simple_profiler.py`

```python
@cli.option('--profile-memory', is_flag=True, help='Track detailed memory usage')
def benchmark(file, profile_memory):
    profiler = SimpleEnergyProfiler()
    
    if profile_memory:
        result = profiler.profile_code_with_memory(code, iterations=iterations)
        
        # Show memory heatmap
        table = Table(title="Memory Profiling Results")
        table.add_column("Line", style="cyan")
        table.add_column("Memory (MB)", style="yellow")
        table.add_column("Allocation Rate", style="red")
        
        for line_num, memory, rate in result['memory_per_line']:
            table.add_row(str(line_num), f"{memory:.2f}", f"{rate:.2f}%")
        
        console.print(table)
```

**Benefits**:
- Memory leak detection
- Allocation profiling
- Bottleneck identification

---

### 14. Refactor: `--safety-checks`

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--safety-checks', type=click.Path(exists=True),
            help='Run tests to validate refactoring')
def refactor(file, safety_checks):
    # Generate refactored code
    refactored_code, optimizations = generate_corrected_code(file)
    
    if safety_checks:
        console.print("[yellow]Running safety tests...[/yellow]")
        
        # Run tests before refactoring
        orig_tests = run_tests(safety_checks)
        
        # Save refactored version temporarily
        temp_file = file + '.refactored_temp'
        with open(temp_file, 'w') as f:
            f.write(refactored_code)
        
        # Run tests on refactored version
        new_tests = run_tests(safety_checks, temp_file)
        
        # Compare results
        if orig_tests == new_tests:
            console.print("[green][YES] All tests pass! Refactoring is safe.[/green]")
        else:
            console.print("[red][NO] Tests failed after refactoring. Aborting.[/red]")
            os.remove(temp_file)
            return
```

**Benefits**:
- Refactoring confidence
- Regression prevention
- Behavioral verification

---

### 15. Batch Processing: `--parallel`

**Files to modify**: `src/cli/main.py`

```python
@cli.option('--parallel', is_flag=True, help='Process files in parallel')
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
def analyze_batch(files, parallel):
    """Analyze multiple files"""
    
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    
    def analyze_single(filepath):
        code = Path(filepath).read_text()
        analysis = ComplexityAnalyzer().analyze(code)
        predictor = EnergyPredictor()
        predictor.load('models/energy_model.pkl')
        energy, conf = predictor.predict(analysis['features'])
        return {
            'file': filepath,
            'analysis': analysis,
            'energy': energy,
            'confidence': conf
        }
    
    if parallel:
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(analyze_single, files))
    else:
        results = [analyze_single(f) for f in files]
    
    # Display aggregated results
    table = Table(title="Batch Analysis Results")
    table.add_column("File")
    table.add_column("Complexity")
    table.add_column("Energy (J)")
    
    for result in results:
        table.add_row(
            result['file'],
            result['analysis']['big_o'],
            f"{result['energy']:.2f}"
        )
    
    console.print(table)
```

**Benefits**:
- Speed for multiple files
- Better resource utilization
- Batch processing

---

## Phase 4: Integration (4-6 days)

### 16. CI/CD Integration

**Create**: `.github/workflows/energylens.yml`

```yaml
name: Code Energy Analysis

on: [push, pull_request]

jobs:
  energylens:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: energylens analyze src/*.py --check --max-score 50
      - run: energylens train --samples 100
      - run: energylens compare src/old.py src/new.py --json > comparison.json
      - uses: actions/upload-artifact@v3
        with:
          name: energylens-results
          path: comparison.json
```

---

### 17. Pre-commit Hook Integration

**Create**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: energylens-check
        name: EnergyLens Code Check
        entry: energylens analyze
        language: system
        types: [python]
        stages: [commit]
```

---

### 18. Configuration File Support

**Files to modify**: `src/cli/main.py`

**Create**: `.energylens.yml`

```yaml
# EnergyLens Configuration
defaults:
  quiet: false
  color: auto
  
analyze:
  threshold:
    energy: 50
    score: 80
  export: json
  
benchmark:
  iterations: 10
  warmup: 2
  
refactor:
  intensity: moderate
  
train:
  model_type: random-forest
  samples: 1000
```

**Implementation**:

```python
import yaml

def load_config(config_file='.energylens.yml'):
    if not Path(config_file).exists():
        return {}
    with open(config_file) as f:
        return yaml.safe_load(f)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True))
def analyze(file, config):
    cfg = load_config(config or '.energylens.yml')
    analyze_cfg = cfg.get('analyze', {})
    
    # Use config values as defaults
    threshold_energy = analyze_cfg.get('threshold', {}).get('energy', 100)
    # ...
```

---

## Implementation Timeline

```
Week 1: Phase 1 (Essential CLI)
├─ Day 1: --json, --quiet, --output
├─ Day 2: --color, --debug
└─ Testing & integration

Week 2: Phase 2 (Command Features)
├─ Day 1-2: --export, --warmup, --pattern-detail
├─ Day 3: --intensity, --three-way-compare
└─ Testing & fixes

Week 3: Phase 3 (Advanced)
├─ Day 1-2: --check mode, --model-type
├─ Day 3: --profile-memory, --safety-checks
└─ Testing & documentation

Week 4: Phase 4 (Integration)
├─ Day 1-2: CI/CD integration
├─ Day 3: Pre-commit hooks, config files
└─ Documentation & release prep
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_analyze_flags.py
def test_analyze_json_output(tmp_path):
    result = runner.invoke(cli.analyze, ['code.py', '--json'])
    data = json.loads(result.output)
    assert 'complexity' in data
    assert 'energy' in data
    
def test_analyze_check_mode(tmp_path):
    result = runner.invoke(cli.analyze, ['code.py', '--check', '--max-score', '30'])
    # Should fail for complex code
    assert result.exit_code == 1
```

### Integration Tests
```python
# tests/test_cli_integration.py
def test_full_pipeline():
    # Train -> analyze -> compare -> refactor
    runner.invoke(cli.train, ['--samples', '10'])
    runner.invoke(cli.analyze, ['f1.py', '--json', '-o', 'result.json'])
    runner.invoke(cli.compare, ['f1.py', 'f2.py', '--json', '-o', 'comp.json'])
```

---

This roadmap provides a clear path to significantly enhance EnergyLens AI with practical, high-impact features.

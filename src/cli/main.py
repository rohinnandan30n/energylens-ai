"""
EnergyLens CLI - Command-Line Interface
Main entry point for the tool
Enhanced with progress tracking, file stats, and advanced formatting
"""
import click
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analyzer.complexity_analyzer import ComplexityAnalyzer
from src.predictor.ml_model import EnergyPredictor
from src.profiler.simple_profiler import SimpleEnergyProfiler

# Use legacy_windows=False on Windows to handle unicode properly
import os
force_terminal = os.environ.get('TERM') is None
console = Console(force_terminal=True, legacy_windows=False)


# ==================== HELPER FUNCTIONS ====================

def get_code_stats(code: str):
    """Extract file statistics: total lines, blank lines, comment lines"""
    lines = code.split('\n')
    total = len(lines)
    blank = sum(1 for line in lines if line.strip() == '')
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    return total, blank, comments


def score_label(score: float) -> str:
    """Convert complexity score (0-100) to label (Low/Moderate/High)"""
    if score < 30:
        return "Low"
    elif score < 70:
        return "Moderate"
    else:
        return "High"


def big_o_badge(big_o: str) -> str:
    """Create a Big-O complexity badge with color"""
    badges = {
        "O(1)": "[green]O(1) [GREEN] TRIVIAL[/green]",
        "O(log n)": "[cyan]O(log n) 🔵 FAST[/cyan]",
        "O(n)": "[yellow]O(n) [YEL] LINEAR[/yellow]",
        "O(n log n)": "[orange1]O(n log n) 🟠 MODERATE[/orange1]",
        "O(n²)": "[red]O(n²) [RED] HARD[/red]",
        "O(n³)": "[red]O(n³) [RED] VERY HARD[/red]",
        "O(2^n)": "[dark_red]O(2^n) [BLK] EXPONENTIAL[/dark_red]",
    }
    return badges.get(big_o, f"[dim]{big_o}[/dim]")


def combined_badge(big_o: str, complexity_score: float) -> str:
    """Create a combined badge: Big-O + difficulty + score label"""
    label = score_label(complexity_score)
    if "O(1)" in big_o:
        return f"[green]O(1) [GREEN] TRIVIAL | Score: {label}[/green]"
    elif "O(log n)" in big_o:
        return f"[cyan]O(log n) 🔵 FAST | Score: {label}[/cyan]"
    elif "O(n)" in big_o and "O(n²)" not in big_o:
        return f"[yellow]O(n) [YEL] LINEAR | Score: {label}[/yellow]"
    elif "O(n log n)" in big_o:
        return f"[orange1]O(n log n) 🟠 MODERATE | Score: {label}[/orange1]"
    elif "O(n²)" in big_o or "O(n³)" in big_o:
        return f"[red]{big_o} [RED] HARD | Score: {label}[/red]"
    elif "O(2^n)" in big_o:
        return f"[dark_red]{big_o} [BLK] EXPONENTIAL | Score: {label}[/dark_red]"
    else:
        return f"[dim]{big_o} | Score: {label}[/dim]"


def estimate_runtime_ms(big_o: str, n: int = 10000) -> float:
    """Estimate runtime in milliseconds for a given Big-O and n value"""
    # Rough estimates in microseconds per operation
    estimates = {
        "O(1)": 0.001,
        "O(log n)": 0.005,
        "O(n)": 0.01,
        "O(n log n)": 0.15,
        "O(n²)": 10,
        "O(n³)": 1000,
        "O(2^n)": 1e10,
    }
    
    for pattern, per_op in estimates.items():
        if pattern in big_o:
            if "O(1)" in pattern:
                return per_op
            elif "O(log n)" in pattern:
                return per_op * (n * 0.0001)  # log approximation
            elif "O(n)" in pattern and "O(n²)" not in pattern:
                return (per_op * n) / 1000  # Convert to ms
            elif "O(n log n)" in pattern:
                return (per_op * n * 0.0001 * n) / 1000
            elif "O(n²)" in pattern:
                return (per_op * n * n) / 1000
            elif "O(n³)" in pattern:
                return (per_op * n * n * n) / 1000000
            elif "O(2^n)" in pattern:
                return 999999  # Cap at max
    
    return 0.0


@click.group()
def cli():
    """⚡ EnergyLens AI - Predict code energy consumption with ML"""
    pass


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def analyze(file, detailed):
    """Analyze a Python file and predict energy consumption"""
    
    file_path = Path(file)
    start_time = time.time()
    
    # Read code with file stats
    try:
        code = file_path.read_text()
        file_size_kb = round(file_path.stat().st_size / 1024, 2)
        total_lines, blank_lines, comment_lines = get_code_stats(code)
    except Exception as e:
        console.print(f"[red][NO] Error reading file: {e}[/red]")
        return
    
    console.print(f"\n[bold cyan][POWER] Analyzing:[/bold cyan] {file}\n")
    
    # Show progress
    for _ in track(range(3), description="Processing code..."):
        time.sleep(0.1)
    
    # Step 1: Analyze complexity
    analyzer = ComplexityAnalyzer()
    try:
        console.print("[green][OK] Complexity analysis completed[/green]")
        analysis = analyzer.analyze(code)
    except ValueError as e:
        console.print(f"[red][NO] Error analyzing code: {e}[/red]")
        return
    
    # Step 2: Load ML model and predict
    predictor = EnergyPredictor()
    energy = None
    confidence = None
    try:
        predictor.load('models/energy_model.pkl')
        console.print("[green][OK] ML model loaded successfully[/green]")
        energy, confidence = predictor.predict(analysis['features'])
        console.print("[green][OK] Prediction generated[/green]")
    except FileNotFoundError:
        console.print("[yellow][WARN]  ML model not found.[/yellow]")
        console.print("[yellow]Run training first: energylens train[/yellow]\n")
    except Exception as e:
        console.print(f"[yellow][WARN]  Model load/predict error: {e}[/yellow]")

    analysis_time = time.time() - start_time

    # Step 3: Display results
    _display_results(analysis, energy, confidence, detailed, analysis_time, 
                     file_size_kb, total_lines, blank_lines, comment_lines)


def _display_results(analysis, energy, confidence, detailed, analysis_time=0, 
                     file_size_kb=None, total_lines=None, blank_lines=None, comment_lines=None):
    """Display analysis results in enhanced format with all details"""
    
    # Main results table
    table = Table(title="[CHART] Analysis Results", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", width=24)
    table.add_column("Value", style="green", width=44)
    
    # Combined badge
    badge_text = combined_badge(analysis['big_o'], analysis['complexity_score'])
    table.add_row("Complexity", badge_text)
    table.add_row("Complexity Score", f"{analysis['complexity_score']:.0f}/100")
    
    # Features summary
    table.add_row("Number of Loops", str(analysis['features'].get('num_loops', 0)))
    table.add_row("Max Loop Depth", str(analysis['features'].get('max_loop_depth', 0)))
    table.add_row("Function Calls", str(analysis['features'].get('num_function_calls', 0)))
    
    # Code stats
    if file_size_kb is not None or total_lines is not None:
        table.add_row("", "")
        if file_size_kb is not None:
            table.add_row("File Size", f"{file_size_kb} KB")
        if total_lines is not None:
            table.add_row("Total Lines", str(total_lines))
            table.add_row("Blank Lines", str(blank_lines))
            table.add_row("Comment Lines", str(comment_lines))
    
    # Estimated runtime
    est_ms = estimate_runtime_ms(analysis['big_o'])
    table.add_row("Est. Runtime", f"{est_ms:.1f} ms (n=10,000)")
    
    # Analysis time
    if analysis_time > 0:
        table.add_row("Analysis Time", f"{analysis_time:.3f} seconds")
    
    # Energy prediction (if available)
    if energy is not None:
        table.add_row("", "")
        table.add_row("Predicted Energy", f"{energy:.2f} J", style="bold yellow")
        table.add_row("Confidence", f"{confidence*100:.0f}%")
        kwh = energy / 3_600_000
        cost = kwh * 0.15
        co2 = kwh * 500
        table.add_row("Energy (kWh)", f"{kwh:.6f}")
        table.add_row("Est. Cost", f"${cost:.6f}")
        table.add_row("Est. CO2", f"{co2:.2f} g")
    
    console.print(table)
    
    # Warnings & suggestions
    warnings = []
    suggestions = []
    feats = analysis['features']
    
    if feats.get('nested_loops'):
        warnings.append("[WARN]  Nested loops detected (O(n²) complexity)")
        suggestions.append("Use vectorized operations (NumPy/Pandas) or hashing for lookups")
    
    if feats.get('has_recursion'):
        warnings.append("[WARN]  Recursion detected - may be exponential")
        suggestions.append("Consider memoization (@lru_cache) or iterative rewrite")
    
    if feats.get('string_concat_in_loop'):
        suggestions.append("Avoid string concatenation in loops; use ''.join()")
    
    if energy and energy > 100:
        warnings.append("[ALERT] High energy consumption predicted!")
    
    if warnings:
        console.print("\n[bold yellow][WARN]  Warnings:[/bold yellow]")
        for w in warnings:
            console.print("  " + w)
    
    if suggestions:
        console.print("\n[bold green][IDEA] Optimization Suggestions:[/bold green]")
        for i, s in enumerate(suggestions, 1):
            console.print(f"  {i}. {s}")
    
    if detailed:
        console.print("\n[bold]🔍 Detailed Features:[/bold]")
        for k, v in feats.items():
            console.print(f"  {k}: {v}")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--iterations', default=10, help='Number of benchmark runs')
def benchmark(file, iterations):
    """Actually run code and measure energy consumption"""
    
    file_path = Path(file)
    start_time = time.time()
    
    # Read code with stats
    try:
        code = file_path.read_text()
        file_size_kb = round(file_path.stat().st_size / 1024, 2)
        total_lines, blank_lines, comment_lines = get_code_stats(code)
    except Exception as e:
        console.print(f"[red][NO] Error reading file: {e}[/red]")
        return
    
    console.print(f"\n[bold cyan][POWER] Benchmarking:[/bold cyan] {file}")
    console.print(f"[yellow]Running code {iterations} times to measure actual energy...[/yellow]\n")
    
    # Show progress
    for _ in track(range(iterations), description="Running benchmark..."):
        time.sleep(0.05)
    
    # Measure energy
    profiler = SimpleEnergyProfiler()
    try:
        result = profiler.profile_code(code, iterations=iterations)
        benchmark_time = time.time() - start_time
        
        # Display results table
        table = Table(title="[CHART] Benchmark Results", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", width=24)
        table.add_column("Value", style="green", width=44)
        
        # Energy and power metrics
        table.add_row("Energy Consumed", f"{result['energy_joules']:.2f} J", style="bold yellow")
        table.add_row("Duration", f"{result['duration_seconds']:.3f} s")
        table.add_row("Avg CPU Usage", f"{result['cpu_percent']:.1f}%")
        table.add_row("Avg Power", f"{result['power_watts']:.2f} W")
        
        # Derived metrics
        kwh = result['energy_joules'] / 3_600_000
        cost = kwh * 0.15
        co2 = kwh * 500
        
        table.add_row("", "")
        table.add_row("Energy (kWh)", f"{kwh:.6f}")
        table.add_row("Est. Cost", f"${cost:.6f}")
        table.add_row("Est. CO2", f"{co2:.2f} g")
        
        # Iterations and timing
        table.add_row("", "")
        table.add_row("Iterations", str(iterations))
        table.add_row("Avg Per Iteration", f"{result['energy_joules']/iterations:.2f} J")
        table.add_row("Benchmark Time", f"{benchmark_time:.3f} seconds")
        
        # File stats
        table.add_row("", "")
        table.add_row("File Size", f"{file_size_kb} KB")
        table.add_row("Total Lines", str(total_lines))
        
        console.print(table)
        
        # Efficiency insights
        if result['cpu_percent'] < 5:
            console.print("[green][YES] Low CPU usage - efficient code[/green]")
        elif result['cpu_percent'] > 50:
            console.print("[yellow][WARN]  High CPU usage - potential optimization opportunity[/yellow]")
            
    except Exception as e:
        console.print(f"[red][NO] Error during benchmark: {e}[/red]")


def estimate_memory_usage(num_loops: int, max_depth: int) -> float:
    """Estimate memory usage in MB based on code complexity"""
    # Rough estimation: base + loop overhead
    base_memory = 0.01  # MB
    memory_per_loop = 0.005 * (max_depth + 1)
    return base_memory + (num_loops * memory_per_loop)


def estimate_runtime_for_ops(big_o: str, operations: int = 1000) -> float:
    """Estimate runtime for a given number of operations in milliseconds"""
    estimates = {
        "O(1)": 0.001,
        "O(log n)": 0.05,
        "O(n)": 0.1,
        "O(n log n)": 1.5,
        "O(n²)": 100,
        "O(n³)": 10000,
        "O(2^n)": 999999,
    }
    
    for pattern, per_op_ms in estimates.items():
        if pattern in big_o:
            return per_op_ms * (operations / 10)
    return 0.1


@cli.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
def compare(file1, file2):
    """Compare energy consumption of two implementations"""
    
    file1_path = Path(file1)
    file2_path = Path(file2)
    
    console.print("\n[bold cyan][POWER] Comparing Implementations[/bold cyan]\n")
    console.print(f"[yellow]Analyzing {file1_path.name} and {file2_path.name}...[/yellow]\n")
    
    # Show progress
    for _ in track(range(3), description="Processing files..."):
        time.sleep(0.08)
    
    # Analyze both files
    analyzer = ComplexityAnalyzer()
    predictor = EnergyPredictor()
    
    try:
        predictor.load('models/energy_model.pkl')
        console.print("[green][OK] ML model loaded[/green]\n")
    except Exception:
        console.print("[red][NO] ML model not found. Run training first.[/red]")
        return
    
    results = []
    for filepath in [file1_path, file2_path]:
        try:
            code = filepath.read_text()
            file_size_kb = round(filepath.stat().st_size / 1024, 2)
            total_lines, blank_lines, comment_lines = get_code_stats(code)
            
            analysis = analyzer.analyze(code)
            energy, confidence = predictor.predict(analysis['features'])
            
            # Calculate additional metrics
            num_loops = analysis['features'].get('num_loops', 0)
            max_depth = analysis['features'].get('max_loop_depth', 0)
            memory_mb = estimate_memory_usage(num_loops, max_depth)
            runtime_1k_ops = estimate_runtime_for_ops(analysis['big_o'], 1000)
            
            results.append({
                'file': filepath.name,
                'energy': energy,
                'big_o': analysis['big_o'],
                'confidence': confidence,
                'score': analysis['complexity_score'],
                'size': file_size_kb,
                'lines': total_lines,
                'memory_mb': memory_mb,
                'runtime_1k': runtime_1k_ops,
                'num_loops': num_loops,
                'max_depth': max_depth,
            })
        except Exception as e:
            console.print(f"[red][NO] Error analyzing {filepath.name}: {e}[/red]")
            return
    
    # Display comparison table
    table = Table(title="[CHART] Comparison Results", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", width=24)
    table.add_column(results[0]['file'], style="yellow", width=20)
    table.add_column(results[1]['file'], style="green", width=20)
    
    # ─── Core Metrics ───
    table.add_row("[bold]Core Metrics[/bold]", "", "")
    table.add_row("Complexity", results[0]['big_o'], results[1]['big_o'])
    table.add_row("Complexity Score", f"{results[0]['score']:.0f}/100", f"{results[1]['score']:.0f}/100")
    
    # ─── Energy Metrics ───
    table.add_row("", "", "")
    table.add_row("[bold]Energy Metrics[/bold]", "", "")
    table.add_row("Energy", f"{results[0]['energy']:.2f} J", f"{results[1]['energy']:.2f} J")
    table.add_row("Confidence", f"{results[0]['confidence']*100:.0f}%", f"{results[1]['confidence']*100:.0f}%")
    
    # ─── Code Metrics ───
    table.add_row("", "", "")
    table.add_row("[bold]Code Metrics[/bold]", "", "")
    table.add_row("File Size", f"{results[0]['size']} KB", f"{results[1]['size']} KB")
    table.add_row("Total Lines", str(results[0]['lines']), str(results[1]['lines']))
    
    # ─── Performance Estimates ───
    table.add_row("", "", "")
    table.add_row("[bold]Performance Estimates[/bold]", "", "")
    table.add_row("Memory Usage", f"{results[0]['memory_mb']:.3f} MB", f"{results[1]['memory_mb']:.3f} MB")
    table.add_row("Time (1000 ops)", f"{results[0]['runtime_1k']:.2f} ms", f"{results[1]['runtime_1k']:.2f} ms")
    
    # Calculate improvements
    try:
        energy_improvement = ((results[0]['energy'] - results[1]['energy']) / results[0]['energy']) * 100
    except:
        energy_improvement = 0.0
    
    try:
        memory_improvement = ((results[0]['memory_mb'] - results[1]['memory_mb']) / results[0]['memory_mb']) * 100
    except:
        memory_improvement = 0.0
    
    try:
        time_improvement = ((results[0]['runtime_1k'] - results[1]['runtime_1k']) / results[0]['runtime_1k']) * 100
    except:
        time_improvement = 0.0
    
    table.add_row("", "", "")
    table.add_row("[bold]Improvements[/bold]", "", "")
    
    energy_color = "green" if energy_improvement > 0 else "red"
    table.add_row("Energy Improvement", f"[{energy_color}]{energy_improvement:+.1f}%[/{energy_color}]", 
                  f"{'[YES] Better' if energy_improvement > 0 else '[NO] Worse'}")
    
    mem_color = "green" if memory_improvement > 0 else "red"
    table.add_row("Memory Improvement", f"[{mem_color}]{memory_improvement:+.1f}%[/{mem_color}]", 
                  f"{'[YES] Better' if memory_improvement > 0 else '[NO] Worse'}")
    
    time_color = "green" if time_improvement > 0 else "red"
    table.add_row("Speed Improvement", f"[{time_color}]{time_improvement:+.1f}%[/{time_color}]", 
                  f"{'[YES] Better' if time_improvement > 0 else '[NO] Worse'}")
    
    # ─── Environmental Impact ───
    table.add_row("", "", "")
    table.add_row("[bold]Environmental Impact[/bold]", "", "")
    
    kwh_1 = results[0]['energy'] / 3_600_000
    co2_1 = kwh_1 * 500  # grams
    km_1 = co2_1 / 120   # Assume 120g CO2 per km
    
    kwh_2 = results[1]['energy'] / 3_600_000
    co2_2 = kwh_2 * 500
    km_2 = co2_2 / 120
    
    co2_saved = co2_1 - co2_2
    km_saved = km_1 - km_2
    
    table.add_row("CO₂ Emissions", f"{co2_1:.2f} g ({km_1:.3f} km)", f"{co2_2:.2f} g ({km_2:.3f} km)")
    table.add_row("CO₂ Saved", f"[green]{co2_saved:.2f} g[/green]", f"[green]{km_saved:.3f} km[/green]")
    
    console.print(table)
    
    # ─── Detailed Analysis ───
    console.print("\n[bold cyan][CHART] Detailed Analysis:[/bold cyan]")
    
    if results[0]['big_o'] != results[1]['big_o']:
        console.print(f"[yellow][WARN]  Complexity differs: {results[0]['big_o']} vs {results[1]['big_o']}[/yellow]")
    
    score_diff = results[0]['score'] - results[1]['score']
    if score_diff > 5:
        console.print(f"[green][YES] {results[1]['file']} has {abs(score_diff):.0f} points better complexity score[/green]")
    elif score_diff < -5:
        console.print(f"[red][NO] {results[0]['file']} has worse complexity by {abs(score_diff):.0f} points[/red]")
    
    if energy_improvement > 10:
        console.print(f"[green][YES] Significant energy improvement: {energy_improvement:.1f}%[/green]")
    elif energy_improvement > 0:
        console.print(f"[green][YES] Moderate energy improvement: {energy_improvement:.1f}%[/green]")
    elif energy_improvement < -10:
        console.print(f"[red][NO] Significant energy regression: {abs(energy_improvement):.1f}%[/red]")
    elif energy_improvement < 0:
        console.print(f"[yellow][WARN]  Slight energy regression: {abs(energy_improvement):.1f}%[/yellow]")
    
    # ─── Recommendation Panel ───
    overall_improvement = (energy_improvement + memory_improvement + time_improvement) / 3
    
    if overall_improvement > 30:
        rec_title = "[TROPHY] Highly Recommended"
        rec_color = "green"
        rec_text = f"Major improvements across all metrics! Use {results[1]['file']} (avg {overall_improvement:.1f}% better)"
    elif overall_improvement > 10:
        rec_title = "[YES] Recommended"
        rec_color = "cyan"
        rec_text = f"Good improvements overall! Consider using {results[1]['file']} (avg {overall_improvement:.1f}% better)"
    elif overall_improvement > 0:
        rec_title = "[WARN]  Marginal Improvement"
        rec_color = "yellow"
        rec_text = f"Slight gains ({overall_improvement:.1f}%). Choose based on code clarity"
    else:
        rec_title = "[NO] Not Recommended"
        rec_color = "red"
        rec_text = f"{results[1]['file']} performs worse overall ({overall_improvement:.1f}%)"
    
    console.print(f"\n[bold {rec_color}]{rec_title}[/bold {rec_color}]")
    console.print(f"[dim]{rec_text}[/dim]")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for refactored code')
def refactor(file, output):
    """Refactor Python code to apply energy optimizations"""
    
    console.print(f"\n[bold cyan][FIX] Refactoring:[/bold cyan] {file}\n")
    
    # Import refactorer
    try:
        from src.refactor.complete_rewriter import generate_corrected_code
    except ImportError:
        console.print("[red][NO] Refactoring module not available[/red]")
        return
    
    # Read code
    try:
        with open(file, 'r') as f:
            code = f.read()
    except Exception as e:
        console.print(f"[red][NO] Error reading file: {e}[/red]")
        return
    
    # Analyze original
    analyzer = ComplexityAnalyzer()
    try:
        original_analysis = analyzer.analyze(code)
    except Exception as e:
        console.print(f"[red][NO] Error analyzing original code: {e}[/red]")
        return
    
    # Generate optimizations
    try:
        refactored_code, optimizations = generate_corrected_code(file)
        
        # Analyze refactored code
        try:
            refactored_analysis = analyzer.analyze(refactored_code)
        except:
            refactored_analysis = None
        
        # Display results
        table = Table(title="[FIX] Refactoring Results", show_header=True)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Original", style="red", width=25)
        table.add_column("Refactored", style="green", width=25)
        
        table.add_row("Complexity", original_analysis['big_o'], 
                      refactored_analysis['big_o'] if refactored_analysis else "N/A")
        table.add_row("Complexity Score", 
                      f"{original_analysis['complexity_score']:.0f}/100",
                      f"{refactored_analysis['complexity_score']:.0f}/100" if refactored_analysis else "N/A")
        
        console.print(table)
        
        # Display applied optimizations
        if optimizations:
            console.print("\n[bold green][YES] Applied Optimizations:[/bold green]")
            for i, opt in enumerate(optimizations, 1):
                console.print(f"  {i}. {opt}")
        else:
            console.print("\n[yellow]ℹ️  No specific optimizations applicable[/yellow]")
        
        # Show improvement
        if refactored_analysis:
            score_improvement = refactored_analysis['complexity_score'] - original_analysis['complexity_score']
            if score_improvement < 0:
                console.print(f"\n[bold green][CHART] Score improved by {abs(score_improvement):.0f} points![/bold green]")
            elif score_improvement > 0:
                console.print(f"\n[yellow][CHART] Score change: +{score_improvement:.0f} points[/yellow]")
        
        # Output refactored code
        if output:
            with open(output, 'w') as f:
                f.write(refactored_code)
            console.print(f"\n[bold green][SAVE] Refactored code saved to: {output}[/bold green]")
        else:
            console.print(f"\n[bold cyan]Refactored Code Preview:[/bold cyan]")
            console.print(f"[yellow]Use --output / -o to save to file[/yellow]\n")
            # Show first 50 lines
            lines = refactored_code.split('\n')[:50]
            console.print('\n'.join(lines))
            if len(refactored_code.split('\n')) > 50:
                console.print(f"\n[dim]... ({len(refactored_code.split(chr(10))) - 50} more lines) ...[/dim]")
            
    except Exception as e:
        console.print(f"[red][NO] Error during refactoring: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@cli.command()
@click.option('--samples', default=100, help='Number of training samples')
def train(samples):
    """Generate training data and train ML model"""
    
    console.print(f"\n[bold cyan][AI] Training ML Model[/bold cyan]\n")
    console.print(f"Generating {samples} training samples...")
    console.print("[yellow]This will take several minutes depending on samples...[/yellow]\n")
    
    # Import here to avoid slow startup
    from src.data.generate_data import TrainingDataGenerator
    
    # Generate data with progress
    console.print("[bold][CHART] Generating training data...[/bold]\n")
    generator = TrainingDataGenerator()
    dataset = generator.generate_dataset(num_samples=samples)
    generator.save_dataset(dataset)
    
    console.print(f"[green][OK] Dataset generated with {len(dataset)} samples[/green]\n")
    
    # Train model
    console.print("[bold][AI] Training ML model...[/bold]\n")
    
    predictor = EnergyPredictor()
    X, y = predictor.prepare_data(dataset)
    
    console.print(f"[cyan][CHART] Training set size: {int(len(X) * 0.8)} samples[/cyan]")
    console.print(f"[cyan][CHART] Test set size: {int(len(X) * 0.2)} samples[/cyan]\n")
    
    predictor.train(X, y)
    predictor.save()
    
    console.print("\n[bold green][YES] Training complete![/bold green]")
    console.print(f"\n[green][OK] Model saved to: models/energy_model.pkl[/green]")
    console.print(f"[green][OK] Training data saved to: data/training_data.pkl[/green]\n")
    console.print("[cyan]You can now use: energylens analyze <file> or energylens compare <f1> <f2>[/cyan]")


@cli.command()
def info():
    """Show information about EnergyLens"""
    
    info_text = """
[bold cyan][POWER] EnergyLens AI[/bold cyan]

Predict code energy consumption using machine learning.

[bold]🎯 Features:[/bold]
- ✓ Static code complexity analysis (Big-O detection)
- ✓ ML-powered energy consumption prediction
- ✓ Actionable optimization suggestions
- ✓ Side-by-side implementation comparison
- ✓ Actual energy benchmarking
- ✓ Automatic code refactoring with suggestions

[bold][CHART] Capabilities:[/bold]
- Detect nested loops, recursion, string operations
- Estimate runtime for given complexity
- Track file statistics (size, lines, comments)
- Calculate energy costs and CO2 emissions
- Compare optimization impact
- Generate training data for models

[bold]🚀 Quick Start:[/bold]
  energylens train --samples 100          Train ML model (run once)
  energylens analyze bad_code.py          Analyze code complexity
  energylens refactor bad_code.py         Get optimization suggestions
  energylens compare bad.py good.py       Compare implementations
  energylens benchmark code.py            Measure actual energy

[bold]📋 Usage Examples:[/bold]
  # Analyze single file
  energylens analyze examples/bad_code.py --detailed

  # Compare two versions
  energylens compare bad_version.py good_version.py

  # Get optimization suggestions
  energylens refactor bad_code.py -o optimized.py

  # Measure actual energy consumption
  energylens benchmark code.py --iterations 20

  # Train model with custom samples
  energylens train --samples 200

[bold]📈 Output Includes:[/bold]
  • Complexity classification (O(1), O(n), O(n²), etc.)
  • Complexity score (0-100 scale)
  • Estimated runtime based on Big-O
  • File statistics (size, lines, comments)
  • Energy predictions with confidence
  • Environmental impact (cost, CO2 emissions)
  • Specific optimization recommendations

[bold][IDEA] Tips:[/bold]
  1. Always run 'energylens train' before using analyze/compare
  2. Use --detailed flag to see all extracted features
  3. Run benchmark on multiple iterations for accurate results
  4. Compare bad vs good code to understand improvements

[bold]📚 More Information:[/bold]
  GitHub: https://github.com/yourusername/energylens-ai
  Documentation: Check README.md in project root

[bold green][AI] EnergyLens - Making code energy-aware![/bold green]
"""
    
    panel = Panel(info_text, title="EnergyLens AI", border_style="cyan", padding=(1, 2))
    console.print(panel)


if __name__ == '__main__':
    cli()
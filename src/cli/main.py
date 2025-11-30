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


def create_energy_bar(energy: float, max_energy: float = 2.0) -> str:
    """Create a visual energy bar"""
    filled = int((energy / max_energy) * 20)
    filled = min(filled, 20)
    empty = 20 - filled
    return f"[bold green]{'█' * filled}[/bold green][dim]{'░' * empty}[/dim] {energy:.2f}J"


def create_progress_bar(value: float, max_val: float = 100) -> str:
    """Create a visual progress bar for scores"""
    filled = int((value / max_val) * 20)
    filled = min(filled, 20)
    empty = 20 - filled
    
    if value < 33:
        color = "green"
    elif value < 66:
        color = "yellow"
    else:
        color = "red"
    
    return f"[bold {color}]{'█' * filled}[/bold {color}][dim]{'░' * empty}[/dim]"


def create_complexity_timeline(big_o: str) -> list:
    """Create estimated complexity timeline for different input sizes"""
    estimates = {
        "O(1)": [(100, 0.0001), (1000, 0.0001), (10000, 0.0001), (100000, 0.0001)],
        "O(log n)": [(100, 0.001), (1000, 0.001), (10000, 0.002), (100000, 0.002)],
        "O(n)": [(100, 0.01), (1000, 0.1), (10000, 1.0), (100000, 10.0)],
        "O(n log n)": [(100, 0.01), (1000, 0.15), (10000, 2.0), (100000, 25)],
        "O(n²)": [(100, 1.0), (1000, 100), (10000, 10000), (100000, float('inf'))],
        "O(n³)": [(100, 100), (1000, 1000000), (10000, float('inf')), (100000, float('inf'))],
        "O(2^n)": [(100, float('inf')), (1000, float('inf')), (10000, float('inf')), (100000, float('inf'))],
    }
    
    for pattern, timeline in estimates.items():
        if pattern in big_o:
            return timeline
    return [(100, 0.01), (1000, 0.1), (10000, 1.0), (100000, 10.0)]


def create_risk_score(score: float, big_o: str) -> str:
    """Create a risk assessment text only (no bar)"""
    if "O(2^n)" in big_o or "O(n³)" in big_o:
        risk_level = "CRITICAL"
        risk_color = "red"
    elif "O(n²)" in big_o:
        risk_level = "HIGH"
        risk_color = "red"
    elif "O(n log n)" in big_o:
        risk_level = "MODERATE"
        risk_color = "yellow"
    elif "O(n)" in big_o:
        risk_level = "LOW"
        risk_color = "green"
    else:
        risk_level = "MINIMAL"
        risk_color = "green"
    
    return f"[{risk_color}]{risk_level}[/{risk_color}]"


def display_section_header(title: str, icon: str = ""):
    """Display a beautiful section header"""
    console.print(f"\n[bold cyan]{'─' * 60}[/bold cyan]")
    console.print(f"[bold cyan]{icon} {title}[/bold cyan]")
    console.print(f"[bold cyan]{'─' * 60}[/bold cyan]\n")


def display_metric_row(label: str, value: str, second_value: str = None):
    """Display a formatted metric row"""
    if second_value:
        console.print(f"  [cyan]{label:.<35}[/cyan] {value:>15} {second_value}")
    else:
        console.print(f"  [cyan]{label:.<35}[/cyan] {value}")


@click.group()
def cli():
    """EnergyLens AI - Predict code energy consumption with ML"""
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
    """Display analysis results in beautiful tabular format"""
    
    complexity_score = analysis['complexity_score']
    big_o = analysis['big_o']
    feats = analysis['features']
    
    # ═══════════════════════════════════════════════════════════════
    # MAIN ANALYSIS TABLE
    # ═══════════════════════════════════════════════════════════════
    table = Table(title="[cyan]CODE ANALYSIS RESULTS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", style="white", width=50)
    
    # Complexity Section
    table.add_row("[bold]Complexity Class[/bold]", f"[bold yellow]{big_o}[/bold yellow]")
    table.add_row("Complexity Score", f"{create_progress_bar(complexity_score, 100)} {complexity_score:.0f}/100")
    table.add_row("Risk Level", f"{create_risk_score(complexity_score, big_o)}")
    
    # Code Metrics
    table.add_row("[bold]Code Metrics[/bold]", "")
    table.add_row("  Loops", f"[yellow]{feats.get('num_loops', 0)}[/yellow]")
    table.add_row("  Max Loop Depth", f"[yellow]{feats.get('max_loop_depth', 0)}[/yellow]")
    table.add_row("  Function Calls", f"[cyan]{feats.get('num_function_calls', 0)}[/cyan]")
    
    # File Stats
    if file_size_kb is not None:
        table.add_row("[bold]File Information[/bold]", "")
        table.add_row("  File Size", f"{file_size_kb} KB")
        table.add_row("  Total Lines", f"{total_lines}")
        table.add_row("  Blank Lines", f"{blank_lines}")
        table.add_row("  Comment Lines", f"{comment_lines}")
    
    # Energy Prediction
    if energy is not None:
        # Calculate memory usage and energy breakdown
        memory_mb = estimate_memory_usage(feats.get('num_loops', 0), feats.get('max_loop_depth', 0))
        memory_energy = memory_mb * 0.5  # Rough estimate: ~0.5J per MB
        total_energy = energy + memory_energy
        
        kwh = total_energy / 3_600_000
        cost = kwh * 0.15
        co2 = kwh * 500
        
        table.add_row("[bold]Energy Analysis[/bold]", "")
        table.add_row("  Execution Energy", f"{create_energy_bar(energy)}")
        table.add_row("  Memory Consumption", f"{memory_mb:.3f} MB")
        table.add_row("  Memory Energy Consumption", f"{create_energy_bar(memory_energy, max_energy=2.0)}")
        table.add_row("[bold]  Total Energy[/bold]", f"[bold green]{create_energy_bar(total_energy, max_energy=2.0)}[/bold green]")
        table.add_row("  Confidence", f"{confidence*100:.0f}%")
        table.add_row("  Energy (kWh)", f"{kwh:.8f} kWh")
        table.add_row("  Est. Cost (USA)", f"[green]${cost:.6f}[/green]")
        table.add_row("  Est. CO2", f"[red]{co2:.2f} g[/red]")
    
    # Performance
    if analysis_time > 0:
        table.add_row("[bold]Analysis Performance[/bold]", "")
        table.add_row("  Analysis Time", f"{analysis_time:.3f} seconds")
    
    console.print(table)
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLEXITY TIMELINE TABLE
    # ═══════════════════════════════════════════════════════════════
    timeline_table = Table(title="[cyan]COMPLEXITY TIMELINE[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    timeline_table.add_column("Input Size", style="yellow", width=18)
    timeline_table.add_column("Estimated Time", style="white", width=45)
    timeline_table.add_column("Verdict", style="white", width=18)
    
    timeline = create_complexity_timeline(big_o)
    for n, runtime in timeline:
        if runtime >= 1e6:
            time_str = "TOO SLOW"
            verdict = "[red]CRITICAL[/red]"
        elif runtime >= 10:
            time_str = f"{runtime:.1f} seconds"
            verdict = "[red]POOR[/red]"
        elif runtime >= 0.1:
            time_str = f"{runtime*1000:.1f} ms"
            verdict = "[yellow]MODERATE[/yellow]"
        else:
            time_str = f"{runtime*1000:.3f} ms"
            verdict = "[green]GOOD[/green]"
        
        bar = "█" * int(min(runtime / 10, 15)) + "░" * max(0, 15 - int(min(runtime / 10, 15)))
        timeline_table.add_row(f"n={n}", f"{bar} {time_str}", verdict)
    
    console.print(timeline_table)
    
    # ═══════════════════════════════════════════════════════════════
    # ISSUES TABLE
    # ═══════════════════════════════════════════════════════════════
    warnings = []
    suggestions = []
    
    # Complexity-based issues
    if feats.get('nested_loops'):
        warnings.append("[red]⚠️  Nested loops detected (O(n²) complexity)[/red]")
        suggestions.append("[yellow]Nested Loops:[/yellow]\n  ❌ for i in data: for j in data: pass\n  ✅ Use set() or dict lookup")
    
    if feats.get('has_recursion'):
        warnings.append("[red]⚠️  Recursion detected - may be exponential[/red]")
        suggestions.append("[yellow]Recursion:[/yellow]\n  ❌ fib(n) = fib(n-1)+fib(n-2)\n  ✅ @functools.cache or DP")
    
    if feats.get('string_concat_in_loop'):
        warnings.append("[yellow]⚠️  String concatenation in loop (O(n²) behavior)[/yellow]")
        suggestions.append("[yellow]String Build:[/yellow]\n  ❌ result += str(x)\n  ✅ ''.join(map(str, data))")
    
    # Energy-based issues
    complexity_score = feats.get('complexity_score', 0)
    if complexity_score > 85:
        warnings.append("[red]⚠️  CRITICAL: Very high complexity score (>85)[/red]")
        suggestions.append("[yellow]High Complexity:[/yellow]\n  Refactor into smaller functions or use better algorithms")
    elif complexity_score > 70:
        warnings.append("[yellow]⚠️  HIGH: Complexity score above 70[/yellow]")
        suggestions.append("[yellow]Moderate Complexity:[/yellow]\n  Profile & optimize bottlenecks; use profiling tools")
    
    if energy and energy > 2.0:
        warnings.append("[red]⚠️  High energy consumption predicted (>2.0J)[/red]")
        suggestions.append("[yellow]Energy Optimization:[/yellow]\n  Reduce loops, cache results, use efficient data structures")
    
    loop_depth = feats.get('max_loop_depth', 0)
    if loop_depth > 2:
        warnings.append(f"[red]⚠️  Deep nesting detected (depth={loop_depth}, O(n^{loop_depth}))[/red]")
        suggestions.append("[yellow]Deep Nesting:[/yellow] Reduce nesting levels using early returns or helper functions")
    
    # Performance tips
    num_loops = feats.get('num_loops', 0)
    if num_loops > 5:
        suggestions.append("[yellow]Multiple Loops:[/yellow] Check if loops can be combined or parallelized")
    
    if feats.get('num_function_calls', 0) > 20:
        suggestions.append("[yellow]Function Calls:[/yellow] High call count may indicate overhead; inline critical paths")
    
    if not (warnings or suggestions):
        suggestions.append("[green]✓ Code looks efficient! No major issues detected.[/green]")
    
    if warnings or suggestions:
        issues_table = Table(title="[cyan]ISSUES & RECOMMENDATIONS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
        issues_table.add_column("Type", style="white", width=15)
        issues_table.add_column("Details", style="white", width=65)
        
        for w in warnings:
            issues_table.add_row("[bold red]⚠️ WARNING[/bold red]", w)
        
        for s in suggestions:
            issues_table.add_row("[bold green]💡 TIP[/bold green]", s)
        
        console.print(issues_table)
    
    if detailed:
        features_table = Table(title="[cyan]DETAILED FEATURES[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
        features_table.add_column("Feature", style="cyan", width=35)
        features_table.add_column("Value", style="white", width=45)
        
        for k, v in feats.items():
            features_table.add_row(k, str(v))
        
        console.print(features_table)
    
    console.print()


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
        
        # ═══════════════════════════════════════════════════════════════
        # BENCHMARK RESULTS TABLE
        # ═══════════════════════════════════════════════════════════════
        energy_j = result['energy_joules']
        kwh = energy_j / 3_600_000
        cost = kwh * 0.15
        co2 = kwh * 500
        
        bench_table = Table(title="[cyan]BENCHMARK RESULTS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
        bench_table.add_column("Metric", style="cyan", width=25)
        bench_table.add_column("Value", style="white", width=55)
        
        # Energy Section
        bench_table.add_row("[bold]Energy Consumption[/bold]", "")
        bench_table.add_row("  Total Energy", f"{create_energy_bar(energy_j)}")
        bench_table.add_row("  Per Iteration", f"{energy_j/iterations:.2f} J")
        
        # Performance Section
        bench_table.add_row("[bold]Execution Metrics[/bold]", "")
        bench_table.add_row("  Duration", f"{result['duration_seconds']:.3f} seconds")
        bench_table.add_row("  CPU Usage (Avg)", f"{create_progress_bar(result['cpu_percent'], 100)} {result['cpu_percent']:.1f}%")
        bench_table.add_row("  Power (Avg)", f"{result['power_watts']:.2f} W")
        
        # Environmental Section
        bench_table.add_row("[bold]Environmental Impact[/bold]", "")
        bench_table.add_row("  Energy (kWh)", f"{kwh:.8f} kWh")
        bench_table.add_row("  Est. Cost (USA)", f"[green]${cost:.6f}[/green]")
        bench_table.add_row("  Est. CO2", f"[red]{co2:.2f} g[/red]")
        
        # Details Section
        bench_table.add_row("[bold]Benchmark Details[/bold]", "")
        bench_table.add_row("  Iterations", f"{iterations}")
        bench_table.add_row("  Total Time", f"{benchmark_time:.3f} seconds")
        bench_table.add_row("  File Size", f"{file_size_kb} KB")
        bench_table.add_row("  Total Lines", f"{total_lines}")
        
        console.print(bench_table)
        
        # Efficiency Verdict
        verdict_table = Table(title="[cyan]EFFICIENCY VERDICT[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
        verdict_table.add_column("Status", style="white", width=80)
        
        if result['cpu_percent'] < 5:
            verdict_table.add_row("[green]EXCELLENT[/green] - Very low CPU usage, efficient code execution")
        elif result['cpu_percent'] < 25:
            verdict_table.add_row("[green]GOOD[/green] - Low CPU usage, decent efficiency")
        elif result['cpu_percent'] < 50:
            verdict_table.add_row("[yellow]MODERATE[/yellow] - Moderate CPU usage, optimization possible")
        else:
            verdict_table.add_row("[red]HIGH[/red] - High CPU usage, significant optimization opportunity")
        
        console.print(verdict_table)
        console.print()
            
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
    comp_table = Table(title="[cyan]IMPLEMENTATION COMPARISON[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    comp_table.add_column("Metric", style="cyan", width=25)
    comp_table.add_column(results[0]['file'], style="yellow", width=25)
    comp_table.add_column(results[1]['file'], style="green", width=25)
    
    # Core Metrics
    comp_table.add_row("[bold]Complexity Class[/bold]", results[0]['big_o'], results[1]['big_o'])
    comp_table.add_row("Score", f"[yellow]{results[0]['score']:.0f}/100[/yellow]", f"[green]{results[1]['score']:.0f}/100[/green]")
    
    # Energy Metrics
    comp_table.add_row("[bold]Energy[/bold]", f"[yellow]{results[0]['energy']:.2f} J[/yellow]", f"[green]{results[1]['energy']:.2f} J[/green]")
    comp_table.add_row("Confidence", f"{results[0]['confidence']*100:.0f}%", f"{results[1]['confidence']*100:.0f}%")
    
    # Code Metrics
    comp_table.add_row("[bold]Code Size[/bold]", f"{results[0]['size']} KB", f"{results[1]['size']} KB")
    comp_table.add_row("Total Lines", str(results[0]['lines']), str(results[1]['lines']))
    
    # Performance
    comp_table.add_row("[bold]Memory[/bold]", f"{results[0]['memory_mb']:.3f} MB", f"{results[1]['memory_mb']:.3f} MB")
    comp_table.add_row("1000 ops", f"{results[0]['runtime_1k']:.2f} ms", f"{results[1]['runtime_1k']:.2f} ms")
    
    console.print(comp_table)
    
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
    
    # Improvements Table
    improvements_table = Table(title="[cyan]PERFORMANCE IMPROVEMENTS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    improvements_table.add_column("Metric", style="cyan", width=20)
    improvements_table.add_column("Improvement", style="white", width=65)
    
    energy_color = "green" if energy_improvement > 0 else "red"
    memory_color = "green" if memory_improvement > 0 else "red"
    time_color = "green" if time_improvement > 0 else "red"
    
    improvements_table.add_row("Energy", f"{create_progress_bar(abs(energy_improvement), 100)} [{energy_color}]{energy_improvement:+.1f}%[/{energy_color}]")
    improvements_table.add_row("Memory", f"{create_progress_bar(abs(memory_improvement), 100)} [{memory_color}]{memory_improvement:+.1f}%[/{memory_color}]")
    improvements_table.add_row("Speed", f"{create_progress_bar(abs(time_improvement), 100)} [{time_color}]{time_improvement:+.1f}%[/{time_color}]")
    
    console.print(improvements_table)
    
    # Environmental Impact Table
    kwh_1 = results[0]['energy'] / 3_600_000
    co2_1 = kwh_1 * 500
    km_1 = co2_1 / 120
    
    kwh_2 = results[1]['energy'] / 3_600_000
    co2_2 = kwh_2 * 500
    km_2 = co2_2 / 120
    
    co2_saved = co2_1 - co2_2
    km_saved = km_1 - km_2
    
    env_table = Table(title="[cyan]ENVIRONMENTAL IMPACT[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    env_table.add_column("Implementation", style="cyan", width=28)
    env_table.add_column("CO2 (grams)", style="white", width=20)
    env_table.add_column("Equivalent (km)", style="white", width=20)
    
    env_table.add_row(results[0]['file'], f"{co2_1:.2f}g", f"{km_1:.3f} km")
    env_table.add_row(results[1]['file'], f"[green]{co2_2:.2f}g[/green]", f"[green]{km_2:.3f} km[/green]")
    
    if co2_saved > 0:
        env_table.add_row("[bold green]SAVED[/bold green]", f"[bold green]{co2_saved:.2f}g[/bold green]", f"[bold green]{km_saved:.3f} km[/bold green]")
    else:
        env_table.add_row("[bold red]INCREASE[/bold red]", f"[bold red]{abs(co2_saved):.2f}g[/bold red]", f"[bold red]{abs(km_saved):.3f} km[/bold red]")
    
    console.print(env_table)
    
    # Recommendation Table
    overall_improvement = (energy_improvement + memory_improvement + time_improvement) / 3
    
    rec_table = Table(title="[cyan]RECOMMENDATION[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
    rec_table.add_column("Status", style="white", width=90)
    
    if overall_improvement > 30:
        rec_table.add_row(f"[bold green]HIGHLY RECOMMENDED[/bold green] - Major improvements ({overall_improvement:.1f}% better). Use [bold]{results[1]['file']}[/bold]")
    elif overall_improvement > 10:
        rec_table.add_row(f"[bold cyan]RECOMMENDED[/bold cyan] - Good improvements ({overall_improvement:.1f}% better). Consider using [bold]{results[1]['file']}[/bold]")
    elif overall_improvement > 0:
        rec_table.add_row(f"[bold yellow]MARGINAL IMPROVEMENT[/bold yellow] - Slight gains ({overall_improvement:.1f}%). Choose based on code clarity")
    else:
        rec_table.add_row(f"[bold red]NOT RECOMMENDED[/bold red] - Impl 2 performs worse ({overall_improvement:.1f}%). Keep using [bold]{results[0]['file']}[/bold]")
    
    console.print(rec_table)
    console.print()


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
        refactor_table = Table(title="[cyan]REFACTORING RESULTS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
        refactor_table.add_column("Metric", style="cyan", width=22)
        refactor_table.add_column("Original", style="red", width=20)
        refactor_table.add_column("Refactored", style="green", width=20)
        
        orig_score = original_analysis['complexity_score']
        ref_score = refactored_analysis['complexity_score'] if refactored_analysis else 0
        
        refactor_table.add_row("[bold]Complexity[/bold]", original_analysis['big_o'], 
                      refactored_analysis['big_o'] if refactored_analysis else "N/A")
        refactor_table.add_row("Score", f"[red]{orig_score:.0f}/100[/red]", 
                      f"[green]{ref_score:.0f}/100[/green]")
        
        console.print(refactor_table)
        
        # Display applied optimizations in a table
        if optimizations:
            opt_table = Table(title="[cyan]APPLIED OPTIMIZATIONS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
            opt_table.add_column("Index", style="cyan", width=8)
            opt_table.add_column("Optimization", style="white", width=72)
            
            for i, opt in enumerate(optimizations, 1):
                opt_clean = opt.replace('✨', '').replace('✅', '').replace('❌', '')
                opt_table.add_row(f"{i}", opt_clean)
            
            console.print(opt_table)
        else:
            console.print("\n[yellow]No optimizations were applicable to this code[/yellow]")
        
        # Show improvement
        if refactored_analysis:
            score_improvement = ref_score - orig_score
            
            improve_table = Table(title="[cyan]IMPROVEMENT ANALYSIS[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
            improve_table.add_column("Result", style="white", width=90)
            
            if score_improvement < 0:
                improvement_pct = abs(score_improvement) / orig_score * 100 if orig_score > 0 else 0
                improve_table.add_row(f"[bold green]Score Improved: {abs(score_improvement):.0f} points ({improvement_pct:.1f}%)[/bold green] - Complexity reduced from O({original_analysis['big_o']}) to O({refactored_analysis['big_o']})")
            elif score_improvement > 0:
                improve_table.add_row(f"[yellow]Score changed: +{score_improvement:.0f} points (slight regression)[/yellow]")
            else:
                improve_table.add_row(f"[cyan]No change in complexity score[/cyan]")
            
            console.print(improve_table)
        
        # Code Preview
        if output:
            with open(output, 'w') as f:
                f.write(refactored_code)
            saved_table = Table(title="[cyan]CODE SAVED[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
            saved_table.add_column("Status", style="white", width=90)
            saved_table.add_row(f"[bold green]Refactored code saved to: {output}[/bold green]")
            console.print(saved_table)
        else:
            preview_table = Table(title="[cyan]REFACTORED CODE PREVIEW[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
            preview_table.add_column("Code", style="dim", width=90)
            
            # Show first 50 lines
            lines = refactored_code.split('\n')[:50]
            preview_table.add_row('\n'.join(lines))
            if len(refactored_code.split('\n')) > 50:
                preview_table.add_row(f"[dim]... ({len(refactored_code.split(chr(10))) - 50} more lines) ...[/dim]")
            
            console.print(preview_table)
            
    except Exception as e:
        console.print(f"[red][NO] Error during refactoring: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@cli.command()
@click.option('--samples', default=100, help='Number of training samples')
def train(samples):
    """Generate training data and train ML model"""
    
    # Import here to avoid slow startup
    from src.data.generate_data import TrainingDataGenerator
    
    # Generate data with progress
    generator = TrainingDataGenerator()
    dataset = generator.generate_dataset(num_samples=samples)
    generator.save_dataset(dataset)
    
    # Dataset generation table
    dataset_table = Table(title="[cyan]DATASET GENERATION[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    dataset_table.add_column("Metric", style="cyan", width=25)
    dataset_table.add_column("Value", style="white", width=50)
    
    dataset_table.add_row("Samples Generated", f"[bold green]{len(dataset)}[/bold green]")
    dataset_table.add_row("Saved Location", "data/training_data.pkl")
    
    console.print(dataset_table)
    
    # Train model
    training_table = Table(title="[cyan]MODEL TRAINING[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    training_table.add_column("Metric", style="cyan", width=25)
    training_table.add_column("Value", style="white", width=50)
    
    predictor = EnergyPredictor()
    X, y = predictor.prepare_data(dataset)
    
    train_size = int(len(X) * 0.8)
    test_size = int(len(X) * 0.2)
    
    training_table.add_row("Training Samples", f"{train_size}")
    training_table.add_row("Test Samples", f"{test_size}")
    training_table.add_row("Total Samples", f"{len(X)}")
    
    predictor.train(X, y)
    predictor.save()
    
    training_table.add_row("Model Status", "[bold green]Trained & Saved[/bold green]")
    
    console.print(training_table)
    
    # Training complete table
    complete_table = Table(title="[cyan]TRAINING COMPLETE[/cyan]", show_header=False, border_style="cyan", padding=(0, 1))
    complete_table.add_column("Status", style="white", width=90)
    
    complete_table.add_row("[bold green]✓ Success![/bold green] Model trained and saved successfully")
    console.print(complete_table)
    
    # Files saved table
    files_table = Table(title="[cyan]FILES SAVED[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    files_table.add_column("File Type", style="cyan", width=20)
    files_table.add_column("Location", style="white", width=50)
    
    files_table.add_row("Model", "models/energy_model.pkl")
    files_table.add_row("Training Data", "data/training_data.pkl")
    
    console.print(files_table)
    
    # Next steps table
    nextsteps_table = Table(title="[cyan]NEXT STEPS[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan", padding=(0, 1))
    nextsteps_table.add_column("Command", style="yellow", width=50)
    nextsteps_table.add_column("Description", style="white", width=40)
    
    nextsteps_table.add_row("$ energylens analyze <file>", "Analyze a Python file")
    nextsteps_table.add_row("$ energylens compare <f1> <f2>", "Compare implementations")
    nextsteps_table.add_row("$ energylens benchmark <file>", "Benchmark code execution")
    
    console.print(nextsteps_table)
    console.print()


@cli.command()
def info():
    """Show information about EnergyLens"""
    
    # Title
    title_table = Table(show_header=False, border_style="cyan")
    title_table.add_column("", style="bold cyan")
    title_table.add_row("[bold cyan]ENERGYLENS AI - Machine Learning Code Energy Analyzer[/bold cyan]")
    console.print(title_table)
    console.print()
    
    # Key Features Table
    features_table = Table(title="[cyan]KEY FEATURES[/cyan]", show_header=False, border_style="cyan")
    features_table.add_column("Features", style="white", width=88)
    
    features = [
        "✓ Static code complexity analysis (Big-O detection)",
        "✓ ML-powered energy consumption prediction (91% accuracy)",
        "✓ Actionable optimization suggestions with impact metrics",
        "✓ Side-by-side implementation comparison",
        "✓ Actual energy benchmarking and profiling",
        "✓ Automatic code refactoring with 8+ patterns",
        "✓ Environmental impact tracking (CO2, costs)"
    ]
    for f in features:
        features_table.add_row(f)
    
    console.print(features_table)
    
    # Quick Start Table
    quick_table = Table(title="[cyan]QUICK START GUIDE[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan")
    quick_table.add_column("Step", style="yellow", width=8)
    quick_table.add_column("Action", style="white", width=80)
    
    quick_table.add_row("1", "[yellow]Train the model[/yellow] (one-time setup)\n$ energylens train --samples 100")
    quick_table.add_row("2", "[yellow]Analyze your code[/yellow]\n$ energylens analyze your_code.py")
    quick_table.add_row("3", "[yellow]Get optimizations[/yellow]\n$ energylens refactor your_code.py -o optimized.py")
    
    console.print(quick_table)
    
    # Command Reference Table
    cmd_table = Table(title="[cyan]COMMAND REFERENCE[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan")
    cmd_table.add_column("Command", style="cyan", width=18)
    cmd_table.add_column("Description", style="white", width=70)
    
    commands = {
        "analyze": "Analyze code complexity and predict energy consumption",
        "benchmark": "Run code and measure actual energy usage",
        "compare": "Compare energy of two implementations",
        "refactor": "Apply automatic optimizations to code",
        "train": "Train/retrain the ML energy prediction model",
        "info": "Show this help information"
    }
    for cmd, desc in commands.items():
        cmd_table.add_row(f"energylens {cmd}", desc)
    
    console.print(cmd_table)
    
    # Common Examples Table
    examples_table = Table(title="[cyan]COMMON EXAMPLES[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan")
    examples_table.add_column("Use Case", style="yellow", width=25)
    examples_table.add_column("Command", style="white", width=63)
    
    examples_table.add_row("Analyze with details", "energylens analyze code.py --detailed")
    examples_table.add_row("Compare two versions", "energylens compare bad.py good.py")
    examples_table.add_row("Refactor and save", "energylens refactor code.py -o optimized.py")
    examples_table.add_row("Benchmark 50 times", "energylens benchmark code.py --iterations 50")
    
    console.print(examples_table)
    
    # Complexity Classes Table
    complexity_table = Table(title="[cyan]COMPLEXITY CLASSES GUIDE[/cyan]", show_header=True, header_style="bold cyan", border_style="cyan")
    complexity_table.add_column("Big-O", style="cyan", width=10)
    complexity_table.add_column("Rating", style="white", width=15)
    complexity_table.add_column("Description", style="white", width=63)
    
    complexity_info = [
        ("O(1)", "[green]BEST[/green]", "Constant time - excellent"),
        ("O(log n)", "[green]VERY GOOD[/green]", "Logarithmic - great performance"),
        ("O(n)", "[yellow]GOOD[/yellow]", "Linear - acceptable"),
        ("O(n log n)", "[yellow]MODERATE[/yellow]", "Decent performance"),
        ("O(n²)", "[red]POOR[/red]", "Quadratic - avoid if possible"),
        ("O(n³)", "[red]VERY POOR[/red]", "Cubic - major optimization needed"),
        ("O(2^n)", "[dark_red]WORST[/dark_red]", "Exponential - severe issue")
    ]
    for bigO, level, desc in complexity_info:
        complexity_table.add_row(bigO, level, desc)
    
    console.print(complexity_table)
    console.print()
    
    display_section_header("OPTIMIZATION PATTERNS", "")
    patterns = [
        "String concatenation in loops → join()",
        "List lookup in loops → set lookup",
        "List comprehension optimization",
        "Nested duplicate detection → hashing",
        "Manual counting → Counter()",
        "Regex recompilation → precompile",
        "Bubble sort → Timsort",
        "Multiple I/O passes → single pass"
    ]
    for i, pattern in enumerate(patterns, 1):
        console.print(f"  {i}. {pattern}")
    
    console.print()


if __name__ == '__main__':
    cli()
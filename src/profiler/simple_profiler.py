"""
Simple Energy Profiler
Measures energy consumption by monitoring CPU usage
"""
import time
import psutil


class SimpleEnergyProfiler:
    """
    Estimates energy consumption based on CPU usage
    Formula: Power = Idle_Power + (TDP - Idle_Power) × CPU_Usage
    """
    
    def __init__(self, tdp=65.0, idle_power=5.0):
        """
        Args:
            tdp: Thermal Design Power of CPU in watts (default: 65W)
            idle_power: Idle power consumption in watts (default: 5W)
        """
        self.tdp = tdp
        self.idle_power = idle_power
    
    def profile_code(self, code: str, iterations: int = 10):
        """
        Execute code and measure energy consumption
        
        Args:
            code: Python code as string
            iterations: Number of times to run code
            
        Returns:
            dict with energy_joules, duration_seconds, cpu_percent
        """
        # Compile code once
        try:
            compiled_code = compile(code, '<string>', 'exec')
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {e}")
        
        # Warm-up run (don't measure this)
        try:
            exec(compiled_code, {})
        except Exception as e:
            raise RuntimeError(f"Code execution failed: {e}")
        
        # Actual measurement
        cpu_samples = []
        start_time = time.time()
        
        for _ in range(iterations):
            # Measure CPU before and after
            cpu_before = psutil.cpu_percent(interval=0.01)
            exec(compiled_code, {})
            cpu_after = psutil.cpu_percent(interval=0.01)
            
            # Average of before and after
            cpu_samples.append((cpu_before + cpu_after) / 2)
        
        end_time = time.time()
        
        # Calculate statistics
        duration = end_time - start_time
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        
        # Estimate power consumption
        # Power increases linearly with CPU usage
        power_watts = self.idle_power + (self.tdp - self.idle_power) * (avg_cpu / 100)
        
        # Energy = Power × Time
        energy_joules = power_watts * duration
        
        return {
            'energy_joules': energy_joules,
            'duration_seconds': duration,
            'cpu_percent': avg_cpu,
            'power_watts': power_watts
        }
    
    def profile_function(self, func, *args, iterations=10, **kwargs):
        """
        Profile a Python function
        
        Args:
            func: Function to profile
            *args, **kwargs: Arguments to pass to function
            iterations: Number of times to run
            
        Returns:
            dict with energy measurements
        """
        cpu_samples = []
        start_time = time.time()
        
        # Warm up
        func(*args, **kwargs)
        
        # Measure
        for _ in range(iterations):
            cpu_before = psutil.cpu_percent(interval=0.01)
            func(*args, **kwargs)
            cpu_after = psutil.cpu_percent(interval=0.01)
            cpu_samples.append((cpu_before + cpu_after) / 2)
        
        duration = time.time() - start_time
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        power_watts = self.idle_power + (self.tdp - self.idle_power) * (avg_cpu / 100)
        energy_joules = power_watts * duration
        
        return {
            'energy_joules': energy_joules,
            'duration_seconds': duration,
            'cpu_percent': avg_cpu,
            'power_watts': power_watts
        }


# Test the profiler
if __name__ == '__main__':
    profiler = SimpleEnergyProfiler()
    
    # Test code
    test_code = """
result = 0
for i in range(1000):
    result += i
"""
    
    print("Testing Energy Profiler...")
    result = profiler.profile_code(test_code, iterations=10)
    
    print(f"✅ Energy: {result['energy_joules']:.2f} J")
    print(f"✅ Duration: {result['duration_seconds']:.3f} s")
    print(f"✅ CPU Usage: {result['cpu_percent']:.1f}%")
    print(f"✅ Power: {result['power_watts']:.2f} W")
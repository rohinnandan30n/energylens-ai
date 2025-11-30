"""
Training Data Generator
Creates synthetic code samples and measures their energy
"""
import random
import pickle
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.profiler.simple_profiler import SimpleEnergyProfiler
from src.analyzer.complexity_analyzer import ComplexityAnalyzer


class TrainingDataGenerator:
    """Generate synthetic code samples with energy measurements"""
    
    def __init__(self):
        self.profiler = SimpleEnergyProfiler()
        self.analyzer = ComplexityAnalyzer()
    
    def generate_code_sample(self, code_type: str) -> str:
        """Generate code of specific type"""
        
        if code_type == 'simple_loop':
            n = random.randint(100, 5000)
            return f"""
result = 0
for i in range({n}):
    result += i
"""
        
        elif code_type == 'nested_loop':
            n = random.randint(10, 100)
            m = random.randint(10, 100)
            return f"""
result = 0
for i in range({n}):
    for j in range({m}):
        result += i * j
"""
        
        elif code_type == 'list_operations':
            n = random.randint(100, 3000)
            return f"""
data = []
for i in range({n}):
    data.append(i * 2)
result = sum(data)
"""
        
        elif code_type == 'sorting':
            n = random.randint(100, 3000)
            return f"""
data = list(range({n}, 0, -1))
result = sorted(data)
"""
        
        elif code_type == 'dict_operations':
            n = random.randint(100, 2000)
            return f"""
data = {{}}
for i in range({n}):
    data[i] = i * 2
result = sum(data.values())
"""
        
        else:  # simple
            n = random.randint(10, 1000)
            return f"result = sum(range({n}))"
    
    def generate_dataset(self, num_samples: int = 100) -> list:
        """
        Generate dataset of code samples with energy measurements
        
        Args:
            num_samples: Number of samples to generate
            
        Returns:
            List of dicts with 'features' and 'energy'
        """
        print(f"🔄 Generating {num_samples} training samples...")
        print("This will take 5-10 minutes...\n")
        
        dataset = []
        code_types = [
            'simple_loop',
            'nested_loop',
            'list_operations',
            'sorting',
            'dict_operations',
            'simple'
        ]
        
        for i in range(num_samples):
            # Pick random code type
            code_type = random.choice(code_types)
            
            try:
                # Generate code
                code = self.generate_code_sample(code_type)
                
                # Measure energy
                measurement = self.profiler.profile_code(code, iterations=5)
                
                # Analyze complexity
                analysis = self.analyzer.analyze(code)
                
                # Store
                dataset.append({
                    'code_type': code_type,
                    'features': analysis['features'],
                    'energy': measurement['energy_joules'],
                    'big_o': analysis['big_o']
                })
                
                # Progress update
                if (i + 1) % 10 == 0:
                    avg_energy = sum(d['energy'] for d in dataset) / len(dataset)
                    print(f"  Progress: {i + 1}/{num_samples} | Avg Energy: {avg_energy:.2f} J")
            
            except Exception as e:
                print(f"  ⚠️  Error with sample {i + 1}: {e}")
                continue
        
        print(f"\n✅ Generated {len(dataset)} valid samples")
        print(f"📊 Energy range: {min(d['energy'] for d in dataset):.2f} - {max(d['energy'] for d in dataset):.2f} J")
        
        return dataset
    
    def save_dataset(self, dataset: list, filename: str = 'training_data.pkl'):
        """Save dataset to file"""
        filepath = Path('data') / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(dataset, f)
        
        print(f"💾 Dataset saved to {filepath}")
    
    def load_dataset(self, filename: str = 'training_data.pkl') -> list:
        """Load dataset from file"""
        filepath = Path('data') / filename
        
        with open(filepath, 'rb') as f:
            dataset = pickle.load(f)
        
        print(f"📂 Loaded {len(dataset)} samples from {filepath}")
        return dataset


# Main execution
if __name__ == '__main__':
    generator = TrainingDataGenerator()
    
    # Generate 100 samples (takes 5-10 minutes)
    dataset = generator.generate_dataset(num_samples=100)
    
    # Save for later use
    generator.save_dataset(dataset)
    
    print("\n✅ Data generation complete!")
"""
Static Code Complexity Analyzer
Analyzes Python code without executing it
"""
import ast
from typing import Dict, List


class ComplexityAnalyzer:
    """
    Analyzes code complexity by parsing Abstract Syntax Tree (AST)
    Extracts features useful for energy prediction
    """
    
    def analyze(self, code: str) -> Dict:
        """
        Analyze code and return complexity metrics
        
        Args:
            code: Python code as string
            
        Returns:
            dict with features and estimated complexity
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {e}")
        
        # Extract features
        features = self._extract_features(tree)
        
        # Estimate Big-O complexity
        big_o = self._estimate_big_o(features)
        
        return {
            'features': features,
            'big_o': big_o,
            'complexity_score': self._calculate_score(features)
        }
    
    def _extract_features(self, tree: ast.AST) -> Dict[str, float]:
        """Extract numerical features from AST"""
        
        features = {
            'num_loops': 0,
            'max_loop_depth': 0,
            'num_function_calls': 0,
            'num_list_ops': 0,
            'has_recursion': 0,
            'nested_loops': 0,
            'has_sort': 0,
            'string_concat_in_loop': 0,
        }
        
        # Count loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                features['num_loops'] += 1
                depth = self._get_loop_depth(node)
                features['max_loop_depth'] = max(features['max_loop_depth'], depth)
                
                if depth >= 2:
                    features['nested_loops'] = 1
                
                # Check for string concatenation in loop
                if self._has_string_concat(node):
                    features['string_concat_in_loop'] = 1
            
            # Count function calls
            if isinstance(node, ast.Call):
                features['num_function_calls'] += 1
                
                # Check for list operations
                if hasattr(node.func, 'attr'):
                    if node.func.attr in ['append', 'extend', 'insert', 'remove']:
                        features['num_list_ops'] += 1
                    
                    # Check for sorting
                    if node.func.attr in ['sort', 'sorted']:
                        features['has_sort'] = 1
        
        # Check for recursion
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        for func in functions:
            if self._is_recursive(func):
                features['has_recursion'] = 1
                break
        
        return features
    
    def _get_loop_depth(self, node: ast.AST, depth: int = 1) -> int:
        """Calculate maximum nesting depth of loops"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._get_loop_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _is_recursive(self, func_node: ast.FunctionDef) -> bool:
        """Check if function calls itself"""
        func_name = func_node.name
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id == func_name:
                    return True
        
        return False
    
    def _has_string_concat(self, loop_node: ast.AST) -> bool:
        """Check if loop contains string concatenation"""
        for node in ast.walk(loop_node):
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, ast.Add):
                    return True
        return False
    
    def _estimate_big_o(self, features: Dict) -> str:
        """Estimate Big-O complexity from features"""
        
        if features['has_recursion']:
            return "O(2^n) or worse"
        
        depth = features['max_loop_depth']
        
        if depth >= 3:
            return f"O(n^{depth})"
        elif features['nested_loops'] or depth == 2:
            return "O(n²)"
        elif features['has_sort']:
            return "O(n log n)"
        elif features['num_loops'] > 0:
            return "O(n)"
        else:
            return "O(1)"
    
    def _calculate_score(self, features: Dict) -> float:
        """
        Calculate complexity score (0-100)
        Higher = more complex = likely more energy
        """
        score = 0
        
        # Loop complexity
        score += features['num_loops'] * 10
        score += features['max_loop_depth'] * 15
        score += features['nested_loops'] * 20
        
        # Function complexity
        score += features['num_function_calls'] * 2
        score += features['num_list_ops'] * 5
        
        # Special patterns
        score += features['has_recursion'] * 30
        score += features['has_sort'] * 10
        score += features['string_concat_in_loop'] * 15
        
        return min(100, score)  # Cap at 100


# Test the analyzer
if __name__ == '__main__':
    analyzer = ComplexityAnalyzer()
    
    # Test code with nested loops
    test_code = """
def find_duplicates(data):
    result = []
    for i in range(len(data)):
        for j in range(i+1, len(data)):
            if data[i] == data[j]:
                result.append(data[i])
    return result
"""
    
    print("Testing Complexity Analyzer...")
    analysis = analyzer.analyze(test_code)
    
    print(f"✅ Big-O: {analysis['big_o']}")
    print(f"✅ Complexity Score: {analysis['complexity_score']:.0f}/100")
    print(f"✅ Features:")
    for key, value in analysis['features'].items():
        print(f"   {key}: {value}")
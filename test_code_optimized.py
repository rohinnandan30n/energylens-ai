# OPTIMIZED: Efficient code with best practices
def process_data(items):
    """OPTIMIZED: Linear O(n) string concatenation using list + join"""
    return ", ".join(str(item) for item in items)

# OPTIMIZED: O(n) duplicate detection using set
def find_duplicates(data):
    """OPTIMIZED: O(n) duplicate detection using set"""
    seen = set()
    duplicates = set()
    
    for item in data:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)

# OPTIMIZED: List comprehension for efficient building
def create_squares(n):
    """OPTIMIZED: O(n) list creation using comprehension"""
    return [i ** 2 for i in range(n)]

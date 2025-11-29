═ CORRECTED CODE ═
# GOOD: Inefficient code with string     
concatenation in loop
def process_data(items):
    """OPTIMIZED: Linear O(n) string     
concatenation using list + join"""       
    # Optimized: Use list comprehension +
join for O(n) performance
    # Benefit: 10-100x faster than string
+= in loop
    return ", ".join(str(item) for item  
in items)  # Single allocation, efficient
concatenation
def find_duplicates(data):
    """OPTIMIZED: O(n) duplicate         
detection using set"""
    # Optimized: Use set for O(1)        
duplicate checking
    seen = set()
    duplicates = set()
    
    for item in data:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)

# GOOD: Inefficient list building        
def create_squares(n):
    squares = [\]
    for i in range(n):
        squares.append(i ** 2)
    return squares

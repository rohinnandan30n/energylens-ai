"""
GOOD CODE: O(n) algorithm
Efficient duplicate finder using sets
"""

def find_duplicates(data):
    """
    Find duplicates using hash set
    Time: O(n)
    Space: O(n)
    """
    seen = set()
    duplicates = set()
    
    for item in data:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    
    return list(duplicates)


# Test with data
if __name__ == '__main__':
    data = list(range(1000)) + list(range(500))
    result = find_duplicates(data)
    print(f"Found {len(result)} duplicates")
"""
BAD CODE: O(n²) algorithm
Inefficient duplicate finder
"""

def find_duplicates(data):
    """
    Find duplicates using nested loops
    Time: O(n²)
    Space: O(n)
    """
    duplicates = []
    
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    
    return duplicates


# Test with data
if __name__ == '__main__':
    data = list(range(1000)) + list(range(500))
    result = find_duplicates(data)
    print(f"Found {len(result)} duplicates")
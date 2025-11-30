"""GOOD: Use set for O(1) lookup"""
def filter_data(data, valid_items):
    valid_set = set(valid_items)  # Convert once
    result = []
    for item in data:
        if item in valid_set:  # O(1) lookup = O(n) total
            result.append(item)
    return result

if __name__ == '__main__':
    data = list(range(10000))
    valid = list(range(5000, 15000))
    filtered = filter_data(data, valid)
    print(f"Found: {len(filtered)}")
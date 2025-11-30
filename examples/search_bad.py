"""BAD: Linear search in list"""
def filter_data(data, valid_items):
    result = []
    for item in data:
        if item in valid_items:  # O(n) search each time = O(n²) total
            result.append(item)
    return result

if __name__ == '__main__':
    data = list(range(10000))
    valid = list(range(5000, 15000))
    filtered = filter_data(data, valid)
    print(f"Found: {len(filtered)}")
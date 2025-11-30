"""BAD: String concatenation in loop"""
def process_data(items):
    result = ""
    for item in items:
        result += str(item) + ","  # O(n²) - creates new string each time!
    return result

if __name__ == '__main__':
    data = list(range(5000))
    output = process_data(data)
    print(f"Length: {len(output)}")
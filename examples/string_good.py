"""GOOD: Use join() for strings"""
def process_data(items):
    return ",".join(str(item) for item in items)  # O(n)

if __name__ == '__main__':
    data = list(range(5000))
    output = process_data(data)
    print(f"Length: {len(output)}")
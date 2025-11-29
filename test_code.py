# BAD: Inefficient code with string concatenation in loop
def process_data(items):
    result = ""
    for item in items:
        result += str(item) + ", "
    return result

# BAD: Nested loops with O(n²) complexity
def find_duplicates(data):
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                duplicates.append(data[i])
    return duplicates

# BAD: Inefficient list building
def create_squares(n):
    squares = []
    for i in range(n):
        squares.append(i ** 2)
    return squares

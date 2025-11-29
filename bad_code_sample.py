# BAD: Inefficient recursive code with redundant calculations
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Exponential O(2^n) - recalculates same values

# BAD: Inefficient dictionary lookups in tight loop
def count_frequencies(items):
    freq = {}
    for item in items:
        if item in freq:
            freq[item] = freq[item] + 1
        else:
            freq[item] = 1
    return freq

# BAD: Inefficient regex in loop without compilation
import re
def validate_emails(emails):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    results = []
    for email in emails:
        if re.match(pattern, email):  # Recompiles regex on every iteration
            results.append(email)
    return results

# BAD: Inefficient nested sorting
def sort_data(records):
    sorted_records = []
    for record in records:
        sorted_records.append(record)
    for i in range(len(sorted_records)):
        for j in range(i+1, len(sorted_records)):
            if sorted_records[i][1] > sorted_records[j][1]:
                sorted_records[i], sorted_records[j] = sorted_records[j], sorted_records[i]
    return sorted_records

# BAD: Inefficient file reading with multiple passes
def process_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    word_count = 0
    for line in lines:
        word_count += len(line.split())
    
    char_count = 0
    for line in lines:
        char_count += len(line)
    
    return word_count, char_count

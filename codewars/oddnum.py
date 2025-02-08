def find_odd_number(arr):
    result = 0
    for num in arr:
        result ^= num  # XOR each number
    return result



def find_it(seq):
    for i in seq:
        if seq.count(i)%2!=0:
            return i




from collections import Counter

def find_odd_number(arr):
    # Count occurrences of each number
    counts = Counter(arr)
    
    # Find the number with an odd count
    for num, count in counts.items():
        if count % 2 == 1:  # Odd count
            return num
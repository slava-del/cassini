# arr=[1,2,3,4,5,6]

# indices=[]
# results=()
# prev=0
# for i in indices:
#     results.append(sum(arr[prev:i]))
#     prev=i
# results.append(sum(arr[prev:]))

# for res in results:
#     print(res)

numbers=[2,3,4,5,6]
target=6

def two_sum(numbers, target):
    for i in range(len(numbers)):
        for j in range (i+1,len(numbers)):
            if numbers[i] + numbers[j] == target:
                print(f'indices: {i}, {j}')
                return (i,j)
    return None

result = two_sum(numbers, target)
if result:
    print(f"Result: {result}")
else:
    print("No two numbers sum up to the target.")


def two_sum(nums, t):
    for i, x in enumerate(nums):
        for j, y in enumerate(nums):
            if i != j and x + y == t:
                return [i, j]
            
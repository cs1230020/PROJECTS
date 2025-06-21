import random

def generate_test_case(num_gates, max_width, max_height):
    gates = []
    for i in range(1, num_gates + 1):
        width = random.randint(1, max_width)
        height = random.randint(1, max_height)
        gates.append(f"G{i} {width} {height}")
    return gates

# Parameters for the test case
num_gates = 1000
max_width = 20
max_height = 20

gates = generate_test_case(num_gates, max_width, max_height)

# Save the test case to 'input.txt'
with open("input.txt", "w") as file:
    for gate in gates:
        file.write(gate + "\n")

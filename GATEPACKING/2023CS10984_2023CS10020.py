class Gate():
    def __init__(self, gate_id, width, height):
        self.gate_id = gate_id
        self.width = width
        self.height = height
        self.x = 0  
        self.y = 0  

class Circuit():
    def __init__(self, bin_width):
        self.bin_width = bin_width
        self.levels = []

    def check_fit(self, index, gate):
        lvl = self.levels[index]
        x_cord = 0
        for g in lvl:
            x_cord+= g.width
        if(x_cord + gate.width <= self.bin_width):
            return x_cord
        return False

    def place_gate(self, index,x_cord, gate):
        lvl = self.levels[index]
        gate.x = x_cord
        gate.y = 0
        for i in range(index):
            h = 0
            for g in self.levels[i]:
                h = max(g.height,h)
            gate.y+=h
                
        lvl.append(gate)

    def add_new_level(self, gate):
        gate.x = 0  
        gate.y = self.total_height()  
        self.levels.append([gate])

    def pack_gate(self, gate):
        for i in range(len(self.levels)):
            x_cord = self.check_fit(i, gate)
            if x_cord!=False:
                self.place_gate(i,x_cord, gate)
                return
        self.add_new_level(gate)  

    def total_height(self):
        return sum(max(g.height for g in lvl) for lvl in self.levels)

def ffdh(bin_width, gates):
    gates.sort(key=lambda g: g.height, reverse=True)
    circuit = Circuit(bin_width)
    for gate in gates:
        circuit.pack_gate(gate)
    return circuit

def print_packing(circuit):
    with open("output.txt", "w") as f:
        max_width_used = max(sum(g.width for g in lvl) for lvl in circuit.levels)
        total_height = circuit.total_height()
        f.write(f"bounding_box {max_width_used} {total_height}\n")
        for level in circuit.levels:
            for gate in level:
                f.write(f"{gate.gate_id} {gate.x} {gate.y}\n")
        f.write('final_assign.py')


gates = []
with open('input.txt', "r") as file:
    for line in file:
        gate_id, w, h = line.strip().split()
        gates.append(Gate(gate_id, int(w), int(h)))
bin_width = max(g.width for g in gates)


circuit = ffdh(bin_width, gates)
print_packing(circuit)

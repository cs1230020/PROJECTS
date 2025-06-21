class HashTable:
    def __init__(self, collision_type, params):
        self.collision_type = collision_type
        self.params = params
        self.num_elements = 0
        self.table_size = params[-1]
        
        if collision_type == "Chain":
            self.z1 = params[0]
            self.table = [[] for _ in range(self.table_size)]
        elif collision_type == "Linear":
            self.z1 = params[0]
            self.table = [None] * self.table_size
        else:
            self.c2, self.z1, self.z2 = params[2], params[0], params[1]
            self.table = [None] * self.table_size

    def hash(self, key, z):
        def char_value(c):
            if 'a' <= c <= 'z':
                return ord(c) - 97 
            elif 'A' <= c <= 'Z':
                return ord(c) - 65 + 26  
            return 0

        index_sum = 0
        for i, char in enumerate(key):
            index_sum += char_value(char) * (z ** i)
        return index_sum

    def get_slot(self, key):
        hash1 = self.hash(key, self.z1) % self.table_size
        if self.collision_type == "Double":
            hash2 = self.c2 - (self.hash(key, self.z2) % self.c2)
            return hash1, hash2
        return hash1

    def insert(self, x):
        key = x[0] if isinstance(x, tuple) else x  
        initial_slot = self.get_slot(key)
        
        if self.collision_type == "Chain":
            if self.table[initial_slot] is None:
                self.table[initial_slot] = []
            
            i = 0
            while i < len(self.table[initial_slot]):
                if self.table[initial_slot][i][0] == key:
                    self.table[initial_slot][i] = x
                    return
                i += 1
            self.table[initial_slot].append(x)
            self.num_elements += 1

        elif self.collision_type == "Linear":
            slot = initial_slot
            while self.table[slot] is not None:
                if isinstance(self.table[slot], tuple) and self.table[slot][0] == key:
                    self.table[slot] = x
                    return
                slot = (slot + 1) % self.table_size
                if slot == initial_slot:
                    raise Exception("Table is full")
            self.table[slot] = x
            self.num_elements += 1

        else:
            hash1, hash2 = initial_slot
            slot = hash1
            i = 0  
            while self.table[slot] is not None:
                if isinstance(self.table[slot], tuple) and self.table[slot][0] == key:
                    self.table[slot] = x
                    return
                i += 1
                slot = (hash1 + i * hash2) % self.table_size
                if slot == hash1:
                    raise Exception("Table is full")
            self.table[slot] = x
            self.num_elements += 1
    
    def get_load(self):
        return self.num_elements / self.table_size

    def __str__(self):
        output = []
        i = 0
        while i < self.table_size:
            if self.table[i] is None:
                output.append("<EMPTY>")
            elif self.collision_type == "Chain" and isinstance(self.table[i], list):
                output.append(" ; ".join(str(entry) for entry in self.table[i]))
            else:
                output.append(str(self.table[i]))
            i += 1
        return " | ".join(output)

    def find(self, key):
        initial_slot = self.get_slot(key)
        
        if self.collision_type == "Chain":
            if self.table[initial_slot] is not None:
                for element in self.table[initial_slot]:
                    if isinstance(element, tuple):
                        if element[0] == key:
                            return element[1]
                    elif element == key:
                        return True
            return None if isinstance(self, HashMap) else False

        elif self.collision_type == "Linear":
            slot = initial_slot
            while self.table[slot] is not None:
                element = self.table[slot]
                if isinstance(element, tuple) and element[0] == key:
                    return element[1]
                elif element == key:
                    return True
                slot = (slot + 1) % self.table_size
                if slot == initial_slot:
                    break
            return None if isinstance(self, HashMap) else False

        else:
            hash1, hash2 = initial_slot
            slot = hash1
            i = 0
            while self.table[slot] is not None:
                element = self.table[slot]
                if isinstance(element, tuple) and element[0] == key:
                    return element[1]
                elif element == key:
                    return True
                slot = (hash1 + i * hash2) % self.table_size
                if slot == hash1 and i > 0:
                    break
                i += 1
            return None if isinstance(self, HashMap) else False


class HashSet(HashTable):  
    def __init__(self, collision_type, params):
        super().__init__(collision_type, params)

    def insert(self, key):
        super().insert(key)

    def find(self, key):
        return super().find(key)

    def __str__(self):
        output = []
        for i in range(self.table_size):
            if self.table[i] is None or not self.table[i]:
                output.append("<EMPTY>")
            elif self.collision_type == "Chain":
                output.append(" ; ".join(str(entry) for entry in self.table[i]))
            else:
                output.append(str(self.table[i]))
        return " | ".join(output)

    def to_list(self):
        word_list = []
        i = 0
        while i < self.table_size:
            slot = self.table[i]
            if slot is not None:
                if isinstance(slot, list):
                    word_list.extend(slot)
                else:
                    word_list.append(slot)
            i += 1
        return word_list

class HashMap(HashTable):  
    def __init__(self, collision_type, params):
        super().__init__(collision_type, params)

    def insert(self, x):
        super().insert(x)

    def find(self, key):
        return super().find(key)

    def __str__(self):
        output = []
        i = 0
        while i < self.table_size:
            if self.table[i] is None or not self.table[i]:
                output.append("<EMPTY>")
            elif self.collision_type == "Chain" and isinstance(self.table[i], list):
                output.append(" ; ".join(f"({entry[0]}, {entry[1]})" for entry in self.table[i]))
            else:
                output.append(f"({self.table[i][0]}, {self.table[i][1]})")
            i += 1
        return " | ".join(output)
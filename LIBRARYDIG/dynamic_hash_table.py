from hash_table import HashSet, HashMap
from prime_generator import get_next_size

class DynamicHashSet(HashSet):
    def __init__(self, collision_type, params):
        super().__init__(collision_type, params)

    def rehash(self):
        
        old_table = self.table
        self.table_size = get_next_size()

        if self.collision_type == "Chain":
            self.table = [[] for _ in range(self.table_size)]
        else:
            self.table = [None] * self.table_size

        self.num_elements = 0

        i = 0
        while i < len(old_table):
            item = old_table[i]
            if item is not None:
                if isinstance(item, list):
                    j = 0
                    while j < len(item):
                        self.insert(item[j])
                        j += 1
                else:
                    self.insert(item)
            i += 1

    def insert(self, key):
       
        super().insert(key)
        if self.get_load() >= 0.5:
            self.rehash()

    def __iter__(self):
        
        if self.collision_type != "Chain":
            for item in self.table:
                if item is not None:
                    yield item
        else:
            i = 0
            while i < len(self.table):
                bucket = self.table[i]
                if bucket is not None:
                    j = 0
                    while j < len(bucket):
                        yield bucket[j]
                        j += 1
                i += 1

class DynamicHashMap(HashMap):
    def __init__(self, collision_type, params):
        super().__init__(collision_type, params)

    def rehash(self):
        
        old_table = self.table
        self.table_size = get_next_size()

        if self.collision_type != "Chain":
            self.table = [None] * self.table_size
        else:
            self.table = [[] for _ in range(self.table_size)]

        self.num_elements = 0

        i = 0
        while i < len(old_table):
            item = old_table[i]
            if item is not None:
                if isinstance(item, list):
                    j = 0
                    while j < len(item):
                        self.insert(item[j])
                        j += 1
                else:
                    self.insert(item)
            i += 1

    def insert(self, kv_pair):
        
        super().insert(kv_pair)
        if self.get_load() >= 0.5:
            self.rehash()

    def __iter__(self):
        
        if self.collision_type == "Chain":
            i = 0
            while i < len(self.table):
                bucket = self.table[i]
                if bucket is not None:
                    j = 0
                    while j < len(bucket):
                        yield bucket[j]
                        j += 1
                i += 1
        else:
            i = 0
            while i < len(self.table):
                item = self.table[i]
                if item is not None:
                    yield item
                i += 1
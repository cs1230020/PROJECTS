from crewmate import CrewMate
from heap import Heap
from treasure import Treasure
from custom import HeapSort
class StrawHatTreasury:
    def __init__(self, m):

        self.crewmates = [CrewMate() for _ in range(m)]
        crewmate_id = 0
        for crewmate in self.crewmates:
            crewmate.id = crewmate_id
            crewmate_id += 1


        self.crewmate_heap = Heap(self.crewmate_cmp, self.crewmates)
        self.all_treasures = []

    def add_treasure(self, treasure):

        min_crewmate = self.crewmate_heap.extract()
        min_crewmate.add_treasure(treasure)
        self.crewmate_heap.insert(min_crewmate)
        self.all_treasures.append(treasure)

    def get_completion_time(self):

        for crewmate in self.crewmates:
            crewmate_treasures = crewmate.assigned_treasures
            t = 0
            index = 0
            available_treasures = []

            while index < len(crewmate_treasures) or available_treasures:

                while index < len(crewmate_treasures) and crewmate_treasures[index].arrival_time <= t:

                    treasure = crewmate_treasures[index]
                    treasure.remaining_size = treasure.size
                    available_treasures.append(treasure)
                    index += 1

                if available_treasures:

                    best_value, selected = None, None
                    for treasure in available_treasures:
                        wait_time = t - treasure.arrival_time
                        remaining_size = treasure.remaining_size
                        value = (wait_time - remaining_size, -treasure.id)  

                        if best_value is None or value > best_value:
                            best_value = value
                            selected = treasure

                    next_arrival = float('inf')
                    if index < len(crewmate_treasures):
                        next_arrival = crewmate_treasures[index].arrival_time - t

                    processing_time = min(next_arrival, selected.remaining_size)
                    selected.remaining_size -= processing_time
                    t += processing_time

                    if selected.remaining_size == 0:
                        selected.completion_time = t
                        available_treasures.remove(selected)
                else:

                    if index < len(crewmate_treasures):
                        t = crewmate_treasures[index].arrival_time

        heap_sorter = HeapSort(lambda a, b: a.id < b.id)  
        self.all_treasures = heap_sorter.heap_sort(self.all_treasures) 

        return self.all_treasures

    def crewmate_cmp(self, a, b):

        if a.get_load() < b.get_load():
            return True
        elif a.get_load() == b.get_load():
            return a.id < b.id
        return False

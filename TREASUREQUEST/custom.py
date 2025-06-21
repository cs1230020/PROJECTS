from heap import Heap
class HeapSort:
    def __init__(self, comparison_function):
       
        self.comparison_function = comparison_function

    def heap_sort(self, array):
        
        heap = Heap(self.comparison_function, array)  # Build the heap from the array
        sorted_array = []

       
        while not heap.isempty():
            sorted_array.append(heap.extract())

        return sorted_array


class Treasure:

    def __init__(self, id, size, arrival_time):

        self.id = id
        self.size = size
        self.arrival_time = arrival_time
        self.completion_time = None
        self.processed_time = 0
        self.remaining_size = size

    def process(self, t):

        self.processed_time += t
        self.remaining_size = max(0, self.size - self.processed_time)
        if self.remaining_size == 0:
            self.completion_time = self.processed_time
            return True
        return False

    def set_completion_time(self, comp):

        self.completion_time = comp

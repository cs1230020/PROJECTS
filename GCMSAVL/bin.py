class Bin:
    def __init__(self, bin_id, capacity):
        self.bin_id = bin_id
        self.capacity = capacity
        self.objects = []  # List of objects currently in the bin

    def add_object(self, obj):
        # Add object only if it fits in the remaining capacity
        if self.capacity >= obj.size:
            self.objects.append(obj.object_id)
            self.capacity -= obj.size
            return True
        return False

    def remove_object(self, object_id, object_size):
        # Remove object by its ID and return capacity
        if object_id in self.objects:
            self.objects.remove(object_id)
            self.capacity += object_size
            return True
        return False


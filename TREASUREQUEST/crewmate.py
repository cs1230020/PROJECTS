class CrewMate:
    
    def __init__(self):
        
        self.id = None
        self.assigned_treasures = []
        self.load = 0

    def add_treasure(self, treasure):
        
        self.assigned_treasures.append(treasure)
        self.load += treasure.size

    def get_load(self):
       
        return self.load
    def __lt__(self,other):
        return self.load<other.load

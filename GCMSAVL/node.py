class Node:
    def __init__(self, value,parent=None):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1
        self.parent=parent

class Heap:

    class Item:
        def __init__(self,k,v):
            self.key=k
            self.value=v
        def __lt__(self,other):
            return self.key<other.key

    def __init__(self, comparison_function, init_array):

        self.comp=comparison_function
        self.data=init_array[:]
        self.build_heap()
        
        pass
    def build_heap(self):

        n = len(self.data)
        
        for i in range((n // 2) - 1, -1, -1):
            self.downheap(i)
    def parent(self,j):
        return (j-1)//2
    def left(self,j):
        return (2*j+1)
    def right(self,j):
        return 2*j+2
    def has_left(self,j):
        return self.left(j)<len(self.data)
    def has_right(self,j):
        return self.right(j)<len(self.data)
    def swap(self,i,j):
        self.data[i],self.data[j]=self.data[j],self.data[i]
    def upheap(self,j):
        parent = self.parent(j)
        if j > 0 and self.comp(self.data[j], self.data[parent]):
            self.swap(j, parent)
            self.upheap(parent)
    def downheap(self,j):
        if self.has_left(j):
            left = self.left(j)
            small_child = left
            if self.has_right(j):
                right = self.right(j)
                if self.comp(self.data[right], self.data[left]):
                    small_child = right
            if self.comp(self.data[small_child], self.data[j]):
                self.swap(j, small_child)
                self.downheap(small_child)

    def __len__(self):
        return len(self.data)
    def isempty(self):
        return len(self.data)==0
    def insert(self, value):

        self.data.append(value)
        self.upheap(len(self.data) - 1)
        # Write your code here
        pass

    def extract(self):

        if self.isempty():
            raise ValueError("Heap is empty")
        self.swap(0, len(self.data) - 1)  # Swap root with the last element
        item = self.data.pop()  # Remove the last element (which was the root)
        if not self.isempty():
            self.downheap(0)  # Restore heap property
        return item

    def top(self):

        if self.isempty():
            raise ValueError("Heap is empty")
        return self.data[0]
        # Write your code here
        pass

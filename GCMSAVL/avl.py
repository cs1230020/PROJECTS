from node import Node
def comp_bin_by_capacity(bin_1, bin_2):
    if bin_1.capacity < bin_2.capacity:
        return -1
    elif bin_1.capacity > bin_2.capacity:
        return 1
    else:
        return comp_bin(bin_1, bin_2)
def comp_bin(bin_1, bin_2):
    if bin_1.bin_id < bin_2.bin_id:
        return -1
    elif bin_1.bin_id > bin_2.bin_id:
        return 1
    else:
        return 0

def comp_object(obj_1, obj_2):
    if obj_1[0] < obj_2[0]:
        return -1
    elif obj_1[0] > obj_2[0]:
        return 1
    else:
        return 0
class AVLTree:
    def __init__(self, compare_function):
        self.root = None
        self.size = 0
        self.comparator = compare_function

    def insert_value(self, value):
        self.root = self.insert(self.root, value, None)

    def insert(self, root, value, parent):
        if not root:
            return Node(value, parent)

        comparison = self.comparator(value, root.value)
        if comparison < 0:
            root.left = self.insert(root.left, value, root)
        elif comparison > 0:
            root.right = self.insert(root.right, value, root)
        else:
            return root

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and self.comparator(value, root.left.value) < 0:
            return self.right_rotate(root)

        if balance < -1 and self.comparator(value, root.right.value) > 0:
            return self.left_rotate(root)

        if balance > 1 and self.comparator(value, root.left.value) > 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        if balance < -1 and self.comparator(value, root.right.value) < 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        
        # Update parent references
        y.parent = z.parent
        z.parent = y
        if T2:
            T2.parent = z

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        
        # Update parent references
        y.parent = z.parent
        z.parent = y
        if T3:
            T3.parent = z

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def search(self, root, value):
        if root is None or self.comparator(value, root.value) == 0:
            return root
        if self.comparator(value, root.value) < 0:
            return self.search(root.left, value)
        return self.search(root.right, value)

    def delete_value(self, value):
        self.root = self.delete(self.root, value)

    def delete(self, root, value):
        if not root:
            return root

        comparison = self.comparator(value, root.value)
        if comparison < 0:
            root.left = self.delete(root.left, value)
        elif comparison > 0:
            root.right = self.delete(root.right, value)
        else:
            if not root.left:
                return root.right
            elif not root.right:
                return root.left

            temp = self.get_min_value_node(root.right)
            root.value = temp.value
            root.right = self.delete(root.right, temp.value)

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)

        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)

        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def get_min_value_node(self, root):
        if root is None or root.left is None:
            return root
        return self.get_min_value_node(root.left)
    def get_max_value_node(self, root):
        """Get the node with the maximum value in the AVL tree."""
        if root is None or root.right is None:
            return root
        return self.get_max_value_node(root.right)

    def get_next(self, value):
        """Get the in-order successor of the given value."""
        node = self.search(self.root, value)
        if node is None:
            return None
        # If the node has a right child, return the min value of the right subtree
        if node.right:
            return self.get_min_value_node(node.right)
        # Otherwise, go up the tree until you find a parent that is larger
        parent = node.parent
        while parent and self.comparator(node.value, parent.value) > 0:
            parent = parent.parent
        return parent

    def get_previous(self, value):
        """Get the in-order predecessor of the given value."""
        node = self.search(self.root, value)
        if node is None:
            return None
        # If the node has a left child, return the max value of the left subtree
        if node.left:
            return self.get_max_value_node(node.left)
        # Otherwise, go up the tree until you find a parent that is smaller
        parent = node.parent
        while parent and self.comparator(node.value, parent.value) < 0:
            parent = parent.parent
        return parent
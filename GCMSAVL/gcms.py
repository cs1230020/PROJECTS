from avl import AVLTree
from bin import Bin
from object import Object, Color
from exceptions import NoBinFoundException
from avl import comp_bin,comp_object
class GCMS:
    def __init__(self):
        self.bins_avl = AVLTree(compare_function=comp_bin)
        self.objects_avl = AVLTree(compare_function=comp_object)

    def add_bin(self, bin_id, capacity):

        new_bin = Bin(bin_id, capacity)
        self.bins_avl.insert_value(new_bin)

    def add_object(self, object_id, size, color):
        obj = Object(object_id, size, color)


        if color == Color.BLUE:
            chosen_bin = self._compact_fit_least_id(obj)
        elif color == Color.YELLOW:
            chosen_bin = self._compact_fit_greatest_id(obj)
        elif color == Color.RED:
            chosen_bin = self._largest_fit_least_id(obj)
        elif color == Color.GREEN:
            chosen_bin = self._largest_fit_greatest_id(obj)
        else:
            raise NoBinFoundException()

        if chosen_bin:
            if chosen_bin.add_object(obj):
                self.objects_avl.insert_value((object_id, chosen_bin, obj))  
                self.bins_avl.delete_value(chosen_bin)
                self.bins_avl.insert_value(chosen_bin)

            else:
                raise NoBinFoundException()
        else:
            raise NoBinFoundException()

    def delete_object(self, object_id):
        object_entry = self.objects_avl.search(self.objects_avl.root, (object_id, None, None)) 

        if object_entry:
            bin, obj = object_entry.value[1], object_entry.value[2]
            self.bins_avl.delete_value(bin)
            bin.remove_object(object_id, obj.size)
            self.bins_avl.insert_value(bin)

            self.objects_avl.delete_value((object_id, None, None))

    def object_info(self, object_id):
        object_entry = self.objects_avl.search(self.objects_avl.root, (object_id, None, None))
        if object_entry:
            return object_entry.value[1].bin_id
        return None
    def bin_info(self, bin_id):

        bin_node = self.bins_avl.search(self.bins_avl.root, Bin(bin_id, 0))
        if bin_node:
            return (bin_node.value.capacity, bin_node.value.objects)
        return None


    def _compact_fit_least_id(self, obj):

        return self._find_compact_fit(self.bins_avl.root, obj.size, least_id=True)

    def _compact_fit_greatest_id(self, obj):

        return self._find_compact_fit(self.bins_avl.root, obj.size, least_id=False)

    def _largest_fit_least_id(self, obj):

        return self._find_largest_fit(self.bins_avl.root, obj.size, least_id=True)

    def _largest_fit_greatest_id(self, obj):

        return self._find_largest_fit(self.bins_avl.root, obj.size, least_id=False)



    def _find_compact_fit(self, node, size, least_id=True):

        if not node:
            return None


        best_fit = None


        left_fit = self._find_compact_fit(node.left, size, least_id)
        if left_fit and left_fit.capacity >= size:
            best_fit = left_fit


        if node.value.capacity >= size:
            if not best_fit or node.value.capacity < best_fit.capacity or \
               (node.value.capacity == best_fit.capacity and
                ((least_id and node.value.bin_id < best_fit.bin_id) or (not least_id and node.value.bin_id > best_fit.bin_id))):
                best_fit = node.value


        right_fit = self._find_compact_fit(node.right, size, least_id)
        if right_fit and right_fit.capacity >= size:
            if not best_fit or right_fit.capacity < best_fit.capacity or \
               (right_fit.capacity == best_fit.capacity and
                ((least_id and right_fit.bin_id < best_fit.bin_id) or (not least_id and right_fit.bin_id > best_fit.bin_id))):
                best_fit = right_fit

        return best_fit

    def _find_largest_fit(self, node, size, least_id=True):

        if not node:
            return None


        best_fit = None


        left_fit = self._find_largest_fit(node.left, size, least_id)
        if left_fit and left_fit.capacity >= size:
            best_fit = left_fit


        if node.value.capacity >= size:
            if not best_fit or node.value.capacity > best_fit.capacity or \
               (node.value.capacity == best_fit.capacity and
                ((least_id and node.value.bin_id < best_fit.bin_id) or (not least_id and node.value.bin_id > best_fit.bin_id))):
                best_fit = node.value


        right_fit = self._find_largest_fit(node.right, size, least_id)
        if right_fit and right_fit.capacity >= size:
            if not best_fit or right_fit.capacity > best_fit.capacity or \
               (right_fit.capacity == best_fit.capacity and
                ((least_id and right_fit.bin_id < best_fit.bin_id) or (not least_id and right_fit.bin_id > best_fit.bin_id))):
                best_fit = right_fit

        return best_fit
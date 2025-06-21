from dynamic_hash_table import DynamicHashSet

class DigitalLibrary:
    def __init__(self):
        raise NotImplementedError
    def distinct_words(self, book_title):
        raise NotImplementedError
    
    def count_distinct_words(self, book_title):
        raise NotImplementedError
    
    def search_keyword(self, keyword):
        raise NotImplementedError
    
    def print_books(self):
        raise NotImplementedError




class MuskLibrary(DigitalLibrary):
    def __init__(self, book_titles, texts):
        
        
        self.books_data = []
        self.sorted_titles = book_titles[:]
        
        for idx in range(len(book_titles)):
            title = book_titles[idx]
            content = texts[idx]
            unique_content = self._extract_unique_words(content)
            self._sort_unique_words(unique_content, 0, len(unique_content) - 1)
            self.books_data.append((title, unique_content))
        
        self._sort_titles()
        self.indexed_books = [None] * len(self.sorted_titles)
        
        for book in self.books_data:
            title_index = self._binary_search(self.sorted_titles, book[0])
            self.indexed_books[title_index] = book[1]

    def _binary_search(self, array, target):
        start, end = 0, len(array) - 1
        while start <= end:
            midpoint = (start + end) // 2
            if array[midpoint] == target:
                return midpoint
            elif array[midpoint] < target:
                start = midpoint + 1
            else:
                end = midpoint - 1
        return -1

    def _char_to_value(self, character):
        if character is None:
            return float('inf')
        if 'a' <= character <= 'z':
            return ord(character) - ord('a') + 26
        elif 'A' <= character <= 'Z':
            return ord(character) - ord('A')
        
    def _merge(self, array, left, middle, right):
        left_size = middle - left + 1
        right_size = right - middle
        left_array = [0] * left_size
        right_array = [0] * right_size
        
        for i in range(left_size):
            left_array[i] = array[left + i]
        
        for j in range(right_size):
            right_array[j] = array[middle + 1 + j]
        
        i = j = 0
        for k in range(left, right + 1):
            if i < left_size and (j >= right_size or left_array[i] <= right_array[j]):
                array[k] = left_array[i]
                i += 1
            else:
                array[k] = right_array[j]
                j += 1

    def _sort_unique_words(self, array, left, right):
        if left < right:
            mid = (left + right) // 2
            self._sort_unique_words(array, left, mid)
            self._sort_unique_words(array, mid + 1, right)
            self._merge(array, left, mid, right)
            
    def _sort_titles(self):
        self._sort_unique_words(self.sorted_titles, 0, len(self.sorted_titles) - 1)

    def _extract_unique_words(self, content):
        unique_list = []
        for word in content:
            if word not in unique_list:
                unique_list.append(word)
        return unique_list

    def distinct_words(self, book_title):
        index = self._binary_search(self.sorted_titles, book_title)
        return self.indexed_books[index] if index != -1 else []

    def count_distinct_words(self, book_title):
        distinct_words = self.distinct_words(book_title)
        return len(distinct_words)

    def search_keyword(self, keyword):
        result_titles = []
        for idx in range(len(self.indexed_books)):
            if self._binary_search(self.indexed_books[idx], keyword) != -1:
                result_titles.append(self.sorted_titles[idx])
        return result_titles

    def print_books(self):
        for idx in range(len(self.sorted_titles)):
            words_list = ' | '.join(self.indexed_books[idx]) if self.indexed_books[idx] else '<EMPTY>'
            print(f"{self.sorted_titles[idx]}: {words_list}")

class JGBLibrary(DigitalLibrary):
    def __init__(self, name, params):
        
        self.strategy = name
        self.params = params
        self.books = []
        
        if self.strategy == "Jobs":
            self.hash_type = "Chain"
        elif self.strategy == "Gates":
            self.hash_type = "Linear"
        elif self.strategy == "Bezos":
            self.hash_type = "Double"

    def add_book(self, book_title, text):
        
        if self.hash_type == "Double":
            z1, z2, c2, table_size_initial = self.params
            book_hash_set = DynamicHashSet(self.hash_type, (z1, z2, c2, table_size_initial))
        else:
            z, table_size_initial = self.params
            book_hash_set = DynamicHashSet(self.hash_type, (z, table_size_initial))
        
        for word in text:
            
            if not book_hash_set.find(word):
                book_hash_set.insert(word)
                
        self.books.append((book_title, book_hash_set))

    def distinct_words(self, book_title):
        
        for title, book_hash_set in self.books:
            if title == book_title:
                return book_hash_set.to_list()
        return []

    def count_distinct_words(self, book_title):
        
        for title, book_hash_set in self.books:
            if title == book_title:
                return book_hash_set.num_elements
        return 0

    def search_keyword(self, keyword):
        
        found_books = []
        for title, book_hash_set in self.books:
            if book_hash_set.find(keyword):
                found_books.append(title)
        return sorted(found_books)

    def print_books(self):
        
        sorted_titles = sorted([book[0] for book in self.books])

        for title in sorted_titles:
            for t, book_hash_set in self.books:
                if t == title:
                    if self.hash_type == "Chain":  
                        words = []
                        for slot in book_hash_set.table:
                            if slot:
                                
                                words.append(' ; '.join(str(word) for word in slot))
                            else:
                                words.append("<EMPTY>")
                        formatted_words = ' | '.join(words)

                    elif self.hash_type in ("Linear", "Double"):  
                        words = []
                        for word in book_hash_set.table:
                            if word is not None:
                                words.append(str(word))
                            else:
                                words.append("<EMPTY>")
                        formatted_words = ' | '.join(words)

                    print(f"{title}: {formatted_words}")

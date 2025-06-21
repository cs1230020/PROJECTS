from flight import Flight

class MinHeap:
    
    def __init__(self):
        self.heap = []
    
    def _left_child(self, index):
        return 2 * index + 1
    
    def _right_child(self, index):
        return 2 * index + 2
    
    def _parent(self, index):
        return (index - 1) // 2
    
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _sift_up(self, index):
        while index > 0 and self.heap[self._parent(index)] > self.heap[index]:
            parent_idx = self._parent(index)
            self._swap(index, parent_idx)
            index = parent_idx
    
    def _sift_down(self, index):
        min_index = index
        size = len(self.heap)
        
        while True:
            left = self._left_child(index)
            right = self._right_child(index)
            
            if left < size and self.heap[left] < self.heap[min_index]:
                min_index = left
            
            if right < size and self.heap[right] < self.heap[min_index]:
                min_index = right
            
            if min_index == index:
                break
                
            self._swap(index, min_index)
            index = min_index
    
    def push(self, item):
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        min_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        
        return min_item
    
    def __bool__(self):
        return bool(self.heap)

class FlightGraph:
    def __init__(self, n):
        self.adj_list = [[] for _ in range(n)]
        self.n = n
        
    def add_flight(self, flight: Flight) -> None:
        self.adj_list[flight.start_city].append(flight)
        
    def get_flights_from(self, city: int):
        return self.adj_list[city]

class Planner:
    def __init__(self, flights):
        n = max(max(flight.start_city, flight.end_city) for flight in flights) + 1
        
        
        city_flight_count = [0] * n
        for flight in flights:
            city_flight_count[flight.start_city] += 1
            city_flight_count[flight.end_city] += 1
            
        
        self.graph = FlightGraph(n)
        for flight in flights:
            self.graph.add_flight(flight)
            
        
        for city_flights in self.graph.adj_list:
            city_flights.sort(key=lambda x: x.departure_time)

    def _is_valid_connection(self, current_arrival, next_departure):
        
        return next_departure >= current_arrival + 20

    def _is_within_timeframe(self, flight, t1, t2):
        
        return t1 <= flight.departure_time and flight.arrival_time <= t2

    def least_flights_earliest_route(self, start_city, end_city, t1, t2):
        n = self.graph.n
        visited = [(float('inf'), float('inf')) for _ in range(n)]  
        pq = MinHeap()
        pq.push((0, t1, start_city, []))  
        min_flights = float('inf')
        best_route = []

        while pq:
            num_flights, current_arrival, current_city, route = pq.pop()
            
            if current_city == end_city:
                if num_flights <= min_flights:
                    min_flights = num_flights
                    if not best_route or current_arrival < visited[end_city][1]:
                        best_route = route
                        visited[end_city] = (num_flights, current_arrival)
                continue
                
            if current_arrival >= visited[current_city][1] and num_flights >= visited[current_city][0]:
                continue
                
            visited[current_city] = (num_flights, current_arrival)
            
            for next_flight in self.graph.get_flights_from(current_city):
                if not self._is_within_timeframe(next_flight, t1, t2):
                    continue
                    
                if route and not self._is_valid_connection(route[-1].arrival_time, next_flight.departure_time):
                    continue
                    
                if next_flight.departure_time >= current_arrival:
                    if num_flights + 1 <= min_flights:
                        pq.push((num_flights + 1,next_flight.arrival_time,next_flight.end_city,route + [next_flight]))
        
        return best_route

    def cheapest_route(self, start_city, end_city, t1, t2):
        n = self.graph.n
        min_cost = [float('inf')] * n
        min_cost[start_city] = 0
        pq = MinHeap()
        pq.push((0, start_city, t1, []))  
        best_route = None
        best_cost = float('inf')

        while pq:
            total_fare, current_city, current_arrival, route = pq.pop()
            
            if current_city == end_city:
                if total_fare < best_cost:
                    best_cost = total_fare
                    best_route = route
                continue
                
            if total_fare >= best_cost:
                continue
            
            for next_flight in self.graph.get_flights_from(current_city):
                if not self._is_within_timeframe(next_flight, t1, t2):
                    continue
                    
                if route and not self._is_valid_connection(route[-1].arrival_time, next_flight.departure_time):
                    continue
                    
                if next_flight.departure_time < current_arrival:
                    continue
                
                new_fare = total_fare + next_flight.fare
                
                if new_fare < min_cost[next_flight.end_city]:
                    min_cost[next_flight.end_city] = new_fare
                    pq.push((new_fare,next_flight.end_city,next_flight.arrival_time,route + [next_flight]))
        
        return best_route if best_route is not None else []

    def least_flights_cheapest_route(self, start_city, end_city, t1, t2):
        
        if (start_city >= self.graph.n or end_city >= self.graph.n or start_city < 0 or end_city < 0 or start_city == end_city):
            return []

        processed = [False] * self.graph.n
        cost_to_city = [float('inf')] * self.graph.n
        flights_to_city = [float('inf')] * self.graph.n
        cost_to_city[start_city] = 0
        flights_to_city[start_city] = 0

        pq = Heap2(lambda a, b: self._compare_flights(a, b))
        pq.insert((0, 0, None, []))

        final_path = []
        optimal_flights = float('inf')
        optimal_cost = float('inf')

        while not pq.is_empty():
            flights_taken, path_cost, current_flight, path = pq.extract()

            if current_flight:
                current_pos = current_flight.end_city
            else:
                current_pos = start_city

            if current_pos == end_city:
                if flights_taken < optimal_flights or (flights_taken == optimal_flights and path_cost < optimal_cost):
                    optimal_flights = flights_taken
                    optimal_cost = path_cost
                    final_path = path
                continue

            if flights_taken >= optimal_flights:
                continue

            if (processed[current_pos] and
                flights_to_city[current_pos] < flights_taken and
                cost_to_city[current_pos] <= path_cost):
                continue

            processed[current_pos] = True
            flights_to_city[current_pos] = flights_taken
            cost_to_city[current_pos] = path_cost

            for next_flight in self.graph.get_flights_from(current_pos):
                if not self._is_within_timeframe(next_flight, t1, t2):
                    continue

                if path and not self._is_valid_connection(path[-1].arrival_time, next_flight.departure_time):
                    continue

                updated_cost = path_cost + next_flight.fare
                updated_flights = flights_taken + 1

                if (updated_flights < flights_to_city[next_flight.end_city] or
                    (updated_flights == flights_to_city[next_flight.end_city] and
                    updated_cost < cost_to_city[next_flight.end_city])):
                    pq.insert((
                        updated_flights,
                        updated_cost,
                        next_flight,
                        path + [next_flight]
                    ))

        return final_path

    def _compare_flights(self, a, b):
        if a[0] != b[0]:
            return a[0] < b[0]
        if a[1] != b[1]:
            return a[1] < b[1]
        return a[2].departure_time < b[2].departure_time

class Heap2:
    def __init__(self, compare_function):
        self.heap = []
        self.compare = compare_function
    
    def _parent(self, i):
        return (i - 1) // 2
    
    def _left_child(self, i):
        return 2 * i + 1
    
    def _right_child(self, i):
        return 2 * i + 2
    
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _sift_up(self, index):
        parent = self._parent(index)
        if index > 0 and self.compare(self.heap[index], self.heap[parent]):
            self._swap(index, parent)
            self._sift_up(parent)
    
    def _sift_down(self, index):
        min_idx = index
        left = self._left_child(index)
        right = self._right_child(index)
        
        if left < len(self.heap) and self.compare(self.heap[left], self.heap[min_idx]):
            min_idx = left
            
        if right < len(self.heap) and self.compare(self.heap[right], self.heap[min_idx]):
            min_idx = right
            
        if min_idx != index:
            self._swap(index, min_idx)
            self._sift_down(min_idx)
    
    def insert(self, item):
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
    
    def extract(self):
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        
        return root
    
    def is_empty(self):
        return len(self.heap) == 0


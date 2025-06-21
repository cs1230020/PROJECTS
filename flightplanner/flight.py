class Flight:
    def __init__(self, flight_no, start_city, departure_time, end_city, arrival_time, fare):
        """ Class for the flights

        Args:
            flight_no (int): Unique ID of each flight
            start_city (int): The city no. where the flight starts
            departure_time (int): Time at which the flight starts
            end_city (int): The city no where the flight ends
            arrival_time (int): Time at which the flight ends
            fare (int): The cost of taking this flight
        """
        self.flight_no = flight_no
        self.start_city = start_city
        self.departure_time = departure_time
        self.end_city = end_city
        self.arrival_time = arrival_time
        self.fare = fare
    def __lt__(self, other):
        # Customize the priority here; for example, prioritize by arrival time
        return self.arrival_time < other.arrival_time

    # You might also want to implement equality if needed
    def __eq__(self, other):
        return (
            self.arrival_time == other.arrival_time and
            self.fare == other.fare
        )
    def compare_flights(self,a, b):
            # a and b are tuples: (num_flights, total_cost, arrival_time, city, route)
            if a[0] != b[0]:  # Compare number of flights
                return a[0] < b[0]
            if a[1] != b[1]:  # Compare total cost
                return a[1] < b[1]
            return a[2] < b[2]  # Compare arrival time
        
        
        
"""
If there are n flights, and m cities:

1. Flight No. will be an integer in {0, 1, ... n-1}
2. Cities will be denoted by an integer in {0, 1, .... m-1}
3. Time is denoted by a non negative integer - we model time as going from t=0 to t=inf
"""
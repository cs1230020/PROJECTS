# Makefile for Part1
CXX=g++
CXXFLAGS=-std=c++17 -O2
SERVER=server
CLIENT=client

.PHONY: all build clean run run-mininet

all: build

build:
	$(CXX) $(CXXFLAGS) -o $(SERVER) server.cpp
	$(CXX) $(CXXFLAGS) -o $(CLIENT) client.cpp

clean:
	rm -f $(SERVER) $(CLIENT) *.log *.err results.csv

run: build
	./$(SERVER) --config config.json

# Run experiments in Mininet (requires sudo)
run-mininet: build
	sudo python3 run_experiments.py

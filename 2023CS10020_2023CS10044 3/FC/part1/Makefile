# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11 -Wall -O2

# macOS ARM (M1/M2) specific paths for jsoncpp
CXXFLAGS += -I/opt/homebrew/Cellar/jsoncpp/1.9.6/include
LDFLAGS = -L/opt/homebrew/lib
LIBS = -ljsoncpp -pthread

# Python interpreter
PYTHON = python3

# Targets
.PHONY: all build run plot clean test help

# Default target
all: build

# Build both server and client
build: server client
	@echo "Build complete!"

# Compile server
server: server.cpp
	@echo "Compiling server..."
	$(CXX) $(CXXFLAGS) -o server server.cpp $(LDFLAGS) $(LIBS)

# Compile client
client: client.cpp
	@echo "Compiling client..."
	$(CXX) $(CXXFLAGS) -o client client.cpp $(LDFLAGS) $(LIBS)

# Run a single iteration
run: build
	@echo "Starting server..."
	@./server > server.log 2>&1 &
	@SERVER_PID=$$!; \
	sleep 1; \
	echo "Running client..."; \
	./client; \
	echo "Stopping server..."; \
	kill $$SERVER_PID 2>/dev/null || true

# Run experiments and generate plots
plot: build
	@echo "Running experiments..."
	$(PYTHON) runner.py
	@echo "Generating plots..."
	$(PYTHON) plotter.py

# Clean build artifacts and results
clean:
	@echo "Cleaning..."
	rm -f server client
	rm -f *.o *.csv *.png *.pdf *.log
	@echo "Clean complete!"

# Test basic functionality
test: build
	@echo "Running basic tests..."
	@./server > test_server.log 2>&1 &
	@SERVER_PID=$$!; \
	sleep 1; \
	echo "Testing client..."; \
	./client > test_output.txt 2>&1 || true; \
	kill $$SERVER_PID 2>/dev/null || true; \
	if [ -s test_output.txt ]; then \
		echo "✓ Test passed - output received"; \
		head -5 test_output.txt; \
	else \
		echo "✗ Test failed - no output"; \
	fi; \
	rm -f test_output.txt test_server.log

help:
	@echo "Available targets:"
	@echo "  make build    - Compile server and client"
	@echo "  make run      - Run a single client-server iteration"
	@echo "  make plot     - Run experiments and generate plots"
	@echo "  make test     - Test basic functionality"
	@echo "  make clean    - Remove compiled files and results"
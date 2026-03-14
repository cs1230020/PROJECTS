# Makefile for Part 3 - FCFS Scheduling with Greedy Client

.PHONY: all run-fcfs plot clean test-server test-client setup help

# Default target
all: help

# Help message
help:
	@echo "Available targets:"
	@echo "  make setup       - Check and create required files"
	@echo "  make run-fcfs    - Run one FCFS experiment with current config"
	@echo "  make plot        - Run full analysis and generate plots"
	@echo "  make test-server - Test server independently"
	@echo "  make test-client - Test client with c=5"
	@echo "  make clean       - Clean up generated files and kill processes"
	@echo ""
	@echo "Workflow:"
	@echo "  1. make setup    (first time only)"
	@echo "  2. make run-fcfs (test single run)"
	@echo "  3. make plot     (full analysis)"

# Setup environment
setup:
	@echo "Setting up Part 3 environment..."
	@if [ ! -f "config.json" ]; then \
		echo "Creating default config.json..."; \
		echo '{' > config.json; \
		echo '  "server_ip": "0.0.0.0",' >> config.json; \
		echo '  "server_port": 8888,' >> config.json; \
		echo '  "k": 5,' >> config.json; \
		echo '  "p": 0,' >> config.json; \
		echo '  "filename": "words.txt",' >> config.json; \
		echo '  "num_repetitions": 5,' >> config.json; \
		echo '  "num_clients": 10,' >> config.json; \
		echo '  "c": 1' >> config.json; \
		echo '}' >> config.json; \
		echo "Created config.json"; \
	else \
		echo "config.json already exists"; \
	fi
	@if [ ! -f "words.txt" ]; then \
		echo "Creating sample words.txt..."; \
		echo "apple,banana,cherry,date,elderberry,fig,grape,honeydew,kiwi,lemon,mango,nectarine,orange,papaya,quince,raspberry,strawberry,tangerine,ugli,vanilla,watermelon,xigua,yuzu,zucchini,apricot,blueberry,coconut,dragonfruit,eggplant,feijoa,guava,huckleberry,imbe,jackfruit,kumquat,lime,mulberry,nutmeg,olive,peach,quinoa,rhubarb,spinach,tomato,ube,violet,wheat,ximenia,yam,zest" > words.txt; \
		echo "Created words.txt with sample data"; \
	else \
		echo "words.txt already exists"; \
	fi
	@echo "Checking Python installation..."
	@python3 --version || (echo "Error: Python 3 not found" && exit 1)
	@echo "Checking required Python modules..."
	@python3 -c "import socket, threading, json, time, numpy, matplotlib" 2>/dev/null || \
		(echo "Installing required modules..." && pip3 install numpy matplotlib)
	@echo "Setup complete!"

# Run single FCFS experiment with current config
run-fcfs:
	@echo "=== Running FCFS experiment ==="
	@echo "Cleaning up any existing servers..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Starting FCFS server..."
	@python3 server.py > server.log 2>&1 &
	@echo "Waiting for server to start..."
	@sleep 2
	@echo "Running clients..."
	@python3 client.py || (echo "Client execution failed"; pkill -f "python.*server.py" 2>/dev/null; exit 1)
	@echo "Stopping server..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@echo "=== Experiment complete ==="

# Run full analysis with varying c values
plot:
	@echo "=== Starting full analysis for Part 3 ==="
	@echo "This will run experiments for c=1 to c=10"
	@echo "Each value will be tested 5 times"
	@echo "Total experiments: 50"
	@echo ""
	@read -p "Continue? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "Cleaning up before starting..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@rm -f results_c*.json 2>/dev/null || true
	@echo "Running analysis..."
	@python3 analysis.py || (echo "Analysis failed"; exit 1)
	@echo ""
	@echo "=== Analysis complete ==="
	@echo "Generated files:"
	@ls -la p3_plot.png 2>/dev/null && echo "  ✓ p3_plot.png" || echo "  ✗ p3_plot.png (not found)"
	@ls -la p3_analysis.png 2>/dev/null && echo "  ✓ p3_analysis.png" || echo "  ✗ p3_analysis.png (not found)"
	@ls -la part3_raw_data_*.json 2>/dev/null | head -1 && echo "  ✓ Raw data file" || echo "  ✗ No raw data file"

# Test server independently
test-server:
	@echo "=== Testing server ==="
	@pkill -f "python.*server.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Starting server in foreground (press Ctrl+C to stop)..."
	@python3 server.py

# Test client with specific c value
test-client:
	@echo "=== Testing client with c=5 ==="
	@pkill -f "python.*server.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Updating config to use c=5..."
	@python3 -c "import json; config=json.load(open('config.json')); config['c']=5; json.dump(config, open('config.json','w'), indent=2)"
	@echo "Starting server in background..."
	@python3 server.py > server_test.log 2>&1 &
	@sleep 2
	@echo "Running client test..."
	@python3 client.py
	@echo "Stopping server..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@echo "=== Test complete ==="

# Clean up generated files and processes
clean:
	@echo "Cleaning up..."
	@echo "Killing any running Python processes..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@pkill -f "python.*client.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Removing generated files..."
	@rm -f p3_plot.png p3_analysis.png 2>/dev/null || true
	@rm -f results_c*.json 2>/dev/null || true
	@rm -f part3_raw_data_*.json 2>/dev/null || true
	@rm -f server.log server_test.log 2>/dev/null || true
	@rm -f *.pyc __pycache__ 2>/dev/null || true
	@echo "Clean complete!"

# For Mininet environment
mininet-run:
	@echo "=== Running on Mininet ==="
	@echo "Note: Make sure you're running this inside Mininet"
	@echo "Updating config for Mininet environment..."
	@python3 -c "import json; config=json.load(open('config.json')); config['server_ip']='10.0.0.1'; json.dump(config, open('config.json','w'), indent=2)"
	@$(MAKE) run-fcfs

mininet-plot:
	@echo "=== Running analysis on Mininet ==="
	@echo "Note: Make sure you're running this inside Mininet"
	@echo "Updating config for Mininet environment..."
	@python3 -c "import json; config=json.load(open('config.json')); config['server_ip']='10.0.0.1'; json.dump(config, open('config.json','w'), indent=2)"
	@$(MAKE) plot

# Debug targets
debug-config:
	@echo "Current configuration:"
	@cat config.json | python3 -m json.tool

debug-words:
	@echo "Words file preview (first 100 chars):"
	@head -c 100 words.txt
	@echo ""
	@echo "Word count:"
	@python3 -c "print(len(open('words.txt').read().strip().split(','))), 'words'"

# Dependency check
check-deps:
	@echo "Checking dependencies..."
	@which python3 >/dev/null || (echo "❌ Python 3 not found" && exit 1)
	@echo "✓ Python 3 found"
	@python3 -c "import socket" || (echo "❌ socket module missing" && exit 1)
	@echo "✓ socket module"
	@python3 -c "import threading" || (echo "❌ threading module missing" && exit 1)
	@echo "✓ threading module"
	@python3 -c "import json" || (echo "❌ json module missing" && exit 1)
	@echo "✓ json module"
	@python3 -c "import numpy" 2>/dev/null || (echo "❌ numpy missing - run: pip3 install numpy" && exit 1)
	@echo "✓ numpy"
	@python3 -c "import matplotlib" 2>/dev/null || (echo "❌ matplotlib missing - run: pip3 install matplotlib" && exit 1)
	@echo "✓ matplotlib"
	@echo "All dependencies satisfied!"
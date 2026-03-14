# Makefile for Part 4 - Round-Robin Scheduling

.PHONY: all run-rr plot clean test-server test-client setup help check-deps

# Default target
all: help

# Help message
help:
	@echo "Part 4: Round-Robin Scheduling"
	@echo "=============================="
	@echo "Available targets:"
	@echo "  make setup       - Check and create required files"
	@echo "  make run-rr      - Run one Round-Robin experiment with current config"
	@echo "  make plot        - Run full analysis and generate plots"
	@echo "  make test-server - Test server independently"
	@echo "  make test-client - Test client with c=5"
	@echo "  make clean       - Clean up generated files and kill processes"
	@echo "  make compare     - Compare Part 3 (FCFS) and Part 4 (Round-Robin) results"
	@echo ""
	@echo "Workflow:"
	@echo "  1. make setup    (first time only)"
	@echo "  2. make run-rr   (test single run)"
	@echo "  3. make plot     (full analysis)"
	@echo "  4. make compare  (optional: compare with Part 3)"

# Setup environment
setup:
	@echo "Setting up Part 4 environment..."
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
		if [ -f "../part3/words.txt" ]; then \
			echo "Copying words.txt from part3..."; \
			cp ../part3/words.txt .; \
		else \
			echo "Creating sample words.txt..."; \
			echo "apple,banana,cherry,date,elderberry,fig,grape,honeydew,kiwi,lemon,mango,nectarine,orange,papaya,quince,raspberry,strawberry,tangerine,ugli,vanilla,watermelon,xigua,yuzu,zucchini,apricot,blueberry,coconut,dragonfruit,eggplant,feijoa,guava,huckleberry,imbe,jackfruit,kumquat,lime,mulberry,nutmeg,olive,peach,quinoa,rhubarb,spinach,tomato,ube,violet,wheat,ximenia,yam,zest" > words.txt; \
		fi; \
		echo "words.txt ready"; \
	else \
		echo "words.txt already exists"; \
	fi
	@echo "Checking Python installation..."
	@python3 --version || (echo "Error: Python 3 not found" && exit 1)
	@echo "Setup complete!"

# Run single Round-Robin experiment with current config
run-rr:
	@echo "=== Running Round-Robin experiment ==="
	@echo "Cleaning up any existing servers..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Starting Round-Robin server..."
	@python3 server.py > server.log 2>&1 &
	@echo "Waiting for server to start..."
	@sleep 2
	@echo "Running clients..."
	@python3 client.py || (echo "Client execution failed"; pkill -f "python.*server.py" 2>/dev/null; exit 1)
	@echo "Stopping server..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@echo "=== Experiment complete ==="
	@echo ""
	@echo "Check if JFI is high (>0.9) - this indicates fair scheduling"

# Run full analysis with varying c values
plot:
	@echo "=== Starting full analysis for Part 4 ==="
	@echo "Round-Robin Scheduling Analysis"
	@echo "This will run experiments for c=1 to c=10"
	@echo "Each value will be tested 5 times"
	@echo "Total experiments: 50"
	@echo ""
	@echo "Expected result: JFI should remain HIGH for all c values"
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
	@ls -la p4_plot.png 2>/dev/null && echo "  ✓ p4_plot.png (main results)" || echo "  ✗ p4_plot.png (not found)"
	@ls -la p4_comparison.png 2>/dev/null && echo "  ✓ p4_comparison.png (FCFS vs RR)" || echo "  ✗ p4_comparison.png (not found)"
	@ls -la part4_raw_data_*.json 2>/dev/null | head -1 && echo "  ✓ Raw data file" || echo "  ✗ No raw data file"

# Test server independently
test-server:
	@echo "=== Testing Round-Robin server ==="
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
	@echo "Starting Round-Robin server in background..."
	@python3 server.py > server_test.log 2>&1 &
	@sleep 2
	@echo "Running client test..."
	@python3 client.py
	@echo "Stopping server..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@echo ""
	@echo "=== Test complete ==="
	@echo "Check if all clients have similar completion times"
	@echo "This indicates Round-Robin fairness"

# Clean up generated files and processes
clean:
	@echo "Cleaning up..."
	@echo "Killing any running Python processes..."
	@pkill -f "python.*server.py" 2>/dev/null || true
	@pkill -f "python.*client.py" 2>/dev/null || true
	@sleep 0.5
	@echo "Removing generated files..."
	@rm -f p4_plot.png p4_comparison.png 2>/dev/null || true
	@rm -f results_c*.json 2>/dev/null || true
	@rm -f part4_raw_data_*.json 2>/dev/null || true
	@rm -f server.log server_test.log 2>/dev/null || true
	@rm -rf __pycache__ 2>/dev/null || true
	@rm -f *.pyc 2>/dev/null || true
	@echo "Clean complete!"

# Compare results with Part 3
compare:
	@echo "=== Comparing Part 3 (FCFS) vs Part 4 (Round-Robin) ==="
	@if [ -f "p4_plot.png" ]; then \
		if [ -f "../part3/p3_plot.png" ]; then \
			echo "Both plots found. You can visually compare:"; \
			echo "  - Part 3 (FCFS): ../part3/p3_plot.png"; \
			echo "  - Part 4 (RR): p4_plot.png"; \
			echo ""; \
			echo "Expected differences:"; \
			echo "  FCFS: JFI drops to ~0.14-0.18 (unfair)"; \
			echo "  RR: JFI stays at ~0.9-1.0 (fair)"; \
		else \
			echo "Part 3 plot not found. Run 'make plot' in part3 directory first."; \
		fi; \
	else \
		echo "Part 4 plot not found. Run 'make plot' first."; \
	fi; \
	@if [ -f "p4_comparison.png" ]; then \
		echo ""; \
		echo "Comparison plot available: p4_comparison.png"; \
	fi

# For Mininet environment
mininet-run:
	@echo "=== Running on Mininet ==="
	@echo "Note: Make sure you're running this inside Mininet"
	@echo "Updating config for Mininet environment..."
	@python3 -c "import json; config=json.load(open('config.json')); config['server_ip']='10.0.0.1'; json.dump(config, open('config.json','w'), indent=2)"
	@$(MAKE) run-rr

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

debug-server-log:
	@echo "Last 20 lines of server log:"
	@tail -20 server.log 2>/dev/null || echo "No server.log file found"

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

# Quick demo showing the difference
demo:
	@echo "=== Quick Demo: Round-Robin Fairness ==="
	@echo "Running with c=10 to show extreme case..."
	@python3 -c "import json; config=json.load(open('config.json')); config['c']=10; json.dump(config, open('config.json','w'), indent=2)"
	@$(MAKE) run-rr
	@echo ""
	@echo "Notice: Even with c=10, all clients have similar completion times"
	@echo "This demonstrates Round-Robin's fairness!"

# Generate summary report
report:
	@echo "=== Part 4 Summary Report ==="
	@echo ""
	@echo "Implementation: Round-Robin Scheduling"
	@echo "Key Feature: Per-client queues with circular processing"
	@echo ""
	@if [ -f "part4_raw_data_*.json" ]; then \
		echo "Latest experimental results:"; \
		python3 -c "import json, glob; \
		files = sorted(glob.glob('part4_raw_data_*.json')); \
		if files: \
			data = json.load(open(files[-1])); \
			print('  c=1:  JFI =', round(data.get('1', {}).get('mean', 0), 3)); \
			print('  c=5:  JFI =', round(data.get('5', {}).get('mean', 0), 3)); \
			print('  c=10: JFI =', round(data.get('10', {}).get('mean', 0), 3))"; \
	else \
		echo "No experimental data found. Run 'make plot' first."; \
	fi
	@echo ""
	@echo "Conclusion: Round-Robin maintains fairness regardless of client behavior"
# Makefile for Part 2: Concurrent Word Counting Clients

.PHONY: all install-deps setup run experiments plot clean debug help

all: setup

# Install Python dependencies
install-deps:
	@echo "Installing Python packages..."
	@pip3 install --user matplotlib numpy scipy

# Verify environment setup
setup:
	@echo "Checking Part 2 environment..."
	@test -f config.json || (echo "config.json missing!" && exit 1)
	@test -f words.txt || (echo "words.txt missing!" && exit 1)
	@python3 -c "import matplotlib, numpy, scipy" 2>/dev/null || (echo "Missing Python deps" && exit 1)
	@echo "Environment OK"

# Run local single server+clients (not Mininet)
run: setup
	@echo "Running Part 2 locally..."
	@python3 server.py & \
	SERVER_PID=$$!; \
	sleep 2; \
	python3 client.py --time-only; \
	kill $$SERVER_PID; wait $$SERVER_PID 2>/dev/null || true

# Run full experiments using Mininet
experiments: setup
	@echo "Running experiments with Mininet..."
	@sudo python3 run_experiments.py

# Generate plots after experiments
plot: setup
	@echo "Generating plot..."
	@python3 plot_results.py
	@test -f p2_plot.png && echo "✓ Plot saved as p2_plot.png" || echo "✗ Plot not generated"

# Clean generated results
clean:
	@echo "Cleaning..."
	@rm -f p2_results.csv p2_plot.png p2_plot.pdf
	@rm -f temp_config.json *.pyc __pycache__/*

debug:
	@echo "Current directory: $$(pwd)"
	@ls -la *.py *.json *.txt 2>/dev/null || true
	@python3 -c "import matplotlib; print('matplotlib ✓')" || echo "matplotlib ✗"
	@python3 -c "import numpy; print('numpy ✓')" || echo "numpy ✗"
	@python3 -c "import scipy; print('scipy ✓')" || echo "scipy ✗"

help:
	@echo "Targets:"
	@echo "  install-deps   - Install Python packages"
	@echo "  setup          - Check environment"
	@echo "  run            - Run server+single client locally"
	@echo "  experiments    - Run Mininet experiments"
	@echo "  plot           - Generate plots"
	@echo "  clean          - Remove generated files"
	@echo "  debug          - Debug environment"

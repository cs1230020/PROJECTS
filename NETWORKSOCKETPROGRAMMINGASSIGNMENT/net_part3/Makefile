PYTHON=python3
SUDO=sudo

# Files
RUNNER=runner.py
PLOT=plot_results.py
CONFIG=config.json

# Default target
all: run plot

# Run experiments
run:
	$(SUDO) $(PYTHON) $(RUNNER) --config $(CONFIG)

# Generate plots
plot:
	$(PYTHON) $(PLOT)

# Clean logs and results
clean:
	rm -f logs/*.log *.png *.csv

.PHONY: all run plot clean

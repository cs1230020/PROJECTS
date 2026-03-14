# Makefile for Part 4: Round-Robin Server Experiments

# Default config file
CONFIG=config.json

# Targets
.PHONY: all run plot clean

all: run plot
	@echo "All done!"

# Run experiments (requires sudo for Mininet)
run:
	sudo python3 run_experiment.py --config $(CONFIG)

# Plot results
plot:
	python3 plot_results.py

# Clean logs and results
clean:
	rm -rf logs results *.png
	@echo "Cleaned logs, results, and plots."

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11 -w    # -w suppresses all warnings

# Directories
SRC_DIR = .
INPUT_DIR = ../inputfiles
BUILD_DIR = build

# Source files
SOURCES = main.cpp Forwarding.cpp NonForwarding.cpp
HEADERS = Forwarding.hpp NonForwarding.hpp ALU.hpp

# Object files
OBJECTS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.o)

# Executable name
EXECUTABLE = processor

# Default target
all: $(BUILD_DIR) $(EXECUTABLE)

# Create build directory
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)    # @ suppresses command echo

# Link the executable
$(EXECUTABLE): $(OBJECTS)
	@$(CXX) $(OBJECTS) -o $(EXECUTABLE)    # @ suppresses command echo

# Compile source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp $(HEADERS)
	@$(CXX) $(CXXFLAGS) -c $< -o $@    # @ suppresses command echo

# Clean build files
clean:
	@rm -rf $(BUILD_DIR) $(EXECUTABLE)    # @ suppresses command echo

# Run tests
test: $(EXECUTABLE)
	@./$(EXECUTABLE) $(INPUT_DIR)/strlen.txt    # @ suppresses command echo

# Phony targets
.PHONY: all clean test

# Dependencies
$(BUILD_DIR)/main.o: main.cpp $(HEADERS)
$(BUILD_DIR)/Forwarding.o: Forwarding.cpp Forwarding.hpp ALU.hpp
$(BUILD_DIR)/NonForwarding.o: NonForwarding.cpp NonForwarding.hpp ALU.hpp
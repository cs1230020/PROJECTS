#include "Forwarding.hpp"
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file>" << std::endl;
        return 1;
    }

    std::string inputFile = argv[1];
    NoForwardProcessor processor(inputFile);

    // Simulate the processor for a specified number of cycles (e.g., 10)
    processor.simulate(25);

    return 0;
}
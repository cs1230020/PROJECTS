// matrix_vector_mult_small.cpp
#include <iostream>
#include <vector>
#include <fstream>
#include "omp.h" // Use the custom header file
#include <cstdlib>
#include <ctime>

// Function to trace memory access
void traceAccess(std::ofstream& traceFile, char op, void* addr) {
    traceFile << op << " 0x" << std::hex << (uintptr_t)addr << std::dec << std::endl;
}

int main() {
    // Create trace files for 4 cores
    std::ofstream traceFiles[4];
    for (int i = 0; i < 4; i++) {
        std::string filename = "matmul_proc" + std::to_string(i) + ".trace";
        traceFiles[i].open(filename);
        if (!traceFiles[i].is_open()) {
            std::cerr << "Error: Could not open trace file: " << filename << std::endl;
            return 1;
        }
    }

    // MUCH SMALLER dimensions - just enough to demonstrate the issue
    const int M = 4;       // Number of rows - one per core
    const int N = 5;       // Just a few iterations
    
    // Allocate memory for matrix A (MxN), and vectors x (N) and y (M)
    std::vector<double> A(M * N, 1.0);  // All 1's for simplicity
    std::vector<double> x(N, 1.0);      // All 1's for simplicity
    
    // Version 1: Without padding (exhibits false sharing)
    std::vector<double> y_falsesharing(M, 0.0);
    
    // Version 2: With padding to avoid false sharing
    struct PaddedDouble {
        double value;
        char padding[56]; // Pad to 64 bytes (assuming 8-byte double)
    };
    
    std::vector<PaddedDouble> y_padded(M);
    for (int i = 0; i < M; i++) {
        y_padded[i].value = 0.0;
    }
    
    // Skip initialization traces to keep files small
    
    // Process each thread's work separately - only a few operations per thread
    for (int tid = 0; tid < 4; tid++) {
        // Each thread only handles one row (i = tid)
        int i = tid;
        
        // Version 1: Demonstrating false sharing (just 3 iterations)
        for (int j = 0; j < 3; j++) {
            // Read the current value
            traceAccess(traceFiles[tid], 'R', &y_falsesharing[i]);
            
            // Update it (simulating matrix-vector multiplication)
            y_falsesharing[i] += 1.0;
            
            // Write back
            traceAccess(traceFiles[tid], 'W', &y_falsesharing[i]);
        }
    }
    
    // Version 2: With padding to avoid false sharing
    for (int tid = 0; tid < 4; tid++) {
        // Each thread only handles one row (i = tid)
        int i = tid;
        
        // First, read initial value
        traceAccess(traceFiles[tid], 'R', &y_padded[i].value);
        
        // Use a local variable (no intermediate traces)
        double local_sum = y_padded[i].value;
        
        // Simulate a few calculations
        for (int j = 0; j < 3; j++) {
            local_sum += 1.0;
        }
        
        // Write back only once
        y_padded[i].value = local_sum;
        traceAccess(traceFiles[tid], 'W', &y_padded[i].value);
    }
    
    // Close trace files
    for (int i = 0; i < 4; i++) {
        traceFiles[i].close();
    }
    
    std::cout << "Small trace files generated successfully!" << std::endl;
    std::cout << "Run your simulator with: ./L1simulate -t matmul -s 6 -E 2 -b 5 -o matmul_results.txt" << std::endl;
    
    return 0;
}
#include <iostream>
#include <string>
#include <cstdlib>
#include <getopt.h>
#include <fstream>
#include <iomanip>
#include "Simulator.h"

unsigned int currentGlobalCycle = 0;

void printHelp() {
    std::cout << "Usage: ./L1simulate [OPTIONS]\n"
              << "Options:\n"
              << "  -t <tracefile>: name of parallel application (e.g. app1) whose 4 traces are to be used\n"
              << "  -s <s>: number of set index bits (number of sets in the cache = S = 2^s)\n"
              << "  -E <E>: associativity (number of cache lines per set)\n"
              << "  -b <b>: number of block bits (block size = B = 2^b)\n"
              << "  -o <outfilename>: logs output in file for plotting etc.\n"
              << "  -h: prints this help\n";
}

void writeFormattedOutput(const Simulator& simulator, const std::string& tracePrefix, 
                         int setIndexBits, int associativity, int blockOffsetBits, 
                         const std::string& outputFile) {
    std::ofstream outFile;
    std::ostream& out = outputFile.empty() ? std::cout : outFile;
    
    if (!outputFile.empty()) {
        outFile.open(outputFile);
        if (!outFile.is_open()) {
            std::cerr << "Error: Could not open output file: " << outputFile << std::endl;
            return;
        }
    }
    
    // Calculate derived parameters
    int blockSize = 1 << blockOffsetBits;
    int numSets = 1 << setIndexBits;
    double cacheSizeKB = (numSets * associativity * blockSize) / 1024.0;
    
    // Print simulation parameters
    out << "Simulation Parameters:" << std::endl;
    out << "Trace Prefix: " << tracePrefix << std::endl;
    out << "Set Index Bits: " << setIndexBits << std::endl;
    out << "Associativity: " << associativity << std::endl;
    out << "Block Bits: " << blockOffsetBits << std::endl;
    out << "Block Size (Bytes): " << blockSize << std::endl;
    out << "Number of Sets: " << numSets << std::endl;
    out << "Cache Size (KB per core): " << std::fixed << std::setprecision(2) << cacheSizeKB << std::endl;
    out << "MESI Protocol: Enabled" << std::endl;
    out << "Write Policy: Write-back, Write-allocate" << std::endl;
    out << "Replacement Policy: LRU" << std::endl;
    out << "Bus: Central snooping bus" << std::endl;
    out << std::endl;
    
    // Get statistics from simulator
    const auto& processors = simulator.getProcessors();
    const auto& caches = simulator.getCaches();
    const auto& bus = simulator.getBus();
    

    
    
    out << std::endl;
    
    // Print per-core statistics
    for (size_t i = 0; i < processors.size(); i++) {
        const auto& processor = processors[i];
        const auto& cache = caches[i];
        const auto& cacheStats = cache->getStatistics();
        
        out << "Core " << i << " Statistics:" << std::endl;
        out << "Total Instructions: " << processor->getTotalInstructions() << std::endl;
        out << "Total Reads: " << processor->getReadInstructions() << std::endl;
        out << "Total Writes: " << processor->getWriteInstructions() << std::endl;
        out << "Total Execution Cycles: " << processor->getTotalCycles() << std::endl;
        out << "Idle Cycles: " << processor->getIdleCycles() << std::endl;
        out << "Cache Misses: " << cacheStats.getMisses() << std::endl;
        
        double missRate = 0.0;
        if (cacheStats.getAccesses() > 0) {
            missRate = 100.0 * cacheStats.getMisses() / cacheStats.getAccesses();
        }
        
        out << "Cache Miss Rate: " << std::fixed << std::setprecision(2) << missRate << "%" << std::endl;
        out << "Cache Evictions: " << cacheStats.getEvictions() << std::endl;
        out << "Writebacks: " << cacheStats.getWritebacks() << std::endl;
        out << "Bus Invalidations: " << cacheStats.getInvalidations() << std::endl;
        out << "Data Traffic (Bytes): " << cacheStats.getBusTraffic() << std::endl;
        out << std::endl;
    }
    
    // Print overall bus summary
    const auto& busStats = bus->getStatistics();
    uint64_t totalBusTransactions = busStats.getBusReads() + busStats.getBusReadXs() + 
                                   busStats.getBusUpgrades() + busStats.getBusFlushes();
    
    out << "Overall Bus Summary:" << std::endl;
    out << "Total Bus Transactions: " << totalBusTransactions << std::endl;
    out << "Total Bus Traffic (Bytes): " << busStats.getBusTraffic() << std::endl;
    
    if (!outputFile.empty()) {
        outFile.close();
        std::cout << "Output written to " << outputFile << std::endl;
    }
}

int main(int argc, char* argv[]) {
    // Default parameters
    std::string tracePrefix = "";
    int setIndexBits = 6;      // 64 sets by default
    int associativity = 2;     // 2-way set associative by default
    int blockOffsetBits = 5;   // 32-byte blocks by default
    std::string outputFile = "";
    
    // Parse command line arguments
    int opt;
    while ((opt = getopt(argc, argv, "t:s:E:b:o:h")) != -1) {
        switch (opt) {
            case 't':
                tracePrefix = optarg;
                break;
            case 's':
                setIndexBits = std::atoi(optarg);
                break;
            case 'E':
                associativity = std::atoi(optarg);
                break;
            case 'b':
                blockOffsetBits = std::atoi(optarg);
                break;
            case 'o':
                outputFile = optarg;
                break;
            case 'h':
                printHelp();
                return 0;
            default:
                std::cerr << "Unknown option: " << static_cast<char>(opt) << std::endl;
                printHelp();
                return 1;
        }
    }
    
    // Validate parameters
    if (tracePrefix.empty()) {
        std::cerr << "Error: Trace file prefix (-t) is required." << std::endl;
        printHelp();
        return 1;
    }
    
    if (setIndexBits <= 0 || associativity <= 0 || blockOffsetBits <= 0) {
        std::cerr << "Error: Cache parameters must be positive." << std::endl;
        return 1;
    }
    
    // Create and run the simulator
    
    Simulator simulator(tracePrefix, setIndexBits, associativity, blockOffsetBits, outputFile);
    alarm(60); 
    simulator.runSimulation();
    
    
    // Generate formatted output
    writeFormattedOutput(simulator, tracePrefix, setIndexBits, associativity, blockOffsetBits, outputFile);
    
    return 0;
}
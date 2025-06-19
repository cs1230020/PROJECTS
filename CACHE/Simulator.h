#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <vector>
#include <memory>
#include <string>
#include "Processor.h"
#include "Cache.h"
#include "Bus.h"
#include "Statistics.h"

class Simulator {
private:
    // Configuration parameters
    int numCores;              // Number of processor cores
    int setIndexBits;          // Number of set index bits (s)
    int associativity;         // Associativity (E)
    int blockOffsetBits;       // Number of block offset bits (b)
    std::string tracePrefix;   // Prefix for trace files
    std::string outputFile;    // Output file for logging
    
    // Simulation components
    std::vector<std::shared_ptr<Processor>> processors;
    std::vector<std::shared_ptr<Cache>> caches;
    std::shared_ptr<Bus> bus;
    
    // Simulation state
    int currentCycle;
    bool simulationComplete;
    
    // Statistics
    Statistics globalStats;
    
    // Helper methods
    void initializeComponents();
    bool allProcessorsComplete() const;
    void collectStatistics();
    void logStatistics() const;
    
public:
    // Constructor and destructor
    Simulator(const std::string& tracePrefix, int setIndexBits, int associativity, 
              int blockOffsetBits, const std::string& outputFile, int numCores = 4);
    ~Simulator();
    
    // Simulation control
    void initialize();
    void runSimulation();
    void runCycles(int numCycles);
    void runUntilCompletion();
    
    // Simulation status
    bool isComplete() const;
    int getCurrentCycle() const;
    void checkForDeadlock() ;
    
    // Statistics methods
    void printStatistics() const;
    void writeStatisticsToFile() const;
    
    // Experiment methods
    int getMaxExecutionTime() const;
    
    // Utility methods
    void printStatus() const;
    void resolveDeadlock();
    // Add these to the public section of Simulator.h
const std::vector<std::shared_ptr<Processor>>& getProcessors() const {
    return processors;
}

const std::vector<std::shared_ptr<Cache>>& getCaches() const {
    return caches;
}

const std::shared_ptr<Bus>& getBus() const {
    return bus;
}
};

#endif // SIMULATOR_H
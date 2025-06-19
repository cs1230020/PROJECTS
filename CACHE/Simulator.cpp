#include "Simulator.h"
#include <iostream>
#include <fstream>
#include <iomanip>
#include <algorithm>
#include <sstream>
#include <cassert>

Simulator::Simulator(const std::string& tracePrefix, int setIndexBits, int associativity, 
                     int blockOffsetBits, const std::string& outputFile, int numCores)
    : numCores(numCores),
      setIndexBits(setIndexBits),
      associativity(associativity),
      blockOffsetBits(blockOffsetBits),
      tracePrefix(tracePrefix),
      outputFile(outputFile),
      currentCycle(0),
      simulationComplete(false)
{
    // Initialize the bus
    bus = std::make_shared<Bus>();
    
    // Initialize processors and caches
    processors.resize(numCores);
    caches.resize(numCores);
    
    for (int i = 0; i < numCores; i++) {
        // Construct trace file path
        std::ostringstream tracePath;
        tracePath << tracePrefix << "_proc" << i << ".trace";
        
        // Create processor
        processors[i] = std::make_shared<Processor>(i, tracePath.str());
        
        // Create cache
        caches[i] = std::make_shared<Cache>(i, setIndexBits, associativity, blockOffsetBits, bus.get());
        
        // Associate cache with processor
        processors[i]->setCache(caches[i]);
    }
}

Simulator::~Simulator() {
    // Smart pointers will handle cleanup
}

void Simulator::initialize() {
    // Reset all components to initial state
    currentCycle = 0;
    simulationComplete = false;
    
    // Reset statistics
    globalStats.reset();
    
    for (auto& processor : processors) {
        processor->resetStatistics();
    }
    
    for (auto& cache : caches) {
        cache->getStatistics().reset();
    }
    
    bus->resetStatistics();
    bus->connectCaches();
}

void Simulator::runSimulation() {
    // Initialize the simulation
    initialize();
    
    // Run until completion
    runUntilCompletion();
    
    // Collect and log statistics
    collectStatistics();
    logStatistics();
}

// Add this to Simulator.cpp
void Simulator::checkForDeadlock() {
    bool allBlockedOrComplete = true;
    bool anyBlocked = false;
    
    // Check if all processors are blocked or trace is complete
    for (auto& processor : processors) {
        if (!processor->isTraceComplete()) {
            if (processor->isBlocked()) {
                anyBlocked = true;
            } else {
                allBlockedOrComplete = false;
                break;
            }
        }
    }

    // Potential deadlock: all active processors are blocked and the bus isn't busy
    if (allBlockedOrComplete && anyBlocked && !bus->isBusy()) {
 
        
        // Force unblock one or more processors to break the deadlock
        resolveDeadlock();
    }
}

void Simulator::resolveDeadlock() {
   
    
    // Option 1: Unblock all processors
    for (auto& processor : processors) {
        if (processor->isBlocked()) {
            // Find the associated cache and unblock it
            int coreId = processor->getCoreId();
            if (coreId >= 0 && coreId < (int)caches.size()) {
                caches[coreId]->unblock();
                
            }
        }
    }
    
    // Option 2: Reset the bus state
    bus->reset();

}

void Simulator::runCycles(int numCycles) {
    for (int i = 0; i < numCycles && !simulationComplete; i++) {
        // Process one cycle
        currentCycle++;
        
        // Process bus activity
        bus->processCycle();
        
        // Process each processor
        for (auto& processor : processors) {
            if (!processor->isTraceComplete()) {
                processor->executeCycle();
            }
        }
        
        // Check if simulation is complete
        simulationComplete = allProcessorsComplete();
        
        // Check for potential deadlock
        checkForDeadlock();
        
        // Check cycle limit
        if (currentCycle > 2147483647) {
            
            simulationComplete = true;
        }
    }
}






bool Simulator::allProcessorsComplete() const {
    for (const auto& processor : processors) {
        if (!processor->isTraceComplete()) {
            return false;
        }
    }
    return true;
}

bool Simulator::isComplete() const {
    return simulationComplete;
}

int Simulator::getCurrentCycle() const {
    return currentCycle;
}

void Simulator::collectStatistics() {
    // Collect statistics from all components
    for (const auto& processor : processors) {
        globalStats.incrementTotalInstructions(processor->getTotalInstructions());
        globalStats.incrementReadInstructions(processor->getReadInstructions());
        globalStats.incrementWriteInstructions(processor->getWriteInstructions());
    }
    
    for (const auto& cache : caches) {
        const Statistics& cacheStats = cache->getStatistics();
        globalStats.incrementAccesses(cacheStats.getAccesses());
        globalStats.incrementMisses(cacheStats.getMisses());
        globalStats.incrementEvictions(cacheStats.getEvictions());
        globalStats.incrementWritebacks(cacheStats.getWritebacks());
        globalStats.incrementInvalidations(cacheStats.getInvalidations());
        globalStats.incrementBusTraffic(cacheStats.getBusTraffic());
    }
    
    // Add bus statistics
    const Statistics& busStats = bus->getStatistics();
    globalStats.incrementBusReads(busStats.getBusReads());
    globalStats.incrementBusReadXs(busStats.getBusReadXs());
    globalStats.incrementBusUpgrades(busStats.getBusUpgrades());
    globalStats.incrementBusFlushes(busStats.getBusFlushes());
    globalStats.incrementBusTraffic(busStats.getBusTraffic());
    globalStats.incrementInvalidations(busStats.getInvalidations());
}

void Simulator::logStatistics() const {
    // If no output file specified, just return
    if (outputFile.empty()) {
        return;
    }
    
    // Open the output file
    std::ofstream outFile(outputFile);
    if (!outFile.is_open()) {
        std::cerr << "Error: Could not open output file: " << outputFile << std::endl;
        return;
    }
    
    // Write simulation parameters
    outFile << "Simulation Parameters:" << std::endl;
    outFile << "  Trace Prefix: " << tracePrefix << std::endl;
    outFile << "  Number of Cores: " << numCores << std::endl;
    outFile << "  Cache Configuration: " << std::endl;
    outFile << "    Sets: " << (1 << setIndexBits) << std::endl;
    outFile << "    Associativity: " << associativity << std::endl;
    outFile << "    Block Size: " << (1 << blockOffsetBits) << " bytes" << std::endl;
    outFile << "    Cache Size: " << ((1 << setIndexBits) * associativity * (1 << blockOffsetBits)) << " bytes" << std::endl;
    outFile << std::endl;
    
    // Write per-core statistics
    outFile << "Per-Core Statistics:" << std::endl;
    for (int i = 0; i < numCores; i++) {
        outFile << "  Core " << i << ":" << std::endl;
        outFile << "    Read Instructions: " << processors[i]->getReadInstructions() << std::endl;
        outFile << "    Write Instructions: " << processors[i]->getWriteInstructions() << std::endl;
        outFile << "    Total Instructions: " << processors[i]->getTotalInstructions() << std::endl;
        outFile << "    Execution Cycles: " << processors[i]->getTotalCycles() << std::endl;
        outFile << "    Idle Cycles: " << processors[i]->getIdleCycles() << std::endl;
        
        const Statistics& cacheStats = caches[i]->getStatistics();
        outFile << "    Cache Accesses: " << cacheStats.getAccesses() << std::endl;
        outFile << "    Cache Misses: " << cacheStats.getMisses() << std::endl;
        outFile << "    Cache Miss Rate: " << std::fixed << std::setprecision(2) 
                << (cacheStats.getAccesses() > 0 ? 100.0 * cacheStats.getMisses() / cacheStats.getAccesses() : 0.0) 
                << "%" << std::endl;
        outFile << "    Cache Evictions: " << cacheStats.getEvictions() << std::endl;
        outFile << "    Cache Writebacks: " << cacheStats.getWritebacks() << std::endl;
        outFile << std::endl;
    }
    
    // Write global statistics
    outFile << "Global Statistics:" << std::endl;
    outFile << "  Total Execution Cycles: " << currentCycle << std::endl;
    outFile << "  Maximum Execution Time: " << getMaxExecutionTime() << std::endl;  // Add this line
    outFile << "  Total Instructions: " << globalStats.getTotalInstructions() << std::endl;
    outFile << "  Bus Invalidations: " << globalStats.getInvalidations() << std::endl;
    outFile << "  Bus Traffic: " << globalStats.getBusTraffic() << " bytes" << std::endl;
    
    // Close the file
    outFile.close();
}

void Simulator::printStatistics() const {
    std::cout << "Simulation Statistics:" << std::endl;
    std::cout << "  Trace Prefix: " << tracePrefix << std::endl;
    std::cout << "  Total Execution Cycles: " << currentCycle << std::endl;
    std::cout << "  Maximum Execution Time: " << getMaxExecutionTime() << std::endl; 
    // Print per-core statistics
    for (int i = 0; i < numCores; i++) {
        std::cout << "  Core " << i << ":" << std::endl;
        std::cout << "    Read Instructions: " << processors[i]->getReadInstructions() << std::endl;
        std::cout << "    Write Instructions: " << processors[i]->getWriteInstructions() << std::endl;
        std::cout << "    Total Instructions: " << processors[i]->getTotalInstructions() << std::endl;
        std::cout << "    Execution Cycles: " << processors[i]->getTotalCycles() << std::endl;
        std::cout << "    Idle Cycles: " << processors[i]->getIdleCycles() << std::endl;
        
        const Statistics& cacheStats = caches[i]->getStatistics();
        std::cout << "    Cache Miss Rate: " << std::fixed << std::setprecision(2) 
                  << (cacheStats.getAccesses() > 0 ? 100.0 * cacheStats.getMisses() / cacheStats.getAccesses() : 0.0) 
                  << "%" << std::endl;
        std::cout << "    Cache Evictions: " << cacheStats.getEvictions() << std::endl;
        std::cout << "    Cache Writebacks: " << cacheStats.getWritebacks() << std::endl;
    }
    
    // Print bus statistics
    std::cout << "  Bus Statistics:" << std::endl;
    std::cout << "    Invalidations: " << globalStats.getInvalidations() << std::endl;
    std::cout << "    Data Traffic: " << globalStats.getBusTraffic() << " bytes" << std::endl;
}

void Simulator::writeStatisticsToFile() const {
    logStatistics();
}

int Simulator::getMaxExecutionTime() const {
    int maxTime = 0;
    for (const auto& processor : processors) {
        // Calculate total time as execution + idle cycles
        int totalTime = processor->getTotalCycles() + processor->getIdleCycles();
        printf("%d\n", totalTime);
        maxTime = std::max(maxTime, totalTime);
    }
    return maxTime;
}

void Simulator::printStatus() const {
    std::cout << "Simulator Status:" << std::endl;
    std::cout << "  Current Cycle: " << currentCycle << std::endl;
    std::cout << "  Simulation Complete: " << (simulationComplete ? "Yes" : "No") << std::endl;
    
    // Print processor status
    for (int i = 0; i < numCores; i++) {
        std::cout << "  Processor " << i << " Status:" << std::endl;
        std::cout << "    Trace Complete: " << (processors[i]->isTraceComplete() ? "Yes" : "No") << std::endl;
        std::cout << "    Blocked: " << (processors[i]->isBlocked() ? "Yes" : "No") << std::endl;
        std::cout << "    Instructions Executed: " << processors[i]->getTotalInstructions() << std::endl;
    }
    
    std::cout << "  Bus Status:" << std::endl;
    std::cout << "    Busy: " << (bus->isBusy() ? "Yes" : "No") << std::endl;
}
void Simulator::runUntilCompletion() {
    const int MAX_CYCLES = 2147483647;   
    while (!simulationComplete && currentCycle < MAX_CYCLES) {
        runCycles(1);
    }
    if (currentCycle >= MAX_CYCLES) {
        std::cout << "Simulation timed out after " << MAX_CYCLES << " cycles." << std::endl;
        printStatus();
    }
}
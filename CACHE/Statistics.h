#ifndef STATISTICS_H
#define STATISTICS_H

#include <cstdint>
#include <string>

class Statistics {
private:
    // Cache statistics
    uint64_t accesses;          // Total cache accesses
    uint64_t misses;            // Total cache misses
    uint64_t readMisses;        // Read misses
    uint64_t writeMisses;       // Write misses
    uint64_t evictions;         // Cache line evictions
    uint64_t writebacks;        // Writebacks to memory
    
    // Processor statistics
    uint64_t totalInstructions; // Total instructions executed
    uint64_t readInstructions;  // Read instructions
    uint64_t writeInstructions; // Write instructions
    
    // Bus statistics
    uint64_t busReads;          // BusRd operations
    uint64_t busReadXs;         // BusRdX operations
    uint64_t busUpgrades;       // BusUpgr operations
    uint64_t busFlushes;        // Flush operations
    uint64_t invalidations;     // Cache line invalidations
    uint64_t busTraffic;        // Total bus traffic in bytes
    
public:
    // Constructor
    Statistics();
    
    // Reset all statistics
    void reset();
    
    // Cache statistics methods
    void incrementAccesses(uint64_t count = 1);
    void incrementMisses(uint64_t count = 1);
    void incrementReadMisses(uint64_t count = 1);
    void incrementWriteMisses(uint64_t count = 1);
    void incrementEvictions(uint64_t count = 1);
    void incrementWritebacks(uint64_t count = 1);
    void incrementReads(uint64_t count = 1);
void incrementWrites(uint64_t count = 1);
    
    uint64_t getAccesses() const;
    uint64_t getMisses() const;
    uint64_t getReadMisses() const;
    uint64_t getWriteMisses() const;
    uint64_t getEvictions() const;
    uint64_t getWritebacks() const;
    
    // Processor statistics methods
    void incrementTotalInstructions(uint64_t count = 1);
    void incrementReadInstructions(uint64_t count = 1);
    void incrementWriteInstructions(uint64_t count = 1);
    
    uint64_t getTotalInstructions() const;
    uint64_t getReadInstructions() const;
    uint64_t getWriteInstructions() const;
    
    // Bus statistics methods
    void incrementBusReads(uint64_t count = 1);
    void incrementBusReadXs(uint64_t count = 1);
    void incrementBusUpgrades(uint64_t count = 1);
    void incrementBusFlushes(uint64_t count = 1);
    void incrementInvalidations(uint64_t count = 1);
    void incrementBusTraffic(uint64_t bytes);
    
    uint64_t getBusReads() const;
    uint64_t getBusReadXs() const;
    uint64_t getBusUpgrades() const;
    uint64_t getBusFlushes() const;
    uint64_t getInvalidations() const;
    uint64_t getBusTraffic() const;
    
    // Derived statistics
    double getMissRate() const;
    double getReadMissRate() const;
    double getWriteMissRate() const;
    
    // Utility methods
    std::string toString() const;
    void print() const;
};

#endif // STATISTICS_H
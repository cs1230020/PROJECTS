#ifndef PROCESSOR_H
#define PROCESSOR_H

#include <string>
#include <fstream>
#include <queue>
#include <memory>
#include "Cache.h"

// Forward declaration
class Cache;

// Enum for memory operation type
enum class MemoryOperation {
    READ,
    WRITE
};

// Structure to represent a memory reference instruction
struct MemoryReference {
    MemoryOperation operation;
    uint32_t address;
    
    MemoryReference(MemoryOperation op, uint32_t addr) 
        : operation(op), address(addr) {}
};

class Processor {
private:
    int coreId;                         // ID of this processor core
    std::shared_ptr<Cache> cache;       // L1 cache for this processor
    std::ifstream traceFile;            // Trace file for this processor
    std::queue<MemoryReference> pendingReferences; // Queue of memory references to process
    
    // Statistics
    int totalInstructions;              // Total instructions processed
    int readInstructions;               // Number of read instructions
    int writeInstructions;              // Number of write instructions
    int totalCycles;                    // Total execution cycles
    int idleCycles;                     // Cycles spent waiting for cache
    bool traceComplete;                 // Flag indicating if trace processing is complete
    bool blocked;                       // Flag indicating if processor is blocked
    
    // Helper methods
    bool loadNextReference();           // Load next reference from trace file
    
public:
    // Constructor and destructor
    Processor(int coreId, const std::string& traceFilePath);
    ~Processor();
    
    // Initialize the processor with a cache
    void setCache(std::shared_ptr<Cache> cache);
    
    // Process one cycle of execution
    bool executeCycle();
    
    // Check if processor has completed its trace
    bool isTraceComplete() const;
    
    // Check if processor is blocked waiting for cache
    bool isBlocked() const;
    
    // Get processor statistics
    int getCoreId() const;
    int getTotalInstructions() const;
    int getReadInstructions() const;
    int getWriteInstructions() const;
    int getTotalCycles() const;
    int getIdleCycles() const;
    
    // Reset processor statistics
    void resetStatistics();
    
    // Print processor status
    void printStatus() const;
};

#endif // PROCESSOR_H
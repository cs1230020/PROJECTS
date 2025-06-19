#ifndef BUS_H
#define BUS_H

#include <vector>
#include <memory>
#include <functional>
#include <queue>
#include <mutex>
#include "Statistics.h"

extern unsigned int currentGlobalCycle;

// Forward declarations
class Cache;

// Enum for bus operations
enum class BusOperation {
    BusRd,      // Bus read (for read miss)
    BusRdX,     // Bus read exclusive (for write miss)
    BusUpgr,    // Bus upgrade (for write to shared line)
    Flush,      // Flush (writeback to memory)
    FlushOpt    // Flush with data transfer to another cache
};

// Structure to represent a bus transaction
struct BusTransaction {
    BusOperation operation;     // Type of bus operation
    uint32_t address;           // Memory address
    int sourceId;               // ID of the requesting core
    bool dataProvided;          // Flag indicating if data was provided by another cache
    int cycles;                 // Cycles taken by this transaction
    
    BusTransaction(BusOperation op, uint32_t addr, int src)
        : operation(op), address(addr), sourceId(src), dataProvided(false), cycles(0) {}
};

class Bus {
private:
    bool busy;
    int currentCycles; // you might later remove this if not needed
    unsigned int busyUntilCycle = 0;  // <-- ADD THIS for fast-forwarding bus busy time
    std::vector<Cache*> caches;

    Statistics stats;
    std::queue<BusTransaction> pendingTransactions;
    
    // Helper methods
    void processSnooping(BusTransaction& transaction);
    
public:
    // Constructor and destructor
    Bus();
    ~Bus();
    
    // Register a cache with the bus
    void registerCache(Cache* cache, int coreId);
    
    // Perform a bus operation
    bool busOperation(BusOperation operation, uint32_t address, int sourceId, 
                     bool& dataProvided, int& cycles);
    
    // Process one cycle of bus activity
    void processCycle();
    
    // Check if bus is busy
   
    // Get bus statistics
    const Statistics& getStatistics() const;
    
    // Reset bus statistics
    void resetStatistics();
    
    // Utility methods
    std::string operationToString(BusOperation op) const;
    
    // Debug methods
    void printStatus() const;
    void connectCaches();
    void reset() {
    busy = false;
    currentCycles = 0;
    while (!pendingTransactions.empty()) {
        pendingTransactions.pop();
    }
}
bool isBusy() const;
void processNextPendingTransaction();
};


#endif // BUS_H
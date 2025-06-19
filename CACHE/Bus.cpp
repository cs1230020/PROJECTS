#include "Bus.h"
#include "Cache.h"
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <cassert>

Bus::Bus()
    : busy(false),
      currentCycles(0)
{
    // Initialize the bus
}

Bus::~Bus() {
    // Nothing special to clean up
}

void Bus::registerCache(Cache* cache, int coreId) {
    // Ensure the caches vector is large enough
    if (coreId >= static_cast<int>(caches.size())) {
        caches.resize(coreId + 1, nullptr);
    }
    
    // Register the cache
    caches[coreId] = cache;
}

// Modify Bus::busOperation to keep the bus busy until cycles are processed
bool Bus::busOperation(BusOperation operation, uint32_t address, int sourceId, 
                      bool& dataProvided, int& cycles) {
    // Create a new transaction
    BusTransaction transaction(operation, address, sourceId);
    
    // If the bus is busy, queue the transaction
    if (busy) {
        pendingTransactions.push(transaction);
        return false;
    }
    
    // Process the transaction immediately
    busy = true;
    dataProvided = false;
    cycles = 0;
    
    // Process snooping for this transaction
    processSnooping(transaction);
    
    // Update statistics based on the operation
    switch (operation) {
        case BusOperation::BusRd:
            stats.incrementBusReads();
            break;
            
        case BusOperation::BusRdX:
            stats.incrementBusReadXs();
            break;
            
        case BusOperation::BusUpgr:
            stats.incrementBusUpgrades();
            break;
            
        case BusOperation::Flush:
        case BusOperation::FlushOpt:
            stats.incrementBusFlushes();
            break;
    }
    
    // Calculate base cycles for the operation
    if (transaction.dataProvided) {
        // Data provided by another cache
        // Calculate based on block size (assuming 4 bytes per word)
        int blockSize = 32; // Default block size (adjust based on your configuration)
        int wordsInBlock = blockSize / 4;
        cycles = transaction.cycles; // 2 cycles per word
        stats.incrementBusTraffic(blockSize);
 
    } else {
        // Data from memory
        if (operation == BusOperation::Flush || operation == BusOperation::FlushOpt) {
            cycles = 100; // Memory writeback
        } else {
      
            cycles = 100; // Memory read
        }
    }
    
    // Set the cycles for the current transaction
    currentCycles = cycles;
    
    // Update the output parameters
    dataProvided = transaction.dataProvided;
    
    // Keep the bus busy until cycles are processed in processCycle
    // Remove the "busy = false" line here
    busy = false;
    return true;
}

// In Bus.cpp, modify the processSnooping method
void Bus::processSnooping(BusTransaction& transaction) {
    // Have all caches snoop this transaction

    int totalInvalidations = 0;
    
    for (size_t i = 0; i < caches.size(); i++) {
        if (caches[i] && static_cast<int>(i) != transaction.sourceId) {
            int initialInvalidations = caches[i]->getStatistics().getInvalidations();
            
            int snoopCycles = 0;
            caches[i]->snoop(transaction.operation, transaction.address, 
                            transaction.sourceId, transaction.dataProvided, snoopCycles);
            
            int newInvalidations = caches[i]->getStatistics().getInvalidations();
            int invalidationsThisSnoop = newInvalidations - initialInvalidations;
            
            if (invalidationsThisSnoop > 0) {
                totalInvalidations += invalidationsThisSnoop;
            }
            
            // If this snoop took cycles and provided data, add to the transaction cycles
            if (snoopCycles > 0 && transaction.dataProvided) {
                transaction.cycles += snoopCycles;
            }
        }
    }
    
    
}

// Improve Bus::processCycle to handle pending transactions properly
void Bus::processCycle() {
    // If the bus is busy, decrement the current cycles
    if (busy && currentCycles > 0) {
        currentCycles--;
        
        // If we've completed the current transaction, check for pending ones
        if (currentCycles == 0) {
            busy = false; // Bus is no longer busy
            
            // Process any pending transactions
            processNextPendingTransaction();
        }
    } else if (!busy && !pendingTransactions.empty()) {
        // Bus isn't busy but there are pending transactions
        processNextPendingTransaction();
    }
}

// Add this helper method to Bus.cpp
void Bus::processNextPendingTransaction() {
    if (pendingTransactions.empty()) {
        return;
    }
    
    BusTransaction transaction = pendingTransactions.front();
    pendingTransactions.pop();
    
    // Process the next transaction
    bool dataProvided = false;
    int cycles = 0;

    // Initiate the bus operation for the next transaction
    bool success = busOperation(transaction.operation, transaction.address, 
                               transaction.sourceId, dataProvided, cycles);
    
    if (!success) {
        // If operation couldn't be processed, requeue it
        pendingTransactions.push(transaction);
    }
}




const Statistics& Bus::getStatistics() const {
    return stats;
}

void Bus::resetStatistics() {
    stats.reset();
}

std::string Bus::operationToString(BusOperation op) const {
    switch (op) {
        case BusOperation::BusRd:
            return "BusRd";
        case BusOperation::BusRdX:
            return "BusRdX";
        case BusOperation::BusUpgr:
            return "BusUpgr";
        case BusOperation::Flush:
            return "Flush";
        case BusOperation::FlushOpt:
            return "FlushOpt";
        default:
            return "Unknown";
    }
}

void Bus::printStatus() const {
    std::cout << "Bus Status:" << std::endl;
    std::cout << "  Busy: " << (busy ? "Yes" : "No") << std::endl;
    if (busy) {
        std::cout << "  Cycles Remaining: " << currentCycles << std::endl;
    }
    std::cout << "  Pending Transactions: " << pendingTransactions.size() << std::endl;
    
    std::cout << "  Statistics:" << std::endl;
    std::cout << "    Bus Reads: " << stats.getBusReads() << std::endl;
    std::cout << "    Bus ReadXs: " << stats.getBusReadXs() << std::endl;
    std::cout << "    Bus Upgrades: " << stats.getBusUpgrades() << std::endl;
    std::cout << "    Bus Flushes: " << stats.getBusFlushes() << std::endl;
    std::cout << "    Bus Traffic: " << stats.getBusTraffic() << " bytes" << std::endl;
    std::cout << "    Invalidations: " << stats.getInvalidations() << std::endl;
}
void Bus::connectCaches() {
    // Create a vector of all registered caches
    std::vector<Cache*> allCaches;
    for (size_t i = 0; i < caches.size(); i++) {
        if (caches[i]) {
            allCaches.push_back(caches[i]);
        }
    }
    
    // Set the reference to all caches in each cache
    for (size_t i = 0; i < caches.size(); i++) {
        if (caches[i]) {
            caches[i]->setCaches(allCaches);
        }
    }
}
bool Bus::isBusy() const {
    return busy;
}


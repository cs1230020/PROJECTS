#include "Processor.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cassert>

Processor::Processor(int coreId, const std::string& traceFilePath)
    : coreId(coreId),
      cache(nullptr),
      totalInstructions(0),
      readInstructions(0),
      writeInstructions(0),
      totalCycles(0),
      idleCycles(0),
      traceComplete(false),
      blocked(false)
{
    // Open the trace file
    traceFile.open(traceFilePath);
    if (!traceFile.is_open()) {
        std::cerr << "Error: Could not open trace file: " << traceFilePath << std::endl;
        traceComplete = true;  // Mark as complete to avoid processing
    }
    
    // Load the first few references
    for (int i = 0; i < 10 && loadNextReference(); i++) {
        // Just preload some references
    }
}

Processor::~Processor() {
    if (traceFile.is_open()) {
        traceFile.close();
    }
}

void Processor::setCache(std::shared_ptr<Cache> newCache) {
    cache = newCache;
}

bool Processor::loadNextReference() {
    if (traceFile.eof() || !traceFile.is_open()) {
        return false;
    }
    
    std::string line;
    if (std::getline(traceFile, line)) {
        std::istringstream iss(line);
        char opType;
        std::string addressStr;
        
        if (iss >> opType >> addressStr) {
            // Parse the operation type
            MemoryOperation op;
            if (opType == 'R' || opType == 'r') {
                op = MemoryOperation::READ;
            } else if (opType == 'W' || opType == 'w') {
                op = MemoryOperation::WRITE;
            } else {
                std::cerr << "Error: Unknown operation type: " << opType << std::endl;
                return false;
            }
            
            // Parse the address
            uint32_t address = 0;
            if (addressStr.substr(0, 2) == "0x") {
                // Hexadecimal address
                address = std::stoul(addressStr, nullptr, 16);
            } else {
                // Decimal address
                address = std::stoul(addressStr);
            }
            
            // Create and queue the memory reference
            pendingReferences.emplace(op, address);
            return true;
        }
    }
    
    // If we reach here, we've reached the end of the file
    if (traceFile.eof() && pendingReferences.empty()) {
        traceComplete = true;
    }
    
    return false;
}

bool Processor::executeCycle() {
    totalCycles++;  // Increment the total cycles for every processor cycle
    
    // If processor is blocked, check if the cache is blocking, if so, increment idle cycles
    if (blocked) {
        if (cache->isBlocking()) {
            idleCycles++;  // Increment idle cycles since cache is still blocking
            return false;  // Don't execute any operation during this cycle
        } else {
            blocked = false;  // Cache is no longer blocking, processor can continue
        }
    }

    // If no pending references, try to load the next reference from the trace
    if (pendingReferences.empty()) {
        if (!loadNextReference()) {
            traceComplete = true;  // Trace is complete
            totalCycles--;  // Subtract the last cycle since we didn't process any
            return false;  // No more references to process
        }
    }

    // Get the next memory reference to process
    MemoryReference ref = pendingReferences.front();
    pendingReferences.pop();  // Remove the reference from the queue
    int cycles = 0;
    bool success = false;
    
    // Perform memory operation based on the operation type (READ/WRITE)
    if (ref.operation == MemoryOperation::READ) {
        success = cache->read(ref.address, cycles);
        if (success) {
            readInstructions++;
            totalInstructions++;
        }
    } else {  // WRITE operation
        success = cache->write(ref.address, cycles);
        if (success) {
            writeInstructions++;
            totalInstructions++;
        }
    }


    // If the operation was successful and took more than 1 cycle (blocking operation)
    if (success && cycles > 1) {
        blocked = true;  // Processor is blocked while waiting for the cache
        idleCycles += cycles;  // Add the cycles the processor was idle
         // Add the cycles to the total cycle count
    }

    // Try to load up to 5 more references if there's space in the queue
    if (pendingReferences.size() < 5) {
        for (int i = 0; i < 5 && loadNextReference(); i++) {
            // Load next references until there are 5 or no more references to load
        }
    }
    
    return success;  // Return true if the operation was successful
}


bool Processor::isTraceComplete() const {
    return traceComplete;
}

bool Processor::isBlocked() const {
    return blocked;
}

int Processor::getCoreId() const {
    return coreId;
}

int Processor::getTotalInstructions() const {
    return totalInstructions;
}

int Processor::getReadInstructions() const {
    return readInstructions;
}

int Processor::getWriteInstructions() const {
    return writeInstructions;
}

int Processor::getTotalCycles() const {
    return totalCycles;
}

int Processor::getIdleCycles() const {
    return idleCycles;
}

void Processor::resetStatistics() {
    totalInstructions = 0;
    readInstructions = 0;
    writeInstructions = 0;
    totalCycles = 0;
    idleCycles = 0;
    blocked = false;
}

void Processor::printStatus() const {
    std::cout << "Processor Core " << coreId << " Status:" << std::endl;
    std::cout << "  Total Instructions: " << totalInstructions 
              << " (Read: " << readInstructions << ", Write: " << writeInstructions << ")" << std::endl;
    std::cout << "  Total Cycles: " << totalCycles << std::endl;
    std::cout << "  Idle Cycles: " << idleCycles << std::endl;
    std::cout << "  IPC: " << std::fixed << std::setprecision(2) 
              << (totalCycles > 0 ? static_cast<double>(totalInstructions) / totalCycles : 0.0) << std::endl;
    std::cout << "  Trace Complete: " << (traceComplete ? "Yes" : "No") << std::endl;
    std::cout << "  Blocked: " << (blocked ? "Yes" : "No") << std::endl;
}
#include "Cache.h"
#include "Bus.h"
#include <iostream>
#include <iomanip>
#include <bitset>
#include <cassert>
#include "CacheUtils.h"
extern int globalUtilCycle;

Cache::Cache(int coreId, int setIndexBits, int associativity, int blockOffsetBits, Bus* bus)
    : coreId(coreId),
      associativity(associativity),
      blockOffsetBits(blockOffsetBits),
      setIndexBits(setIndexBits),
      bus(bus),
      isBlocked(false),
      blockedCycles(0)
{
    // Calculate derived parameters
    numSets = 1 << setIndexBits;
    blockSize = 1 << blockOffsetBits;
    tagBits = 32 - setIndexBits - blockOffsetBits;
    
    // Initialize cache sets
    sets.resize(numSets, CacheSet(associativity, blockSize));
    
    // Register this cache with the bus
    if (bus) {
        bus->registerCache(this, coreId);
    }
}

// Add method to set references to other caches
void Cache::setCaches(const std::vector<Cache*>& otherCaches) {
    caches = otherCaches;
}

int Cache::getLineIndex(unsigned int address) const {
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    
    const CacheSet& set = sets[setIndex];
    return set.findLine(tag);
}

Cache::~Cache() {
    // Nothing special to clean up
}

unsigned int Cache::getTag(unsigned int address) const {
    return address >> (setIndexBits + blockOffsetBits);
}

unsigned int Cache::getSetIndex(unsigned int address) const {
    return (address >> blockOffsetBits) & ((1 << setIndexBits) - 1);
}

unsigned int Cache::getBlockOffset(unsigned int address) const {
    return address & ((1 << blockOffsetBits) - 1);
}

bool Cache::read(unsigned int address, int& cycles) {
    // If cache is blocked, can't process this request
    if (isBlocked) {
        return false;
    }
    stats.incrementAccesses();
    stats.incrementReads();
    
    bool hit = lookupAndUpdate(address, false, cycles);
    if (hit) {
        // If it's a hit, just return with 1 cycle
        cycles = 1;
        return true;
    } else {
        stats.incrementReadMisses();
        isBlocked = true;
        
        bool dataProvided = false;
        int busCycles = 0;
        
        // First, check if we need to evict a line
        unsigned int setIndex = getSetIndex(address);
        CacheSet& set = sets[setIndex];
        



        // Now, initiate the bus operation
        bool success = bus->busOperation(BusOperation::BusRd, address, coreId, dataProvided, busCycles);
        
        // After the bus operation
        if (success && dataProvided) {
            // Data was provided by another cache
            allocateLine(address, false, busCycles, true);  // Allocate data from another cache
        } else {
            // Data was not provided by other caches, fetch it from memory
            allocateLine(address, false, busCycles, false);  // Allocate data from memory
        }

        // Update total cycles
        cycles += busCycles;
        blockedCycles += busCycles - 1; // Track blocked cycles (subtract 1 for hit cycle)
        
        return true;
    }
}


bool Cache::write(unsigned int address, int& cycles) {
    // If cache is blocked, can't process this request
    if (isBlocked) {
        return false;
    }

    stats.incrementAccesses();
    stats.incrementWrites();
    
    // Try to find the data in the cache
    bool hit = lookupAndUpdate(address, true, cycles);

    
    if (hit) {
        // Cache hit - takes 1 cycle

                // Cache hit
                unsigned int tag = getTag(address);
                unsigned int setIndex = getSetIndex(address);
                int busCycles = 0;
                bool dummy = false;
                
                CacheSet& set = sets[setIndex];
                int lineIndex = set.findLine(tag);
                CacheLine& line = set.getLine(lineIndex);
        
                
                    // Write hit
                    if (line.getState() == CacheState::SHARED || line.getState() == CacheState::EXCLUSIVE) {
                        // Need to upgrade to MODIFIED
                        if (line.getState() == CacheState::SHARED) {
                            // Issue a bus upgrade to inform other caches
                            bus->busOperation(BusOperation::BusUpgr, address, coreId, dummy, busCycles);
                            cycles += busCycles;
                        }
                        line.setState(CacheState::MODIFIED);
                    }
                    
                    // If already MODIFIED, no need to do anything
              
                
        
        return true;
    } else {
        // Cache miss - need to fetch from memory or other caches
        stats.incrementWriteMisses();
        
        // Block the cache until the miss is resolved
        isBlocked = true;
        
        // Initialize eviction cycles - separate from bus cycles
        int evictionCycles = 0;
        
        // Handle eviction if the set is full before inserting new data
        unsigned int setIndex = getSetIndex(address);
        CacheSet& set = sets[setIndex];

        
        // Now perform the bus operation
        bool dataProvided = false;
        int busCycles = evictionCycles; // Start with cycles from eviction
        bool success = bus->busOperation(BusOperation::BusRdX, address, coreId, dataProvided, busCycles);
        
        if (success && dataProvided) {
            allocateLine(address, true, busCycles, true);
        } else {
            allocateLine(address, true, busCycles, false);
        }

        // Update total cycles
        cycles += busCycles;
        blockedCycles = busCycles > 0 ? busCycles - 1 : 0; // Ensure non-negative
        
        return true;
    }
}

bool Cache::lookupAndUpdate(unsigned int address, bool isWrite, int& cycles) {
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    int busCycles = 0;
    bool dummy = false;
    
    CacheSet& set = sets[setIndex];
    int lineIndex = set.findLine(tag);
    
    if (lineIndex != -1) {

        // Update LRU status
        set.updateLRU(lineIndex);
        return true;
    }

    
    return false; // Cache miss
}

void Cache::allocateLine(unsigned int address, bool isWrite, int& cycles, bool busresponse) {
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    
    CacheSet& set = sets[setIndex];

    
    // Check if we need to evict a line
    if (set.isFull()) {
        int victimIndex = set.getLRUIndex();
        CacheLine& victimLine = set.getLine(victimIndex);
        
        // Evict the victim line if necessary
        if (victimLine.isValid()) {
            // Construct the address from tag, set index, and offset 0
            unsigned int victimAddress = (victimLine.getTag() << (setIndexBits + blockOffsetBits)) | 
                                        (setIndex << blockOffsetBits);
            evictLine(victimLine, victimAddress, cycles);
            stats.incrementEvictions();
        }
    }
   
    
    // Allocate a new line
    int lineIndex = set.allocateLine(tag);
    CacheLine& line = set.getLine(lineIndex);
    
    // Set the appropriate state based on the operation
    if (isWrite) {
        line.setState(CacheState::MODIFIED);
    } else {
        // For a read, the state depends on whether other caches have the data
        // This was determined during the bus operation
        // If no other cache has it, it's EXCLUSIVE, otherwise SHARED
        bool otherCachesHaveData = busresponse; 
        line.setState(otherCachesHaveData ? CacheState::SHARED : CacheState::EXCLUSIVE);
    }
    
    // Unblock the cache
    isBlocked = false;
}

// Modified to take the line's address
void Cache::evictLine(CacheLine& line, unsigned int address, int& cycles) {
    if (line.getState() == CacheState::MODIFIED) {
        cycles += 100;
        stats.incrementWritebacks();  
    } 
    else if (line.getState() == CacheState::SHARED) {
        // Check if we're the last cache with this line in SHARED state
        int sharedCacheCount = 0;
        int lastSharedCacheId = -1;
        
        for (Cache* cache : caches) {
            if (cache && cache->coreId != coreId) {
                int lineIndex = cache->getLineIndex(address);
                if (lineIndex != -1) {
                    CacheLine& otherLine = cache->sets[getSetIndex(address)].getLine(lineIndex);
                    if (otherLine.isValid() && otherLine.getState() == CacheState::SHARED) {
                        sharedCacheCount++;
                        lastSharedCacheId = cache->coreId;
                    }
                }
            }
        }

        // If only one other cache has it in SHARED state, promote it to EXCLUSIVE
        if (sharedCacheCount == 1 && lastSharedCacheId != -1) {
            Cache* lastCache = caches[lastSharedCacheId];
            int lineIndex = lastCache->getLineIndex(address);
            if (lineIndex != -1) {
                CacheLine& otherLine = lastCache->sets[getSetIndex(address)].getLine(lineIndex);
                otherLine.setState(CacheState::EXCLUSIVE);
            }
        }
    }
    
    // Invalidate the line
    line.setState(CacheState::INVALID);  
}

bool Cache::snoop(BusOperation op, unsigned int address, int sourceId, bool& providedData, int& cycles) {
    // Don't snoop our own operations
    if (sourceId == coreId) {
        return true;
    }
    
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    
    CacheSet& set = sets[setIndex];
    int lineIndex = set.findLine(tag);
    
    if (lineIndex == -1) {
        // We don't have this line, nothing to do
        return true;
    }
    
    CacheLine& line = set.getLine(lineIndex);
    CacheState currentState = line.getState();
    
    switch (op) {
        case BusOperation::BusRd:
            if (currentState == CacheState::MODIFIED) {
                // We have the modified data, need to provide it
                providedData = true;
                
                // Sending data takes 2 cycles per word
                int wordsInBlock = blockSize / 4; // 4 bytes per word
                cycles += 2 * wordsInBlock;
                cycles += 100;
                stats.incrementWritebacks();
                // Update bus traffic statistics
                stats.incrementBusTraffic(blockSize);
                stats.incrementBusTraffic(blockSize);
                
                // Change state to SHARED, since now it is no longer exclusive
                line.setState(CacheState::SHARED);

            } else if (currentState == CacheState::EXCLUSIVE) {
                // We have exclusive access but data is clean
                providedData = true;
                int wordsInBlock = blockSize / 4;
                cycles += 2 * wordsInBlock;
                
                // Update bus traffic statistics
                stats.incrementBusTraffic(blockSize);
                
                // Change state to SHARED, since now it is no longer exclusive
                line.setState(CacheState::SHARED);
            } else if (currentState == CacheState::SHARED) {
                // We already share the data, just return the value
                providedData = true; // Indicating that data is provided
                int wordsInBlock = blockSize / 4;
                cycles += 2 * wordsInBlock;
                
                // No state change needed
                stats.incrementBusTraffic(blockSize); // Count the traffic
            }
            break;
    
        case BusOperation::BusRdX:
            if (currentState == CacheState::MODIFIED) {
                // We have the modified data, need to provide it
                providedData = true;
                
                // Sending data takes 2 cycles per word
                int wordsInBlock = blockSize / 4; // 4 bytes per word
                cycles += 200;
                stats.incrementWritebacks();

                
                // Update bus traffic statistics
                stats.incrementBusTraffic(blockSize);
                stats.incrementBusTraffic(blockSize);
                // Invalidate our copy
                line.setState(CacheState::INVALID);
                stats.incrementInvalidations();
            } else if (currentState == CacheState::EXCLUSIVE) {
                // We have exclusive access but data is clean
                providedData = true;
                int wordsInBlock = blockSize / 4;
                cycles += 100;
                 
                
                // Update bus traffic statistics
                stats.incrementBusTraffic(blockSize);
                
                // Invalidate our copy
                line.setState(CacheState::INVALID);
                stats.incrementInvalidations();
            } else if (currentState == CacheState::SHARED) {
                // We have shared access, but another processor needs exclusive access
                providedData = true;
                int wordsInBlock = blockSize / 4;
                cycles += 100;
                 
                
                // Update bus traffic statistics
                stats.incrementBusTraffic(blockSize);
                
                // Invalidate our copy
                line.setState(CacheState::INVALID);
                stats.incrementInvalidations();
            }
            break;
        
        case BusOperation::BusUpgr:
            if (currentState == CacheState::SHARED) {
                // Another cache wants to upgrade from SHARED to MODIFIED
                line.setState(CacheState::INVALID); // Invalidate our copy
                stats.incrementInvalidations();
            } else if (currentState == CacheState::EXCLUSIVE || currentState == CacheState::MODIFIED) {
                // This is unexpected in MESI protocol but handle it anyway
               
                
                // If we have the line in exclusive or modified state, provide the data
                providedData = true;
                int wordsInBlock = blockSize / 4;
                cycles += 2 * wordsInBlock;
                stats.incrementBusTraffic(blockSize);
                
                // Invalidate our copy
                line.setState(CacheState::INVALID);
                stats.incrementInvalidations();
            }
            break;
        
        default:
            // Unknown operation
  
            break;
    }
    
    return true;
}

// Remaining methods unchanged
bool Cache::isHit(unsigned int address) const {
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    
    const CacheSet& set = sets[setIndex];
    return set.findLine(tag) != -1;
}

bool Cache::isBlocking() const {
    return isBlocked;
}

void Cache::unblock() {
    isBlocked = false;
}

int Cache::getBlockedCycles() const {
    return blockedCycles;
}

const Statistics& Cache::getStatistics() const {
    return stats;
}

Statistics& Cache::getStatistics() {
    return stats;
}

void Cache::resetStatistics() {
    stats.reset();
    blockedCycles = 0;
}

void Cache::processCycle() {
    // If cache is blocked and waiting for operation to complete
    if (isBlocked && blockedCycles > 0) {
        blockedCycles--;
        
        // If operation is complete, finish the memory access
        if (blockedCycles == 0) {
            // Unblock the cache
            isBlocked = false;
        }
    }
}

void Cache::printState() const {
    std::cout << "Cache State for Core " << coreId << ":" << std::endl;
    std::cout << "  Sets: " << numSets << ", Associativity: " << associativity 
              << ", Block Size: " << blockSize << " bytes" << std::endl;
    
    for (unsigned int i = 0; i < sets.size(); i++) {
        const CacheSet& set = sets[i];
        std::cout << "  Set " << i << ":" << std::endl;
        
        for (int j = 0; j < associativity; j++) {
            const CacheLine& line = set.getLine(j);
            if (line.isValid()) {
                std::cout << "    Line " << j << ": Tag=0x" << std::hex << line.getTag() 
                          << ", State=" << stateToString(line.getState()) 
                          << ", LRU=" << std::dec << set.getLRUValue(j) << std::endl;
            }
        }
    }
    
    std::cout << "  Statistics:" << std::endl;
    std::cout << "    Accesses: " << stats.getAccesses() << std::endl;
    std::cout << "    Misses: " << stats.getMisses() << std::endl;
    std::cout << "    Miss Rate: " << std::fixed << std::setprecision(2) 
              << (stats.getAccesses() > 0 ? 100.0 * stats.getMisses() / stats.getAccesses() : 0.0) 
              << "%" << std::endl;
    std::cout << "    Evictions: " << stats.getEvictions() << std::endl;
    std::cout << "    Writebacks: " << stats.getWritebacks() << std::endl;
}

std::string Cache::getCacheLineState(unsigned int address) const {
    unsigned int tag = getTag(address);
    unsigned int setIndex = getSetIndex(address);
    
    const CacheSet& set = sets[setIndex];
    int lineIndex = set.findLine(tag);
    
    if (lineIndex == -1) {
        return "INVALID";
    }
    
    const CacheLine& line = set.getLine(lineIndex);
    return stateToString(line.getState());
}
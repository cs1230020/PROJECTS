#ifndef CACHE_H
#define CACHE_H

#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include "CacheSet.h"
#include "Bus.h"
#include "Statistics.h"

class Bus; // Forward declaration

class Cache {
private:
    int coreId;                     // ID of the processor core this cache belongs to
    int numSets;                    // Number of sets in the cache (2^s)
    int associativity;              // Number of lines per set (E)
    int blockSize;                  // Size of each block in bytes (2^b)
    int blockOffsetBits;            // Number of bits for block offset (b)
    int setIndexBits;               // Number of bits for set index (s)
    int tagBits;                    // Number of bits for tag
    
    std::vector<CacheSet> sets;     // Array of cache sets
    Bus* bus;                       // Pointer to the shared bus
    Statistics stats;               // Statistics for this cache
    
    bool isBlocked;                 // Flag to indicate if cache is blocked waiting for a miss
    int blockedCycles;              // Number of cycles the cache has been blocked
    unsigned int blockedUntilCycle = 0;
    
    // Helper methods for address manipulation
    unsigned int getTag(unsigned int address) const;
    unsigned int getSetIndex(unsigned int address) const;
    unsigned int getBlockOffset(unsigned int address) const;
    
    // Internal cache operations
    bool lookupAndUpdate(unsigned int address, bool isWrite, int& cycles);
    void allocateLine(unsigned int address, bool isWrite, int& cycles,  bool busresponse);
    void evictLine(CacheLine& line, unsigned int address, int& cycles);
    
    // MESI protocol state transitions
    void handleBusRead(unsigned int address, bool& providedData, int& cycles);
    void handleBusReadX(unsigned int address, bool& providedData, int& cycles);
    void handleBusUpgrade(unsigned int address, int& cycles);
    std::vector<Cache*> caches;
    
    // Get line index in a set
    int getLineIndex(unsigned int address) const;
    
public:
    Cache(int coreId, int setIndexBits, int associativity, int blockOffsetBits, Bus* bus);
    ~Cache();
    
    // Cache operations
    bool read(unsigned int address, int& cycles);
    bool write(unsigned int address, int& cycles);
    
    // Bus snooping operations
    bool snoop(BusOperation op, unsigned int address, int sourceId, bool& providedData, int& cycles);
    
    // Utility methods
    bool isHit(unsigned int address) const;
    bool isBlocking() const;
    void unblock();
    int getBlockedCycles() const;
    
    // Statistics methods
    const Statistics& getStatistics() const;
    Statistics& getStatistics();
    void resetStatistics();
    void processCycle();
    // Debug methods
    void printState() const;
    std::string getCacheLineState(unsigned int address) const;
    void setCaches(const std::vector<Cache*>& otherCaches);
    
    // Friend declaration for Bus to access private members
    friend class Bus;
};

#endif // CACHE_H